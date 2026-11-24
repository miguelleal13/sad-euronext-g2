"""Mede, ano a ano (2010-2026), o tamanho dos movimentos do BCP que o mercado não explica.

Pergunta: o modelo sorteia os movimentos não identificados de 2023-2024. Esse período é típico, ou foi
invulgarmente calmo ou agitado? Se for típico, usar 2023-2024 fica justificado com dados.

Para cada ano calcula, com os betas estimados em 2023-2024 (os mesmos do modelo):
  resto = retorno do BCP - beta x setor bancário europeu - beta_pt x mercado português (sem o BCP)
e mostra o seu desvio-padrão. Como antes de 2020 não temos a lista de comunicados, o resto inclui também as notícias
do BCP; por isso a comparação justa é com a linha de 2023-2024 calculada da MESMA maneira (todos os dias).
Para os anos com lista de notícias (2020-21, 2023-24, 2025-26) mostra também o resto só nos dias sem notícia.

Cuidado com 2010-2017: o BCP teve aumentos de capital e os preços ajustados do Yahoo têm saltos artificiais
(ex.: +12% e +24% em junho/julho de 2014). Por isso mostra também uma medida robusta (1.4826 x desvio absoluto
mediano), que quase não é afetada por meia dúzia de dias anormais.

Uso: python scripts/medir_residuos_anuais.py    (descarrega o setor e as ações portuguesas desde 2009)
Escreve data/processed/residuos_anuais.xlsx
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from choques_reais import portugal_returns, sector_returns  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TRAIN = ("2023-01-01", "2024-12-31")


def robust_sd(x):
    x = x.dropna()
    return 1.4826 * np.median(np.abs(x - np.median(x)))


def main():
    p = pd.read_csv(ROOT / "data" / "raw" / "bcp_daily.csv", index_col=0, parse_dates=True)
    r = np.log(p["Adj Close"]).diff().rename("bcp")
    s, ticker = sector_returns(end="2026-12-31", start="2009-11-01")
    s.index = pd.to_datetime(s.index).tz_localize(None).normalize()
    pt, _ = portugal_returns(end="2026-12-31", start="2009-11-01")
    x = pd.concat([r, s], axis=1).dropna()
    x["pt"] = pt.reindex(x.index).fillna(0.0) if pt is not None else 0.0

    n = pd.read_csv(ROOT / "data" / "raw" / "noticias_bcp.csv", sep=";", parse_dates=["data"])
    n = n[~n["tipo"].str.endswith("(imprensa)") & (n["tipo"] != "BCE")]
    news_days = set()
    for d in n["data"]:                      # dia do acontecimento e o seguinte
        pos = x.index.searchsorted(d)
        news_days |= {x.index[k] for k in (pos, pos + 1) if k < len(x)}

    # betas do treino (dias sem notícia de 2023-2024), como no modelo
    tr = x.loc[TRAIN[0]:TRAIN[1]]
    q = tr.drop([d for d in tr.index if d in news_days])
    g = np.cov(q["pt"], q["setor"])[0, 1] / q["setor"].var()
    X = np.column_stack([np.ones(len(q)), q["setor"], q["pt"] - g * q["setor"]])
    b, *_ = np.linalg.lstsq(X, q["bcp"].to_numpy(), rcond=None)
    x["resto"] = x["bcp"] - b[0] - b[1] * x["setor"] - b[2] * (x["pt"] - g * x["setor"])
    x["sem_noticia"] = ~x.index.isin(list(news_days))

    rows = []
    for y, g_ in x.groupby(x.index.year):
        with_list = y in (2020, 2021, 2023, 2024, 2025, 2026)
        rows.append({"ano": y, "dias": len(g_), "dp BCP": g_["bcp"].std(),
                     "dp resto (todos os dias)": g_["resto"].std(),
                     "dp robusto resto": robust_sd(g_["resto"]),
                     "parte da variância no resto": g_["resto"].var() / g_["bcp"].var(),
                     "dp resto (dias sem notícia)": g_.loc[g_["sem_noticia"], "resto"].std() if with_list else np.nan})
    t = pd.DataFrame(rows)
    ref = x.loc[TRAIN[0]:TRAIN[1], "resto"]
    ref_sd, ref_rob = ref.std(), robust_sd(ref)
    pd.set_option("display.width", 200)
    print(f"Betas do treino: setor {b[1]:.3f}, Portugal {b[2]:.3f}  (índice do setor: {ticker})\n")
    print(t.to_string(index=False, float_format=lambda v: f"{v:.4f}"))
    yearly = t["dp robusto resto"]
    print(f"\n2023-2024 (todos os dias): dp do resto {ref_sd:.4f}, robusto {ref_rob:.4f}")
    print(f"Mediana dos anos 2010-2026 (robusto): {yearly.median():.4f}; "
          f"anos com resto robusto abaixo do de 2023-24: {(yearly < ref_rob).sum()} de {len(yearly)}")
    out = ROOT / "data" / "processed" / "residuos_anuais.xlsx"
    t.to_excel(out, index=False)
    print(f"Guardado em {out}")


if __name__ == "__main__":
    main()
