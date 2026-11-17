"""Separa a informação que move o BCP em canais, com os dados reais de 2023-2024.

Em vez de uma só fonte de "notícias", mede quanto da variância diária do BCP vem de:
  1. mercado/setor  - movimento dos bancos europeus (EURO STOXX Banks) e do PSI no mesmo dia
  2. resultados     - dias de apresentação de resultados trimestrais do BCP (dia seguinte incluído,
                      porque são divulgados depois do fecho)
  3. BCE            - dias de decisão de política monetária do BCE
  4. noite          - variação entre o fecho e a abertura seguinte (o modelo não tem noite)
  5. específico     - o que sobra: notícias próprias do BCP sem data marcada
Para cada canal dá a frequência, o tamanho típico de um choque e a parte da variância total.
No canal específico (e no de mercado) a frequência e o tamanho saem da curtose, como em
check_noticias.py: se os choques chegam como Poisson(lambda) com tamanho Normal(0, s),
curtose = 3 / lambda e desvio-padrão diário = s * raiz(lambda).

Uso: python scripts/decompor_noticias.py   (lê data/raw/bcp_daily.csv; descarrega os índices do Yahoo)
Escreve data/processed/canais_noticias.xlsx
"""
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "bcp_daily.csv"
OUT = ROOT / "data" / "processed" / "canais_noticias.xlsx"
START, END = "2023-01-01", "2024-12-31"
# índice do setor bancário europeu (tenta pela ordem até um funcionar) e índice PSI
SECTOR = ["^SX7E", "EXX1.DE", "SX7EEX.DE"]
PSI = ["PSI20.LS", "^PSI20"]
# datas de divulgação de resultados do BCP (site de investidores do Millennium bcp)
RESULTADOS = ["2023-02-27", "2023-05-15", "2023-07-27", "2023-10-30",
              "2024-02-26", "2024-05-15", "2024-07-31", "2024-10-30"]
# reuniões de política monetária do BCE com decisão de taxas
BCE = ["2023-02-02", "2023-03-16", "2023-05-04", "2023-06-15", "2023-07-27", "2023-09-14", "2023-10-26", "2023-12-14",
       "2024-01-25", "2024-03-07", "2024-04-11", "2024-06-06", "2024-07-18", "2024-09-12", "2024-10-17", "2024-12-12"]


def download(tickers):
    for t in tickers:
        try:
            d = yf.download(t, start="2022-12-01", end="2025-01-10", auto_adjust=False, progress=False)
        except Exception:
            continue
        if len(d):
            if hasattr(d.columns, "levels"):
                d.columns = d.columns.get_level_values(0)
            col = "Adj Close" if "Adj Close" in d else "Close"
            print(f"  índice {t}: {len(d)} dias")
            return np.log(d[col]).diff().rename(t)
    print(f"  AVISO: nenhum destes índices descarregou: {tickers}")
    return None


def poisson_from_kurt(x):
    k = x.kurt()
    lam = 3 / k if k > 0 else np.nan
    return lam, x.std() / np.sqrt(lam) if lam == lam else np.nan


def main():
    d = pd.read_csv(RAW, index_col=0, parse_dates=True)
    r = np.log(d["Adj Close"]).diff()
    night = np.log(d["Open"] / d["Close"].shift())
    df = pd.DataFrame({"r": r, "noite": night}).loc[START:END].dropna()
    total_var = df["r"].var()

    print("A descarregar índices...")
    fac = [s for s in (download(SECTOR), download(PSI)) if s is not None]
    rows = []

    # 1. mercado / setor: regressão do retorno do BCP nos índices
    resid = df["r"].copy()
    if fac:
        X = pd.concat(fac, axis=1).reindex(df.index).fillna(0.0)
        A = np.column_stack([np.ones(len(X)), X.to_numpy()])
        beta, *_ = np.linalg.lstsq(A, df["r"].to_numpy(), rcond=None)
        fitted = A @ beta
        resid = df["r"] - fitted
        mkt = pd.Series(fitted - beta[0], index=df.index)
        lam, s = poisson_from_kurt(mkt)
        rows.append({"canal": "mercado / setor (bancos europeus, PSI)", "frequência": f"{lam:.2f} por dia",
                     "tamanho do choque": s, "parte da variância": mkt.var() / total_var,
                     "nota": "betas: " + ", ".join(f"{c} {b:.2f}" for c, b in zip(X.columns, beta[1:]))})

    # 2. e 3. eventos marcados: variância a mais nesses dias, no resíduo (já sem o mercado)
    def event_days(dates, next_day):
        idx = set()
        for x in pd.to_datetime(dates):
            pos = df.index.searchsorted(x)
            for k in ([pos, pos + 1] if next_day else [pos]):
                if k < len(df):
                    idx.add(df.index[k])
        return sorted(idx)

    ev_res, ev_bce = event_days(RESULTADOS, True), event_days(BCE, False)
    normal = resid.drop(ev_res + ev_bce, errors="ignore")
    base = normal.var()
    for nome, days, n_ev in [("resultados do BCP", ev_res, len(RESULTADOS)), ("decisões do BCE", ev_bce, len(BCE))]:
        extra = max(0.0, (resid.loc[days] ** 2).sum() - len(days) * base)   # variância a mais nesses dias
        rows.append({"canal": nome, "frequência": f"{n_ev / 2:.0f} por ano (datas fixas)",
                     "tamanho do choque": np.sqrt(extra / n_ev), "parte da variância": extra / (total_var * len(df)),
                     "nota": f"|resíduo| médio nesses dias {resid.loc[days].abs().mean():.4f} contra {normal.abs().mean():.4f} nos outros"})

    # 4. noite (fecho -> abertura)
    rows.append({"canal": "noite (fecho -> abertura)", "frequência": "todos os dias",
                 "tamanho do choque": df["noite"].std(), "parte da variância": df["noite"].var() / total_var,
                 "nota": "no modelo entra como choque à abertura de cada dia"})

    # 5. específico do BCP, sem data marcada: o resíduo nos dias normais
    lam, s = poisson_from_kurt(normal)
    rows.append({"canal": "específico do BCP (sem data)", "frequência": f"{lam:.2f} por dia",
                 "tamanho do choque": s, "parte da variância": base * len(normal) / (total_var * len(df)),
                 "nota": "inclui a variância da sessão que não vem dos outros canais"})

    t = pd.DataFrame(rows)
    pd.set_option("display.width", 200)
    print(f"\nVariância diária total do BCP {START[:4]}-{END[:4]}: desvio-padrão {np.sqrt(total_var):.4f}\n")
    print(t.to_string(index=False, float_format=lambda v: f"{v:.4f}"))
    print("\nNota: a noite sobrepõe-se aos outros canais (as notícias da noite também são de mercado ou do BCP),"
          " por isso as partes não somam exatamente 100%.")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    t.to_excel(OUT, index=False)
    print(f"Guardado em {OUT}")


if __name__ == "__main__":
    main()
