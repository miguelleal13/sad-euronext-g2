"""Guarda os dados de 1 minuto do BCP. O Yahoo só disponibiliza cerca de 7 dias,
por isso este script deve ser corrido 2 vezes por semana até dezembro.

Cada corrida junta os dados novos a data/raw/bcp_1min.csv, sem duplicados.
"""
from pathlib import Path

import pandas as pd
import yfinance as yf

TICKER = "BCP.LS"
OUT = Path(__file__).resolve().parent.parent / "data" / "raw" / "bcp_1min.csv"


def main():
    new = yf.download(TICKER, period="7d", interval="1m", auto_adjust=False, progress=False)
    if new.empty:
        raise SystemExit("Sem dados intradiários devolvidos pelo Yahoo.")
    if hasattr(new.columns, "levels"):
        new.columns = new.columns.get_level_values(0)
    new.index = pd.to_datetime(new.index, utc=True)

    if OUT.exists():
        old = pd.read_csv(OUT, index_col=0)
        old.index = pd.to_datetime(old.index, utc=True)
        df = pd.concat([old, new])
        df = df[~df.index.duplicated(keep="last")].sort_index()
    else:
        df = new

    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT)
    print(f"{len(new)} linhas novas; total {len(df)} ({df.index.min()} a {df.index.max()})")


if __name__ == "__main__":
    main()
