"""Junta as metas dos três períodos num Excel (data/processed/metas.xlsx).

Uso:
    python scripts/make_metas.py
"""
import pandas as pd

from target_stats import RAW, OUT_DIR, compute

# BES começa a 15/07/2014 para excluir o aumento de capital do BCP
# (fim de junho/início de julho de 2014), que aparece nos dados do Yahoo como subidas falsas de +12% e +24%.
PERIODOS = {
    "Calmo 2023-24": ("2023-01-01", "2024-12-31"),
    "BES 2014": ("2014-07-15", "2014-09-30"),
    "COVID 2020": ("2020-02-15", "2020-04-30"),
}


def queda_maxima(start, end):
    """Maior queda do pico ao mínimo dentro do período (0.25 = -25%)."""
    df = pd.read_csv(RAW, index_col=0, parse_dates=True)
    px = df.loc[start:end, "Adj Close" if "Adj Close" in df.columns else "Close"].dropna()
    return (1 - px / px.cummax()).max()


def main():
    if not RAW.exists():
        raise SystemExit("Falta data/raw/bcp_daily.csv: corre primeiro download_daily.py")
    colunas = {}
    for nome, (start, end) in PERIODOS.items():
        s = compute(start, end)
        s.pop("periodo")
        s["queda_maxima"] = queda_maxima(start, end)
        colunas[nome] = s
    metas = pd.DataFrame(colunas)
    print(metas.round(4).to_string())
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / "metas.xlsx"
    metas.to_excel(out)
    print(f"\nGuardado em {out}")


if __name__ == "__main__":
    main()