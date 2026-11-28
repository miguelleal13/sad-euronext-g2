"""Leitura segura do precos.csv do AnyLogic, usada por kpis_choque.py e verificacao_minuto.py.

Quando o AnyLogic corre várias réplicas ao mesmo tempo (vários núcleos), todas escrevem no mesmo
ficheiro: as linhas de corridas diferentes ficam misturadas e, de vez em quando, duas linhas ficam
coladas (uma linha com 13 campos em vez de 7). Este módulo:
  0. verifica primeiro (sem escrever nada) se o ficheiro está limpo e com as corridas seguidas: se estiver, lê-o
     aos bocados e entrega cada corrida diretamente, sem ficheiros temporários (para ficheiros de vários GB);
  1. senão, lê o ficheiro linha a linha e separa as linhas por corrida em ficheiros
     temporários, por isso não importa se as corridas estão seguidas ou misturadas;
  2. ignora as linhas estragadas (número de campos errado ou números que não se leem) e conta-as;
  3. ignora as "corridas" falsas feitas de bocados de linhas (menos de 90% das linhas da maior corrida);
  4. SÓ SE O FICHEIRO VIER ESTRAGADO: retira preços de um só minuto que saltam mais de 3% e voltam logo, que podem
     vir de linhas coladas. Num ficheiro limpo nada é retirado, porque esses saltos são do próprio modelo;
  5. devolve cada corrida ordenada pelo tempo, sem minutos repetidos, e diz quanto perdeu.
"""
import shutil
from collections import Counter
import tempfile
from pathlib import Path

import pandas as pd

COLS = ["label", "run", "time", "price", "bid", "ask", "volume"]
MIN_SHARE = 0.9      # uma corrida verdadeira tem pelo menos 90% das linhas da maior
SPIKE = 0.03         # pico: salta mais de 3% e volta no minuto seguinte para onde estava (dentro de 1%)


def _drop_spikes(g):
    """Retira preços de um só minuto que saltam e voltam logo (vêm de linhas coladas de outra corrida).
    Um choque verdadeiro não volta para trás no minuto seguinte, por isso não é afetado."""
    import numpy as np
    total = 0
    for _ in range(3):
        lp = np.log(g["price"].to_numpy())
        if len(lp) < 3:
            break
        up = lp[1:-1] - lp[:-2]
        down = lp[2:] - lp[1:-1]
        back = np.abs(lp[2:] - lp[:-2])
        bad = (np.abs(up) > SPIKE) & (np.abs(down) > SPIKE) & (np.sign(up) != np.sign(down)) & (back < 0.01)
        idx = np.flatnonzero(bad) + 1
        if not len(idx):
            break
        total += len(idx)
        g = g.drop(g.index[idx]).reset_index(drop=True)
    return g, total


def _ok(parts):
    if len(parts) != 7 or not parts[0] or not parts[1]:
        return False
    try:
        t, p = float(parts[2]), float(parts[3])
        float(parts[4]); float(parts[5]); float(parts[6])
    except ValueError:
        return False
    return t > 0 and p > 0


def _scan(path):
    """1.ª passagem, rápida e sem escrever nada: conta linhas estragadas e vê se as corridas estão seguidas."""
    n = bad = 0
    seen, last, contiguous = set(), None, True
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            n += 1
            parts = line.split(";", 2)
            if len(parts) < 3 or line.count(";") != 6:
                bad += 1
                continue
            run = parts[1]
            if run != last:
                if run in seen:
                    contiguous = False
                    break
                seen.add(run)
                last = run
            if n % 10_000_000 == 0:
                print(f"  a verificar: {n:,} linhas", flush=True)
    return contiguous and bad == 0, n


def _stream(path, label_filter):
    """Ficheiro limpo e com as corridas seguidas: lê aos bocados e entrega cada corrida quando acaba (sem disco)."""
    carry, total, nruns = None, 0, 0
    for chunk in pd.read_csv(path, sep=";", names=COLS, dtype={"label": str, "run": str}, chunksize=2_000_000):
        total += len(chunk)
        if carry is not None:
            chunk = pd.concat([carry, chunk])
        last = chunk["run"].iloc[-1]
        done, carry = chunk[chunk["run"] != last], chunk[chunk["run"] == last]
        for run, g in done.groupby("run", sort=False):
            if label_filter and label_filter not in g["label"].iloc[0]:
                continue
            nruns += 1
            yield g["label"].iloc[0], run, g.sort_values("time").drop_duplicates("time", keep="last").reset_index(drop=True)
        print(f"  {total:,} linhas lidas, {nruns} corridas", flush=True)
    if carry is not None and len(carry):
        for run, g in carry.groupby("run", sort=False):
            if label_filter and label_filter not in g["label"].iloc[0]:
                continue
            nruns += 1
            yield g["label"].iloc[0], run, g.sort_values("time").drop_duplicates("time", keep="last").reset_index(drop=True)
    print(f"  ficheiro limpo e com as corridas seguidas: {nruns} corridas lidas diretamente; nenhum preço é retirado",
          flush=True)


def runs(path, label_filter=""):
    """Gera (label, run, DataFrame ordenado pelo tempo) para cada corrida do precos.csv."""
    clean, n = _scan(path)
    if clean:
        yield from _stream(path, label_filter)
        return
    print("  ficheiro com linhas estragadas ou corridas misturadas: separar por corrida (usa disco temporário)",
          flush=True)
    tmp = Path(tempfile.mkdtemp(prefix="precos_"))
    buf, files, labels = {}, {}, {}
    n = bad = switches = 0
    last = None
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                n += 1
                parts = line.rstrip("\r\n").split(";")
                if not _ok(parts):
                    bad += 1
                    continue
                if label_filter and label_filter not in parts[0]:
                    continue
                run = parts[1]
                if run != last:
                    switches += 1
                    last = run
                labels.setdefault(run, Counter())[parts[0]] += 1
                buf.setdefault(run, []).append(line if line.endswith("\n") else line + "\n")
                if len(buf[run]) >= 50_000:
                    files.setdefault(run, tmp / f"{len(files)}.csv")
                    with open(files[run], "a", encoding="utf-8") as o:
                        o.writelines(buf[run])
                    buf[run] = []
                if n % 2_000_000 == 0:
                    print(f"  {n:,} linhas lidas", flush=True)
        for run, lines in buf.items():
            if lines:
                files.setdefault(run, tmp / f"{len(files)}.csv")
                with open(files[run], "a", encoding="utf-8") as o:
                    o.writelines(lines)
        mixed = switches > len(files)
        print(f"  {n:,} linhas; {bad} estragadas e ignoradas"
              + ("; corridas MISTURADAS no ficheiro (réplicas em paralelo)" if mixed else ""), flush=True)
        # corridas verdadeiras têm quase todas as linhas; bocados de linhas coladas criam "corridas" falsas pequenas
        counts = {}
        for run, fp in files.items():
            with open(fp, "r", encoding="utf-8") as fh:
                counts[run] = sum(1 for _ in fh)
        top = max(counts.values()) if counts else 0
        real = [r for r in files if counts[r] >= MIN_SHARE * top]
        fake = len(files) - len(real)
        rc = [counts[r] for r in real]
        print(f"  {len(real)} corridas verdadeiras; {fake} bocados de linhas coladas ignorados"
              + (f"; linhas por corrida: {min(rc):,} a {max(rc):,}" if real else ""), flush=True)
        labels = {r: c.most_common(1)[0][0] for r, c in labels.items()}   # o label verdadeiro é o mais frequente
        damaged = bad > 0 or mixed or fake > 0
        if not damaged:
            print("  ficheiro limpo: nenhum preço é retirado (os saltos de um minuto são do próprio modelo)", flush=True)
        spikes_total = 0
        for run in real:
            g = pd.read_csv(files[run], sep=";", names=COLS, dtype={"label": str, "run": str})
            g = g[g["label"] == labels[run]]
            g = g.sort_values("time", kind="stable").drop_duplicates("time", keep="last").reset_index(drop=True)
            if damaged:
                g, k = _drop_spikes(g)
                spikes_total += k
            yield labels[run], run, g
        if damaged:
            print(f"  ficheiro estragado: {spikes_total} picos de um minuto retirados (podem incluir alguns do próprio modelo)",
                  flush=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
