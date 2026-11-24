"""Choques reais do período de TESTE (2025-01-02 a 2026-10-23), com os parâmetros estimados no TREINO (2023-2024).

Para o teste ser honesto, nada é estimado com os dados de 2025-2026:
  - o beta do BCP ao setor bancário europeu, a constante e o canal Portugal (beta e regra |t| > 2) são os de 2023-2024;
  - o dia de reação de cada tipo de comunicado é o medido em 2023-2024;
  - os movimentos não identificados continuam a ser sorteados dos de 2023-2024 (residuos_reais.csv), não dos de teste.
Dos dados de 2025-2026 só se usam os retornos reais do setor e do mercado português (os choques que aconteceram) e
os comunicados/acontecimentos com data (data/raw/noticias_bcp.csv).

O choque de cada comunicado no teste é o retorno anormal do BCP no dia de reação, calculado com o beta do treino.
(O choque de um acontecimento é sempre medido no próprio dia em que acontece: é o mesmo princípio do treino.)

Uso: python scripts/choques_teste.py                                   (teste 2025-2026)
     python scripts/choques_teste.py 2020-01-01 2021-12-31 teste2020     (outro período de teste)
Escreve data/processed/choques_reais_<nome>.csv (mesmo formato do choques_reais.csv) e .xlsx
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from choques_reais import portugal_returns, sector_returns  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TRAIN = ("2023-01-01", "2024-12-31")
TEST = (sys.argv[1], sys.argv[2]) if len(sys.argv) > 2 else ("2025-01-01", "2026-12-31")
NAME = sys.argv[3] if len(sys.argv) > 3 else "teste"


def main():
    p = pd.read_csv(ROOT / "data" / "raw" / "bcp_daily.csv", index_col=0, parse_dates=True)
    r = np.log(p["Adj Close"]).diff().rename("bcp")
    start = (pd.Timestamp(min(TEST[0], TRAIN[0])) - pd.Timedelta(days=40)).strftime("%Y-%m-%d")
    s, ticker = sector_returns(end="2026-12-31", start=start)
    s.index = pd.to_datetime(s.index).tz_localize(None).normalize()
    pt, n_pt = portugal_returns(end="2026-12-31", start=start)
    allx = pd.concat([r, s], axis=1).dropna()
    allx["pt"] = pt.reindex(allx.index).fillna(0.0) if pt is not None else 0.0
    n = pd.read_csv(ROOT / "data" / "raw" / "noticias_bcp.csv", sep=";", parse_dates=["data"])
    n = n[~n["tipo"].str.endswith("(imprensa)") & (n["tipo"] != "BCE")]

    def reaction_days(df, news, lags):
        out = {}
        for _, x in news.iterrows():
            pos = df.index.searchsorted(x["data"]) + lags.get(x["tipo"], 0)
            if pos < len(df):
                out.setdefault(df.index[pos], []).append(x["tipo"])
        return out

    # ---------- TREINO: estimar tudo ----------
    tr = allx.loc[TRAIN[0]:TRAIN[1]]
    ntr = n[(n["data"] >= TRAIN[0]) & (n["data"] <= TRAIN[1])]
    tipos = sorted(ntr["tipo"].unique())
    any_tr = set(reaction_days(tr, ntr, {t: 0 for t in tipos})) | set(reaction_days(tr, ntr, {t: 1 for t in tipos}))
    q = tr.drop(list(any_tr))
    beta = np.cov(q["bcp"], q["setor"])[0, 1] / q["setor"].var()
    alpha = q["bcp"].mean() - beta * q["setor"].mean()
    g = np.cov(q["pt"], q["setor"])[0, 1] / q["setor"].var() if q["setor"].var() > 0 else 0.0
    X = np.column_stack([np.ones(len(q)), q["setor"], q["pt"] - g * q["setor"]])
    b, *_ = np.linalg.lstsq(X, q["bcp"].to_numpy(), rcond=None)
    e = q["bcp"].to_numpy() - X @ b
    se = np.sqrt(np.diag(e @ e / (len(e) - 3) * np.linalg.inv(X.T @ X)))
    beta_pt = b[2] if abs(b[2] / se[2]) > 2 else 0.0
    if beta_pt != 0:
        alpha, beta = b[0], b[1]
    abn_tr = tr["bcp"] - alpha - beta * tr["setor"] - beta_pt * (tr["pt"] - g * tr["setor"])
    lags = {}
    for t in tipos:
        v = {}
        for lag in (0, 1):
            d = [k for k, ts in reaction_days(tr, ntr, {t: lag}).items() if t in ts]
            v[lag] = (abn_tr.loc[d] ** 2).mean() if d else 0.0
        lags[t] = max(v, key=v.get)

    # ---------- TESTE: aplicar ----------
    te = allx.loc[TEST[0]:TEST[1]]
    nte = n[(n["data"] >= TEST[0]) & (n["data"] <= TEST[1])]
    novos = sorted(set(nte["tipo"]) - set(lags))
    days = reaction_days(te, nte, lags)
    pt_res = te["pt"] - g * te["setor"]
    choque_pt = beta_pt * pt_res
    abn = te["bcp"] - alpha - beta * te["setor"] - choque_pt
    out = pd.DataFrame({"data": te.index.strftime("%Y-%m-%d"), "choque_setor": beta * te["setor"].to_numpy()})
    out["choque_noticia"] = [abn[d] if d in days else 0.0 for d in te.index]
    out["tipo"] = [" + ".join(sorted(set(days[d]))) if d in days else "" for d in te.index]
    out["choque_portugal"] = choque_pt.to_numpy()
    out.insert(0, "dia", range(len(out)))

    tot = te["bcp"].var()
    resumo = pd.DataFrame([
        ("período de teste", f"{te.index.min().date()} a {te.index.max().date()}"), ("dias de teste", len(te)),
        ("índice do setor", ticker), ("beta ao setor (do treino)", round(beta, 3)),
        ("beta ao mercado português (do treino)", round(beta_pt, 3)),
        ("comunicados/acontecimentos no teste", len(nte)), ("dias com choque de notícia", len(days)),
        ("tipos sem dia de reação medido no treino (usam o próprio dia)", ", ".join(novos) or "nenhum"),
        ("preço inicial do teste (último fecho antes do início)", round(float(p.loc[:pd.Timestamp(TEST[0]) - pd.Timedelta(days=1), "Close"].iloc[-1]), 4)),
        ("parte da variância do BCP (teste) explicada pelo setor", round(out["choque_setor"].var() / tot, 3)),
        ("parte da variância do BCP (teste) nos choques de notícias",
         round((out["choque_noticia"] ** 2).sum() / (tot * len(te)), 3)),
        ("desvio-padrão diário do BCP no teste", round(np.sqrt(tot), 4)),
    ], columns=["medida", "valor"])
    path = ROOT / "data" / "processed" / f"choques_reais_{NAME}"
    out.to_csv(path.with_suffix(".csv"), sep=";", index=False)
    with pd.ExcelWriter(path.with_suffix(".xlsx")) as xw:
        resumo.to_excel(xw, sheet_name="resumo", index=False)
        out.to_excel(xw, sheet_name="choques", index=False)
    print(resumo.to_string(index=False))
    print(f"\nTempo de paragem do teste no AnyLogic: {len(te) * 510} minutos ({len(te)} dias x 510)")
    print(f"Guardado em {path.with_suffix('.csv')} e .xlsx")


if __name__ == "__main__":
    main()
