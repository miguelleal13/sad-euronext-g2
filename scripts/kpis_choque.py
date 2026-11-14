"""KPIs do choque por corrida, para ficheiros grandes (Cenários 2, 3 e 4).

Lê o precos.csv aos bocados (não carrega o ficheiro todo para a memória), por isso aguenta vários GB.
Cada corrida tem de estar seguida no ficheiro (é o que o AnyLogic grava).

Escreve data/processed/kpis_choque_<nome da pasta>.xlsx com 2 folhas:
  runs   - uma linha por corrida: queda máxima no dia do choque, queda nos primeiros 30 min, retorno no fecho
           do dia e a 5 dias, tempo até recuperar metade da queda, volatilidade diária da corrida, spread
           relativo médio fora das reservas, volume total, nº de reservas e % do tempo em reserva (corrida inteira)
  resumo - por cenário (label): média e intervalo de confiança de 95% (t-Student) de cada KPI,
           com as colunas colares (c), reserva curta (h) e nº de chartists (n) separadas

Uso: python scripts/kpis_choque.py PASTA            (pasta com precos.csv e halts.csv)
     python scripts/kpis_choque.py PASTA 30600      (instante do choque em minutos; por defeito 30600 = dia 60)
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
DIR = Path(sys.argv[1])
T0 = float(sys.argv[2]) if len(sys.argv) > 2 else 30600.0
DAY = 510
RESULT = ROOT / "data" / "processed" / f"kpis_choque_{DIR.name}.xlsx"   # um ficheiro por pasta (cenário)
COLS = ["label", "run", "time", "price", "bid", "ask", "volume"]
KPIS = ["queda_max_dia", "queda_30min", "ret_fecho", "ret_5d", "recupera_meia_min", "vol_diaria",
        "spread_medio", "volume_total", "n_reservas", "pct_tempo_reserva"]


def run_kpis(g, halts_run):
    t, p = g["time"].to_numpy(), g["price"].to_numpy()
    p0 = p[t <= T0][-1]
    day = (t > T0) & (t <= T0 + DAY)
    w5 = (t > T0) & (t <= T0 + 5 * DAY)
    i_min = np.flatnonzero(day)[np.argmin(p[day])]
    half = p0 - (p0 - p[i_min]) / 2
    after = np.flatnonzero(w5 & (t >= t[i_min]) & (p >= half))
    closes = g.assign(d=((g["time"] - 1) // DAY).astype(int)).groupby("d")["price"].last()
    # spread só fora das reservas: durante a reserva não há negociação e o livro fica cruzado (bid > ask)
    in_halt = np.zeros(len(t), dtype=bool)
    for a, b in zip(halts_run["start"], halts_run["end"]):
        in_halt |= (t >= a) & (t <= b)
    q = g[~in_halt]
    mid = (q["ask"] + q["bid"]) / 2
    dur = (halts_run["end"] - halts_run["start"]).sum() if len(halts_run) else 0.0
    return {
        "queda_max_dia": p[i_min] / p0 - 1,
        "queda_30min": p[(t > T0) & (t <= T0 + 30)].min() / p0 - 1,
        "ret_fecho": p[t <= T0 + DAY][-1] / p0 - 1,
        "ret_5d": p[w5][-1] / p0 - 1,
        "recupera_meia_min": t[after[0]] - t[i_min] if len(after) else np.nan,
        "vol_diaria": np.log(closes).diff().std(),
        "spread_medio": ((q["ask"] - q["bid"]) / mid).mean(),
        "volume_total": g["volume"].iloc[-1],
        "n_reservas": len(halts_run),
        "pct_tempo_reserva": dur / t[-1],
    }


def main():
    h = (pd.read_csv(DIR / "halts.csv", sep=";", names=["label", "run", "start", "end", "pre", "auc"],
                     dtype={"label": str, "run": str})
         if (DIR / "halts.csv").stat().st_size > 0 else pd.DataFrame(columns=["label", "run", "start", "end"]))
    halts_by_run = dict(tuple(h.groupby("run")))
    empty = h.iloc[0:0]
    rows, carry, n = [], None, 0
    for chunk in pd.read_csv(DIR / "precos.csv", sep=";", names=COLS, dtype={"label": str, "run": str},
                             chunksize=2_000_000):
        if carry is not None:
            chunk = pd.concat([carry, chunk])
        last_run = chunk["run"].iloc[-1]
        done, carry = chunk[chunk["run"] != last_run], chunk[chunk["run"] == last_run]
        for run, g in done.groupby("run", sort=False):
            rows.append({"label": g["label"].iloc[0], "run": run, **run_kpis(g, halts_by_run.get(run, empty))})
        n += len(chunk) - len(carry)
        print(f"  {n:,} linhas lidas, {len(rows)} corridas", flush=True)
    for run, g in carry.groupby("run", sort=False):
        rows.append({"label": g["label"].iloc[0], "run": run, **run_kpis(g, halts_by_run.get(run, empty))})

    runs = pd.DataFrame(rows)
    if runs["run"].duplicated().any():
        raise SystemExit("ERRO: há corridas partidas no ficheiro (não estão seguidas); os KPIs estariam errados")
    parts = runs["label"].str.extract(r"_c(\d+)_h([\d.]+)_n(\d+)")
    runs.insert(1, "colares", parts[0].astype(int))
    runs.insert(2, "reserva_min", parts[1].astype(float))
    runs.insert(3, "n_chartists", parts[2].astype(int))

    def ci(x):
        x = x.dropna()
        return stats.t.ppf(0.975, len(x) - 1) * x.std() / np.sqrt(len(x)) if len(x) > 1 else np.nan

    g = runs.groupby(["label", "colares", "reserva_min", "n_chartists"])[KPIS]
    res = g.mean().join(g.agg(ci).add_suffix("_ic95")).join(g.size().rename("n_corridas")).reset_index()
    res = res.sort_values(["n_chartists", "reserva_min", "colares"])
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(RESULT) as xw:
        runs.to_excel(xw, sheet_name="runs", index=False)
        res.to_excel(xw, sheet_name="resumo", index=False)
    show = ["label", "n_corridas", "queda_max_dia", "ret_fecho", "recupera_meia_min", "spread_medio",
            "n_reservas", "pct_tempo_reserva"]
    print(res[show].to_string(index=False, float_format=lambda x: f"{x:.4f}"))
    print(f"\nGuardado em {RESULT}")


if __name__ == "__main__":
    main()
