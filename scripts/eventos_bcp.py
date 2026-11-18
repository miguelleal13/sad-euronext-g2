"""Estudo de eventos com notícias reais do BCP (2023-2024).

Lê data/raw/noticias_bcp.csv (uma linha por notícia: data;tipo;depois_do_fecho;titulo;fonte) e os preços
de data/raw/bcp_daily.csv, e responde a três perguntas:
  1. Quantas notícias de cada tipo houve por ano?
  2. Quanto mexe o BCP nos dias dessas notícias, comparado com os dias sem notícias?
     (depois_do_fecho = 1 conta o dia seguinte, porque a reação só acontece na abertura)
  3. Que dias de grande movimento (|r| > 3%) NÃO têm nenhuma notícia registada?
     Esses dias são a lista para procurar notícias nos jornais e completar o ficheiro.
Os tipos que acabam em "(imprensa)" são notícias de jornais encontradas DEPOIS de saber que o dia foi grande:
servem para explicar esses dias, mas ficam fora das médias por tipo (entrariam com enviesamento de seleção).

Uso: python scripts/eventos_bcp.py
Escreve data/processed/eventos_bcp.xlsx (folhas: por_tipo, dias_grandes_sem_noticia, eventos)
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PRICES = ROOT / "data" / "raw" / "bcp_daily.csv"
NEWS = ROOT / "data" / "raw" / "noticias_bcp.csv"
OUT = ROOT / "data" / "processed" / "eventos_bcp.xlsx"
START, END = "2023-01-01", "2024-12-31"


def main():
    p = pd.read_csv(PRICES, index_col=0, parse_dates=True)
    r = np.log(p["Adj Close"]).diff().loc[START:END].dropna()
    n = pd.read_csv(NEWS, sep=";", parse_dates=["data"])
    n = n[(n["data"] >= START) & (n["data"] <= END)]
    years = r.index.year.nunique()

    # dia de mercado em que cada notícia chega ao preço
    rows = []
    for _, x in n.iterrows():
        pos = r.index.searchsorted(x["data"] + pd.Timedelta(days=1) if x["depois_do_fecho"] == 1 else x["data"])
        if pos < len(r):
            d = r.index[pos]
            rows.append({**x.to_dict(), "dia_reacao": d, "retorno": r[d], "abs_retorno": abs(r[d])})
    ev = pd.DataFrame(rows)
    news_days = set(ev["dia_reacao"])
    quiet = r.drop(list(news_days))
    base_var = quiet.var()

    ev_all = ev
    ev = ev[~ev["tipo"].str.endswith("(imprensa)")]
    t = ev.groupby("tipo").agg(n=("titulo", "size"), abs_retorno_medio=("abs_retorno", "mean"),
                               maior_movimento=("abs_retorno", "max"))
    t["por_ano"] = t["n"] / years
    t["dias_acima_3pct"] = ev.groupby("tipo")["abs_retorno"].apply(lambda s: (s > 0.03).sum())
    t["choque_extra"] = ev.groupby("tipo")["retorno"].apply(lambda s: np.sqrt(max(0.0, (s ** 2).mean() - base_var)))
    t.loc["(dias sem notícia)", ["n", "abs_retorno_medio", "maior_movimento"]] = [len(quiet), quiet.abs().mean(), quiet.abs().max()]
    t.loc["(dias sem notícia)", "dias_acima_3pct"] = (quiet.abs() > 0.03).sum()

    big = r[r.abs() > 0.03]
    sem = big.drop([d for d in big.index if d in news_days]).to_frame("retorno")
    explained = ev_all[ev_all["dia_reacao"].isin(big.index)].sort_values("dia_reacao")
    sem["procurar em"] = "Jornal de Negócios / ECO / Expresso: 'BCP' na data e na véspera"

    pd.set_option("display.width", 200)
    print(f"{len(n)} notícias registadas; {len(r)} dias de mercado; {len(big)} dias com |r| > 3%, "
          f"dos quais {len(big) - len(sem)} têm notícia registada\n")
    print(t.sort_values("abs_retorno_medio", ascending=False).to_string(float_format=lambda v: f"{v:.4f}"))
    print("\nDias com |r| > 3% explicados por uma notícia:")
    print(explained[["dia_reacao", "retorno", "tipo", "titulo"]].to_string(index=False, max_colwidth=90,
                                                                          float_format=lambda v: f"{v:+.4f}"))
    print(f"\n{len(sem)} dias com |r| > 3% sem notícia registada (os maiores primeiro):")
    print(sem.reindex(sem["retorno"].abs().sort_values(ascending=False).index).head(25).to_string(float_format=lambda v: f"{v:+.4f}"))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(OUT) as xw:
        t.to_excel(xw, sheet_name="por_tipo")
        sem.to_excel(xw, sheet_name="dias_grandes_sem_noticia")
        explained.to_excel(xw, sheet_name="dias_grandes_com_noticia", index=False)
        ev_all.to_excel(xw, sheet_name="eventos", index=False)
    print(f"\nGuardado em {OUT}")


if __name__ == "__main__":
    main()
