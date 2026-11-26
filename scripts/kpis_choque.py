"""KPIs do choque por corrida (Base, Cenários 2, 3, 4, Limiares e sensibilidade).

Os indicadores estão fixados em docs/KPIS_CENARIOS.md ANTES das corridas.
Lê o precos.csv com scripts/ler_precos.py: aguenta vários GB, corridas misturadas (réplicas em paralelo)
e linhas estragadas (ignoradas e contadas).

Escreve data/processed/kpis_choque_<nome da pasta>.xlsx com 2 folhas:
  runs   - uma linha por corrida, com todos os indicadores (ver KPIS abaixo)
  resumo - por cenário (label): média e intervalo de confiança de 95% (t-Student) de cada indicador,
           probabilidade de crash com intervalo de Wilson a 95%, e nº de corridas

Uso: python scripts/kpis_choque.py PASTA                       (choque a 30600 min = dia 60; limiar de crash -15%)
     python scripts/kpis_choque.py PASTA 30600 -0.16 -0.14     (instante do choque, limiar principal e alternativo)
Os limiares de crash saem de scripts/limiar_crash.py (dados do BCP): o principal (percentil 99) e o
alternativo (percentil 95), para mostrar que a conclusão não depende do limiar.
"""
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

import ler_precos

ROOT = Path(__file__).resolve().parent.parent
DIR = Path(sys.argv[1])
T0 = float(sys.argv[2]) if len(sys.argv) > 2 else 30600.0
CRASH = float(sys.argv[3]) if len(sys.argv) > 3 else -0.15
CRASH_ALT = float(sys.argv[4]) if len(sys.argv) > 4 else None
DAY = 510
RESULT = ROOT / "data" / "processed" / f"kpis_choque_{DIR.name}.xlsx"
KPIS = [
    # estabilidade
    "queda_max_dia", "queda_a_mais", "crash", "crash_alt", "queda_30min", "ret_fecho", "ret_5d", "recupera_meia_min",
    "vol_diaria",
    # liquidez
    "spread_dia_choque", "spread_5d", "spread_medio", "volume_dia_choque", "volume_5d", "volume_total",
    "min_reserva_dia_choque", "n_reservas_dia_choque", "n_reservas", "pct_tempo_reserva",
]


def overlap(a, b, lo, hi):
    """Minutos de reserva [a, b] dentro da janela [lo, hi]."""
    return max(0.0, min(b, hi) - max(a, lo))


def run_kpis(g, halts_run):
    t, p = g["time"].to_numpy(), g["price"].to_numpy()
    cumvol = g["volume"].to_numpy()                       # volume acumulado da corrida
    p0 = p[t <= T0][-1]
    v0 = cumvol[t <= T0][-1]
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
    rel = (g["ask"] - g["bid"]) / ((g["ask"] + g["bid"]) / 2)
    ok = ~in_halt

    def spread(mask):
        m = ok & mask
        return rel[m].mean() if m.any() else np.nan

    hs = list(zip(halts_run["start"], halts_run["end"]))
    dur = sum(b - a for a, b in hs)
    queda = p[i_min] / p0 - 1
    return {
        "queda_max_dia": queda,
        "queda_a_mais": queda - (-0.10),                   # negativo = caiu mais do que a notícia
        "crash": float(queda < CRASH),
        "crash_alt": float(queda < CRASH_ALT) if CRASH_ALT is not None else np.nan,
        "queda_30min": p[(t > T0) & (t <= T0 + 30)].min() / p0 - 1,
        "ret_fecho": p[t <= T0 + DAY][-1] / p0 - 1,
        "ret_5d": p[w5][-1] / p0 - 1,
        "recupera_meia_min": t[after[0]] - t[i_min] if len(after) else np.nan,
        "vol_diaria": np.log(closes).diff().std(),
        "spread_dia_choque": spread(day),
        "spread_5d": spread((t > T0 + DAY) & (t <= T0 + 6 * DAY)),   # os 5 dias seguintes ao dia do choque
        "spread_medio": spread(np.ones(len(t), dtype=bool)),
        "volume_dia_choque": cumvol[t <= T0 + DAY][-1] - v0,
        "volume_5d": cumvol[t <= T0 + 6 * DAY][-1] - cumvol[t <= T0 + DAY][-1],
        "volume_total": cumvol[-1],
        "min_reserva_dia_choque": sum(overlap(a, b, T0, T0 + DAY) for a, b in hs),
        "n_reservas_dia_choque": sum(1 for a, b in hs if b > T0 and a <= T0 + DAY),
        "n_reservas": len(hs),
        "pct_tempo_reserva": dur / t[-1],
    }


def wilson(k, n, z=1.96):
    if n == 0:
        return np.nan, np.nan
    ph = k / n
    c = (ph + z * z / (2 * n)) / (1 + z * z / n)
    h = z * np.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return max(0.0, c - h), min(1.0, c + h)


def main():
    hfile = DIR / "halts.csv"
    h = (pd.read_csv(hfile, sep=";", names=["label", "run", "start", "end", "pre", "auc"],
                     dtype={"label": str, "run": str})
         if hfile.exists() and hfile.stat().st_size > 0 else pd.DataFrame(columns=["label", "run", "start", "end"]))
    halts_by_run = dict(tuple(h.groupby("run")))
    empty = h.iloc[0:0]
    rows = []
    for label, run, g in ler_precos.runs(DIR / "precos.csv"):
        if g["time"].min() > T0 or g["time"].max() < T0 + 6 * DAY:
            print(f"  AVISO: corrida {run} ({label}) incompleta ({len(g)} minutos); fica de fora")
            continue
        try:
            rows.append({"label": label, "run": run, **run_kpis(g, halts_by_run.get(run, empty))})
        except ValueError as e:
            print(f"  AVISO: corrida {run} ({label}) sem dados suficientes à volta do choque ({e}); fica de fora")

    runs = pd.DataFrame(rows)
    # fatores lidos do label, quando existem (ex.: shock_c2_h5_n13); labels de outro formato ficam vazios
    for col, pat in [("colares", r"_c(\d+)"), ("reserva_min", r"_h([\d.]+)"), ("n_chartists", r"_n(\d+)")]:
        runs.insert(1, col, pd.to_numeric(runs["label"].str.extract(pat)[0], errors="coerce"))

    def ci(x):
        x = x.dropna()
        return stats.t.ppf(0.975, len(x) - 1) * x.std() / np.sqrt(len(x)) if len(x) > 1 else np.nan

    g = runs.groupby("label")[KPIS]
    res = g.mean().join(g.agg(ci).add_suffix("_ic95")).join(g.size().rename("n_corridas"))
    for col, name in [("crash", "prob_crash"), ("crash_alt", "prob_crash_alt")]:
        k = runs.groupby("label")[col].sum()
        res[name] = res[col]
        res[name + "_ic_inf"] = [wilson(k[l], res.loc[l, "n_corridas"])[0] for l in res.index]
        res[name + "_ic_sup"] = [wilson(k[l], res.loc[l, "n_corridas"])[1] for l in res.index]
        if CRASH_ALT is None and col == "crash_alt":
            res[[name, name + "_ic_inf", name + "_ic_sup"]] = np.nan
    res = res.drop(columns=["crash", "crash_ic95", "crash_alt", "crash_alt_ic95"]).reset_index()
    fac = runs.groupby("label")[["colares", "reserva_min", "n_chartists"]].first().reset_index()
    res = fac.merge(res, on="label").sort_values(["n_chartists", "reserva_min", "colares", "label"])
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(RESULT) as xw:
        runs.to_excel(xw, sheet_name="runs", index=False)
        res.to_excel(xw, sheet_name="resumo", index=False)
        pd.DataFrame([("instante do choque (min)", T0), ("limiar de crash (principal)", CRASH),
                      ("limiar de crash (robustez)", CRASH_ALT)],
                     columns=["parâmetro", "valor"]).to_excel(xw, sheet_name="parametros", index=False)
    show = ["label", "n_corridas", "queda_max_dia", "prob_crash", "prob_crash_alt", "ret_fecho", "recupera_meia_min",
            "spread_dia_choque", "volume_dia_choque", "min_reserva_dia_choque"]
    pd.set_option("display.width", 220)
    print(res[show].to_string(index=False, float_format=lambda x: f"{x:.4f}"))
    alt = f"; robustez {CRASH_ALT:.2%}" if CRASH_ALT is not None else ""
    print(f"\nLimiar de crash: principal {CRASH:.2%}{alt}.  Guardado em {RESULT}")


if __name__ == "__main__":
    main()
