"""Descarrega os preços diários do BCP (BCP.LS) desde 2010 para data/raw/."""
from pathlib import Path

import yfinance as yf

TICKER = "BCP.LS"
START = "2010-01-01"
OUT = Path(__file__).resolve().parent.parent / "data" / "raw" / "bcp_daily.csv"


def main():
    df = yf.download(TICKER, start=START, interval="1d", auto_adjust=False, progress=False)
    if df.empty:
        raise SystemExit("Sem dados: verifica a ligação à internet ou o ticker.")
    if hasattr(df.columns, "levels"):  # o yfinance pode devolver colunas MultiIndex
        df.columns = df.columns.get_level_values(0)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT)
    print(f"{len(df)} dias guardados em {OUT} ({df.index.min().date()} a {df.index.max().date()})")


if __name__ == "__main__":
    main()
