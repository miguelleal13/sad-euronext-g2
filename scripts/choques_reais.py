"""Choques reais para o NewsAgent: o modelo deixa de sortear notícias e passa a usar as de 2023-2024.

Para cada dia de mercado de 2023-2024 calcula, só com dados reais:
  choque_setor   = beta x retorno do índice dos bancos europeus nesse dia
                   (beta estimado por regressão do BCP no índice, nos dias sem comunicado do BCP)
  choque_noticia = retorno anormal do BCP no dia de reação a um comunicado oficial do BCP
                   (retorno do BCP - beta x retorno do índice); 0 nos dias sem comunicado
  choque_portugal = efeito do mercado português SEM o BCP (média das outras ações do PSI), na parte que o setor
                   europeu não explica. Só entra se for significativo (|t| > 2, regra fixada antes de ver o resultado);
                   senão fica a 0. Fica na ÚLTIMA coluna do CSV.
Nada é escolhido para "dar certo": a frequência, o tamanho e a ordem dos choques são os de 2023-2024.

O dia de reação a um comunicado (o próprio dia ou o seguinte, porque muitos saem depois do fecho)
também é medido, para cada tipo de comunicado: o script compara a variância anormal nos dois casos
e usa o que tiver mais reação.
Os comunicados vêm de data/raw/noticias_bcp.csv (só os oficiais do BCP: as linhas "(imprensa)" e "BCE" ficam
de fora, porque foram escolhidas a olhar para o preço ou já estão no índice).

Uso: python scripts/choques_reais.py      (descarrega o índice do Yahoo; lê bcp_daily.csv e noticias_bcp.csv)
Escreve:
  data/processed/choques_reais.csv   - dia;data;choque_setor;choque_noticia;tipo;choque_portugal   (para o AnyLogic ler)
  data/processed/choques_reais.xlsx  - o mesmo + resumo (beta, R2, variâncias, dia de reação)
"""
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

ROOT = Path(__file__).resolve().parent.parent
PRICES = ROOT / "data" / "raw" / "bcp_daily.csv"
NEWS = ROOT / "data" / "raw" / "noticias_bcp.csv"
OUT = ROOT / "data" / "processed" / "choques_reais"
START, END = "2023-01-01", "2024-12-31"
SECTOR = ["^SX7E", "EXX1.DE", "SX7EEX.DE"]   # EURO STOXX Banks (índice ou ETF), pela ordem


def sector_returns():
    for t in SECTOR:
        try:
            d = yf.download(t, start="2022-12-01", end="2025-01-10", auto_adjust=False, progress=False)
        except Exception:
            continue
        if len(d):
            if hasattr(d.columns, "levels"):
                d.columns = d.columns.get_level_values(0)
            col = "Adj Close" if "Adj Close" in d else "Close"
            print(f"Índice do setor: {t} ({len(d)} dias)")
            return np.log(d[col]).diff().rename("setor"), t
    raise SystemExit("Nenhum índice do setor descarregou; experimenta mais tarde (o Yahoo limita pedidos).")


PSI_EX_BCP = ["EDP.LS", "EDPR.LS", "GALP.LS", "JMT.LS", "NOS.LS", "SON.LS", "CTT.LS", "NVG.LS", "SEM.LS",
              "RENE.LS", "ALTR.LS", "COR.LS", "IBS.LS", "EGL.LS"]   # ações do PSI em 2023-24, sem o BCP


def portugal_returns():
    rets = []
    for t in PSI_EX_BCP:
        try:
            d = yf.download(t, start="2022-12-01", end="2025-01-10", auto_adjust=False, progress=False)
        except Exception:
            continue
        if len(d):
            if hasattr(d.columns, "levels"):
                d.columns = d.columns.get_level_values(0)
            col = "Adj Close" if "Adj Close" in d else "Close"
            x = d[col].dropna()
            x.index = pd.to_datetime(x.index).tz_localize(None).normalize()
            rets.append(np.log(x).diff().rename(t))
    if not rets:
        print("AVISO: nenhuma ação portuguesa descarregou; canal Portugal fica a 0")
        return None, 0
    m = pd.concat(rets, axis=1)
    print(f"Mercado português sem o BCP: média de {m.shape[1]} ações")
    return m.mean(axis=1, skipna=True).rename("pt"), m.shape[1]


def main():
    p = pd.read_csv(PRICES, index_col=0, parse_dates=True)
    r = np.log(p["Adj Close"]).diff().rename("bcp")
    s, ticker = sector_returns()
    pt, n_pt = portugal_returns()
    df = pd.concat([r, s], axis=1).loc[START:END].dropna()   # só dias com as duas bolsas abertas
    df["pt"] = pt.reindex(df.index).fillna(0.0) if pt is not None else 0.0

    n = pd.read_csv(NEWS, sep=";", parse_dates=["data"])
    n = n[~n["tipo"].str.endswith("(imprensa)") & (n["tipo"] != "BCE")]
    n = n[(n["data"] >= START) & (n["data"] <= END)]

    def reaction_days(lags):
        """lags: dicionário tipo -> 0 (próprio dia) ou 1 (dia seguinte)."""
        out = {}
        for _, x in n.iterrows():
            pos = df.index.searchsorted(x["data"]) + lags.get(x["tipo"], 0)
            if pos < len(df):
                out.setdefault(df.index[pos], []).append(x["tipo"])
        return out

    tipos = sorted(n["tipo"].unique())
    # beta com os dias sem comunicado (nem no próprio dia nem no seguinte)
    news_any = set(reaction_days({t: 0 for t in tipos})) | set(reaction_days({t: 1 for t in tipos}))
    quiet = df.drop(list(news_any))
    beta = np.cov(quiet["bcp"], quiet["setor"])[0, 1] / quiet["setor"].var()
    alpha = quiet["bcp"].mean() - beta * quiet["setor"].mean()
    r2 = 1 - (quiet["bcp"] - alpha - beta * quiet["setor"]).var() / quiet["bcp"].var()

    # canal Portugal: parte do mercado português (sem BCP) que o setor europeu não explica
    g = np.cov(quiet["pt"], quiet["setor"])[0, 1] / quiet["setor"].var() if quiet["setor"].var() > 0 else 0.0
    pt_res = df["pt"] - g * df["setor"]
    q_res = pt_res.loc[quiet.index]
    X = np.column_stack([np.ones(len(quiet)), quiet["setor"], q_res])
    b, *_ = np.linalg.lstsq(X, quiet["bcp"].to_numpy(), rcond=None)
    e = quiet["bcp"].to_numpy() - X @ b
    se = np.sqrt(np.diag(e @ e / (len(e) - 3) * np.linalg.inv(X.T @ X)))
    t_pt = b[2] / se[2] if se[2] > 0 else 0.0
    beta_pt = b[2] if abs(t_pt) > 2 else 0.0          # regra fixada antes: só entra se |t| > 2
    if beta_pt != 0:
        alpha, beta = b[0], b[1]
    choque_pt = beta_pt * pt_res
    abn = df["bcp"] - alpha - beta * df["setor"] - choque_pt

    # dia de reação medido POR TIPO: o desfasamento (0 ou 1 dia) com mais variância anormal nesse tipo
    lags, lag_rows = {}, []
    for t in tipos:
        v = {}
        for lag in (0, 1):
            d = reaction_days({t: lag})
            d = [k for k, ts in d.items() if t in ts]
            v[lag] = (abn.loc[d] ** 2).mean() if d else 0.0
        lags[t] = max(v, key=v.get)
        lag_rows.append((t, (n["tipo"] == t).sum(), f"{v[0]:.6f}", f"{v[1]:.6f}",
                         "próprio dia" if lags[t] == 0 else "dia seguinte"))
    days = reaction_days(lags)
    lag_tab = pd.DataFrame(lag_rows, columns=["tipo", "n", "var. anormal no próprio dia",
                                              "var. anormal no dia seguinte", "dia de reação usado"])

    out = pd.DataFrame({"data": df.index.strftime("%Y-%m-%d"), "choque_setor": beta * df["setor"].to_numpy()})
    out["choque_noticia"] = [abn[d] if d in days else 0.0 for d in df.index]
    out["tipo"] = [" + ".join(sorted(set(days[d]))) if d in days else "" for d in df.index]
    out["choque_portugal"] = choque_pt.to_numpy()
    out.insert(0, "dia", range(len(out)))

    tot = df["bcp"].var()
    resumo = pd.DataFrame([
        ("índice do setor", ticker), ("dias de mercado", len(df)),
        ("beta do BCP ao setor", round(beta, 3)), ("R2 da regressão (dias sem comunicado)", round(r2, 3)),
        ("desvio-padrão diário do BCP", round(np.sqrt(tot), 4)),
        ("parte da variância do BCP explicada pelo setor", round((beta ** 2) * df["setor"].var() / tot, 3)),
        ("mercado português sem BCP", f"média de {n_pt} ações"),
        ("beta do BCP ao mercado português (parte não explicada pelo setor)", round(b[2], 3)),
        ("t desse beta", round(t_pt, 2)),
        ("canal Portugal no modelo", "sim (|t| > 2)" if beta_pt != 0 else "não (|t| <= 2): fica a 0"),
        ("parte da variância do BCP explicada pelo canal Portugal", round(choque_pt.var() / tot, 3)),
        ("dias com comunicado", len(days)),
        ("parte da variância do BCP nos choques de comunicados", round((out["choque_noticia"] ** 2).sum() / (tot * len(df)), 3)),
        ("variância anormal média nos dias sem comunicado", f"{(abn.drop(list(news_any)) ** 2).mean():.6f}"),
        ("parte da variância do BCP sem explicação (resíduo dos dias sem comunicado)",
         round((abn.drop(list(days)) ** 2).sum() / (tot * len(df)), 3)),
    ], columns=["medida", "valor"])

    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT.with_suffix(".csv"), sep=";", index=False)
    with pd.ExcelWriter(OUT.with_suffix(".xlsx")) as xw:
        resumo.to_excel(xw, sheet_name="resumo", index=False)
        lag_tab.to_excel(xw, sheet_name="dia_de_reacao", index=False)
        out.to_excel(xw, sheet_name="choques", index=False)
    print(resumo.to_string(index=False))
    print("\nDia de reação por tipo (medido):")
    print(lag_tab.to_string(index=False))
    print("\nMaiores choques de comunicados:")
    print(out[out["choque_noticia"] != 0].reindex(out["choque_noticia"].abs().sort_values(ascending=False).index)
          .head(10).to_string(index=False, float_format=lambda v: f"{v:+.4f}"))
    print(f"\nGuardado em {OUT.with_suffix('.csv')} e .xlsx")


if __name__ == "__main__":
    main()
