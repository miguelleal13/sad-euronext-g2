"""Critério baseado nos dados para "o modelo bate com o BCP": intervalos de bootstrap a 95% dos 7 factos.

Em vez de tolerâncias escolhidas por nós (ex.: volatilidade a +-25%), pergunta-se: que valores podia o próprio BCP
ter dado, só por acaso, num período com o mesmo número de dias? Reamostram-se os dias reais em blocos de 10 dias
seguidos (para manter o clustering e a persistência do volume), 3000 vezes, e calculam-se os 7 factos em cada
reamostragem. O intervalo entre os percentis 2.5% e 97.5% é a margem de acaso. Um valor do modelo dentro desse
intervalo não se distingue estatisticamente do BCP.

Uso: python scripts/intervalos_factos.py                          (2023-2024, treino)
     python scripts/intervalos_factos.py 2025-01-01 2026-12-31    (outro período)
Escreve data/processed/intervalos_factos_<início>_<fim>.xlsx
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
BLOCK, REPS = 10, 3000


def facts(r, v):
    r, v = pd.Series(r), pd.Series(v)
    return {"volatilidade_diaria": r.std(), "curtose_excesso": stats.kurtosis(r),
            "autocorr_abs_retornos_lag1": r.abs().autocorr(), "autocorr_retornos_lag1": r.autocorr(),
            "pct_dias_var_maior_3pct": (r.abs() > 0.03).mean(), "corr_volume_absret": v.corr(r.abs()),
            "autocorr_volume_lag1": v.autocorr()}


def main():
    start, end = (sys.argv[1], sys.argv[2]) if len(sys.argv) > 2 else ("2023-01-01", "2024-12-31")
    d = pd.read_csv(ROOT / "data" / "raw" / "bcp_daily.csv", index_col=0, parse_dates=True).loc[start:end].copy()
    d["r"] = np.log(d["Adj Close"]).diff()
    d = d.dropna(subset=["r"])
    r, v, n = d["r"].to_numpy(), d["Volume"].to_numpy(float), len(d)
    rng = np.random.default_rng(0)
    boot = []
    for _ in range(REPS):
        idx = np.concatenate([np.arange(s, s + BLOCK) for s in rng.integers(0, n - BLOCK, n // BLOCK + 1)])[:n]
        boot.append(facts(r[idx], v[idx]))
    b = pd.DataFrame(boot)
    t = pd.DataFrame({"BCP": pd.Series(facts(r, v)), "limite inferior (2.5%)": b.quantile(0.025),
                      "limite superior (97.5%)": b.quantile(0.975)})
    print(f"BCP {start} a {end} ({n} dias), bootstrap em blocos de {BLOCK} dias, {REPS} reamostragens\n")
    print(t.to_string(float_format=lambda x: f"{x:.4f}"))
    out = ROOT / "data" / "processed" / f"intervalos_factos_{start[:4]}_{end[:4]}.xlsx"
    t.to_excel(out)
    print(f"\nGuardado em {out}")


if __name__ == "__main__":
    main()
