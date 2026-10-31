"""Calibração: compara o modelo com os factos estilizados do BCP real (docs/FACTOS_ESTILIZADOS.md).

Uso (depois de correr o cenário baseline no AnyLogic):
    python scripts/compare_model.py              # usa todas as corridas com label a começar por "baseline"
    python scripts/compare_model.py baseline_c2  # filtra por outro início de label
    python scripts/compare_model.py baseline C:/caminho/para/a/pasta   # lê o precos.csv dessa pasta
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from target_stats import compute, stats_from_returns

ROOT = Path(__file__).resolve().parent.parent
PRICES = ROOT / "model" / "Euronext_Main" / "output" / "precos.csv"
OUT_DIR = ROOT / "data" / "processed"
DAY = 510          # minutos por dia de negociação no modelo

COLS = ["label", "run", "time", "price", "bid", "ask", "volume"]

# Os mesmos critérios de "bate" de docs/FACTOS_ESTILIZADOS.md: (métrica, função(real, modelo) -> bool)
FACTS = [
    ("volatilidade_diaria", lambda r, m: abs(m - r) <= 0.25 * abs(r)),
    ("curtose_excesso", lambda r, m: m > 1 and abs(m - r) <= 0.5 * abs(r)),
    ("autocorr_abs_retornos_lag1", lambda r, m: m > 0.05 and np.sign(m) == np.sign(r)),
    ("autocorr_retornos_lag1", lambda r, m: -0.1 <= m <= 0.1),
    ("pct_dias_var_maior_3pct", lambda r, m: abs(m - r) <= 0.5 * abs(r)),
    ("corr_volume_absret", lambda r, m: m > 0),
]


def model_stats(prefix, prices):
    # run como texto: um id só com dígitos não pode virar número e partir a corrida em duas
    df = pd.read_csv(prices, sep=";", names=COLS, dtype={"label": str, "run": str})
    df = df[df["label"].str.startswith(prefix)]
    if df.empty:
        raise SystemExit(f"Não há corridas com label a começar por '{prefix}' em {prices}")
    runs = []
    for _, g in df.groupby("run"):
        # minutos 1..510 = dia 0, 511..1020 = dia 1, ... (o minuto 510 fecha o dia)
        daily = g.assign(day=((g["time"] - 1) // DAY).astype(int)).groupby("day").agg(price=("price", "last"),
                                                                               cumvol=("volume", "last"))
        vol = daily["cumvol"].diff()                      # o modelo grava o volume acumulado
        if (vol < 0).any():
            print(f"AVISO: corrida {g['run'].iloc[0]} com volume diário negativo (o volume int do Stock transbordou)")
        runs.append(stats_from_returns(np.log(daily["price"]).diff(), vol))
    runs = pd.DataFrame(runs)
    return runs.mean(), runs.median(), len(runs)


def main():
    prefix = sys.argv[1] if len(sys.argv) > 1 else "baseline"
    prices = Path(sys.argv[2]) / "precos.csv" if len(sys.argv) > 2 else PRICES
    real = compute("2023-01-01", "2024-12-31")
    model, median, n = model_stats(prefix, prices)

    # o critério usa a média das corridas (docs/FACTOS_ESTILIZADOS.md); a mediana mostra se a média vem de 1-2 corridas extremas
    rows = [{"facto": k, "BCP real": real[k], "modelo": model[k], "mediana": median[k],
             "bate": "sim" if ok(real[k], model[k]) else "NAO"} for k, ok in FACTS]
    table = pd.DataFrame(rows)
    print(f"Modelo: {n} corridas com label '{prefix}*'\n")
    print(table.to_string(index=False, float_format=lambda x: f"{x:.4f}"))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"calibracao_{prefix}.xlsx"
    table.to_excel(out, index=False)
    print(f"\nGuardado em {out}")


if __name__ == "__main__":
    main()
