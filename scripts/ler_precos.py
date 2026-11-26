"""Leitura segura do precos.csv do AnyLogic, usada por kpis_choque.py e verificacao_minuto.py.

Quando o AnyLogic corre várias réplicas ao mesmo tempo (vários núcleos), todas escrevem no mesmo
ficheiro: as linhas de corridas diferentes ficam misturadas e, de vez em quando, duas linhas ficam
coladas (uma linha com 13 campos em vez de 7). Este módulo:
  1. lê o ficheiro linha a linha (aguenta vários GB) e separa as linhas por corrida em ficheiros
     temporários, por isso não importa se as corridas estão seguidas ou misturadas;
  2. ignora as linhas estragadas (número de campos errado ou números que não se leem) e conta-as;
  3. devolve cada corrida ordenada pelo tempo, sem minutos repetidos.
"""
import shutil
import tempfile
from pathlib import Path

import pandas as pd

COLS = ["label", "run", "time", "price", "bid", "ask", "volume"]


def _ok(parts):
    if len(parts) != 7 or not parts[0] or not parts[1]:
        return False
    try:
        t, p = float(parts[2]), float(parts[3])
        float(parts[4]); float(parts[5]); float(parts[6])
    except ValueError:
        return False
    return t > 0 and p > 0


def runs(path, label_filter=""):
    """Gera (label, run, DataFrame ordenado pelo tempo) para cada corrida do precos.csv."""
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
                labels.setdefault(run, parts[0])
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
        print(f"  {n:,} linhas; {bad} estragadas e ignoradas; {len(files)} corridas"
              + ("; corridas MISTURADAS no ficheiro (réplicas em paralelo), separadas pelo script" if mixed else ""),
              flush=True)
        for run, fp in files.items():
            g = pd.read_csv(fp, sep=";", names=COLS, dtype={"label": str, "run": str})
            g = g.sort_values("time", kind="stable").drop_duplicates("time", keep="last").reset_index(drop=True)
            yield labels[run], run, g
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
