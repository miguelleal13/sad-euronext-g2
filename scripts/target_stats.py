"""Calcula as estatísticas reais do BCP que o modelo tem de reproduzir.

Uso:
    python scripts/target_stats.py                       # período calmo 2023–2024
    python scripts/target_stats.py 2014-06-01 2014-09-30  # ex.: caso BES
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "bcp_daily.csv"
OUT_DIR = ROOT / "data" / "processed"


def compute(start, end):
    df = pd.read_csv(RAW, index_col=0, parse_dates=True)
    px = df.loc[start:end, "Adj Close" if "Adj Close" in df.columns else "Close"].dropna()
    return {"periodo": f"{start} a {end}", **stats_from_returns(np.log(px).diff())}


def stats_from_returns(r):
    """Estatísticas de uma série de retornos diários (logarítmicos)."""
    r = pd.Series(r).dropna()
    return {
        "n_dias": len(r),
        "volatilidade_diaria": r.std(),
        "volatilidade_anual": r.std() * np.sqrt(252),
        "curtose_excesso": stats.kurtosis(r),  # 0 = normal; > 0 = caudas pesadas
        "assimetria": stats.skew(r),
        "pct_dias_var_maior_3pct": (r.abs() > 0.03).mean(),
        "autocorr_retornos_lag1": r.autocorr(1),
        "autocorr_abs_retornos_lag1": r.abs().autocorr(1),  # clustering de volatilidade
        "pior_dia": r.min(),
        "melhor_dia": r.max(),
    }


def main():
    start, end = (sys.argv[1], sys.argv[2]) if len(sys.argv) == 3 else ("2023-01-01", "2024-12-31")
    if not RAW.exists():
        raise SystemExit("Falta data/raw/bcp_daily.csv: corre primeiro download_daily.py")
    s = compute(start, end)
    for k, v in s.items():
        print(f"{k:32s} {v:.4f}" if isinstance(v, float) else f"{k:32s} {v}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"target_stats_{start}_{end}.xlsx"
    pd.DataFrame([s]).T.rename(columns={0: "BCP real"}).to_excel(out)
    print(f"\nGuardado em {out}")


if __name__ == "__main__":
    main()
