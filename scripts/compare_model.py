"""Calibração: compara as estatísticas do modelo com as do BCP real.

Uso (depois de correr o cenário baseline no AnyLogic):
    python scripts/compare_model.py              # usa todas as corridas com label a começar por "baseline"
    python scripts/compare_model.py baseline_c2  # filtra por outro início de label
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from target_stats import compute, stats_from_returns

ROOT = Path(__file__).resolve().parent.parent
PRICES = ROOT / "model" / "output" / "precos.csv"
OUT_DIR = ROOT / "data" / "processed"
DAY = 510          # minutos por dia de negociação no modelo
TOL = 0.25         # "bate" se o modelo estiver a ±25% do valor real

COLS = ["label", "run", "time", "price", "bid", "ask", "volume"]
CHECK = ["volatilidade_diaria", "curtose_excesso", "pct_dias_var_maior_3pct", "autocorr_abs_retornos_lag1"]


def model_stats(prefix):
    df = pd.read_csv(PRICES, sep=";", names=COLS)
    df = df[df["label"].astype(str).str.startswith(prefix)]
    if df.empty:
        raise SystemExit(f"Não há corridas com label a começar por '{prefix}' em {PRICES}")
    runs = []
    for _, g in df.groupby("run"):
        close = g.assign(day=(g["time"] // DAY).astype(int)).groupby("day")["price"].last()
        runs.append(stats_from_returns(np.log(close).diff()))
    return pd.DataFrame(runs).mean(), len(runs)


def main():
    prefix = sys.argv[1] if len(sys.argv) > 1 else "baseline"
    real = compute("2023-01-01", "2024-12-31")
    model, n = model_stats(prefix)

    rows = []
    for k in CHECK:
        r, m = real[k], model[k]
        ok = abs(m - r) <= TOL * abs(r) if r != 0 else abs(m) < 0.01
        rows.append({"estatistica": k, "BCP real": r, "modelo": m, "bate": "sim" if ok else "NAO"})
    table = pd.DataFrame(rows)
    print(f"Modelo: {n} corridas com label '{prefix}*'\n")
    print(table.to_string(index=False, float_format=lambda x: f"{x:.4f}"))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"calibracao_{prefix}.xlsx"
    table.to_excel(out, index=False)
    print(f"\nGuardado em {out}")


if __name__ == "__main__":
    main()
