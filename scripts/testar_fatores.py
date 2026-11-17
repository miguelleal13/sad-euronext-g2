"""Testa com dados reais (2023-2024) que fatores externos mexem no preço do BCP, para justificar
quais entram no modelo e quais ficam de fora.

Método: regressão do retorno diário do BCP em cada fator candidato, sozinho e junto com o setor bancário
europeu (o fator que o modelo já usa). Para cada candidato mostra:
  R2 sozinho         - que parte da variância do BCP o fator explica sozinho
  R2 a mais          - quanto acrescenta DEPOIS do setor (o que importa para o modelo: se for ~0, o fator
                       já está dentro do setor ou não mexe no BCP)
  t                  - significância do coeficiente na regressão com o setor (|t| > 2 ~ significativo a 5%)
Os dias de comunicados do BCP e de acontecimentos portugueses ficam fora da regressão (já são tratados à parte).

Fatores candidatos (todos públicos, descarregados do Yahoo Finance):
  setor bancário europeu (EURO STOXX Banks)     - já no modelo
  mercado europeu (EURO STOXX 50)                - mercado em geral
  mercado americano (S&P 500, do dia anterior)   - fecha depois de Lisboa, por isso conta no dia seguinte
  volatilidade americana (VIX, variação)         - medo / aversão ao risco global
  euro-dólar                                     - câmbio
  petróleo Brent                                 - energia, inflação
  euro-zlóti polaco                              - o BCP tem um banco na Polónia (Bank Millennium)
  bancos portugueses (BPI não cotado; usa o PSI) - mercado português

Uso: python scripts/testar_fatores.py
Escreve data/processed/testar_fatores.xlsx
"""
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

ROOT = Path(__file__).resolve().parent.parent
START, END = "2023-01-01", "2024-12-31"
CANDIDATOS = [   # (nome, lista de tickers alternativos, desfasamento em dias, transformação)
    ("setor bancário europeu (EURO STOXX Banks)", ["^SX7E", "EXX1.DE"], 0, "ret"),
    ("mercado europeu (EURO STOXX 50)", ["^STOXX50E", "EXW1.DE"], 0, "ret"),
    ("mercado português (PSI)", ["PSI20.LS", "^PSI20"], 0, "ret"),
    ("mercado português SEM o BCP (média de ações do PSI)", ["PT_EX_BCP"], 0, "ret"),
    ("mercado americano (S&P 500, dia anterior)", ["^GSPC", "SPY"], 1, "ret"),
    ("volatilidade americana (VIX, dia anterior)", ["^VIX"], 1, "ret"),
    ("euro-dólar", ["EURUSD=X"], 0, "ret"),
    ("petróleo Brent", ["BZ=F"], 0, "ret"),
    ("euro-zlóti polaco (Polónia)", ["EURPLN=X"], 0, "ret"),
]


PSI_EX_BCP = ["EDP.LS", "EDPR.LS", "GALP.LS", "JMT.LS", "NOS.LS", "SON.LS", "CTT.LS", "NVG.LS", "SEM.LS",
              "RENE.LS", "ALTR.LS", "COR.LS", "IBS.LS", "EGL.LS"]   # ações do PSI em 2023-24, sem o BCP


def portugal_ex_bcp():
    """Retorno diário médio (pesos iguais) das ações do PSI sem o BCP."""
    rets = []
    for t in PSI_EX_BCP:
        s, _ = download([t])
        if s is not None:
            rets.append(s.rename(t))
    if not rets:
        return None, None
    m = pd.concat(rets, axis=1).loc["2022-12-01":]
    return m.mean(axis=1, skipna=True), f"média de {m.shape[1]} ações"


def download(tickers):
    if tickers == ["PT_EX_BCP"]:
        return portugal_ex_bcp()
    for t in tickers:
        try:
            d = yf.download(t, start="2022-12-01", end="2025-01-10", auto_adjust=False, progress=False)
        except Exception:
            continue
        if len(d):
            if hasattr(d.columns, "levels"):
                d.columns = d.columns.get_level_values(0)
            col = "Adj Close" if "Adj Close" in d else "Close"
            s = d[col].dropna()
            s.index = pd.to_datetime(s.index).tz_localize(None).normalize()
            return np.log(s).diff(), t
    return None, None


def ols(y, X):
    X = np.column_stack([np.ones(len(y)), X])
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    e = y - X @ b
    se = np.sqrt(np.diag(e @ e / (len(y) - X.shape[1]) * np.linalg.inv(X.T @ X)))
    return b, se, 1 - e.var() / y.var()


def main():
    p = pd.read_csv(ROOT / "data" / "raw" / "bcp_daily.csv", index_col=0, parse_dates=True)
    bcp = np.log(p["Adj Close"]).diff().rename("bcp")
    n = pd.read_csv(ROOT / "data" / "raw" / "noticias_bcp.csv", sep=";", parse_dates=["data"])
    n = n[~n["tipo"].str.endswith("(imprensa)") & (n["tipo"] != "BCE")]
    excl = set()
    for d in n["data"]:          # tira o dia do acontecimento e o seguinte
        excl |= {d.normalize(), (d + pd.Timedelta(days=1)).normalize()}

    series = {}
    for nome, tickers, lag, _ in CANDIDATOS:
        s, t = download(tickers)
        if s is None:
            print(f"  AVISO: não descarregou {nome} ({tickers})")
            continue
        series[nome] = (s.shift(lag) if lag else s, t)
        print(f"  {nome}: {t}")

    setor_nome = CANDIDATOS[0][0]
    if setor_nome not in series:
        raise SystemExit("Sem o índice do setor não dá para comparar; experimenta mais tarde.")
    df = pd.concat([bcp] + [s.rename(k) for k, (s, _) in series.items()], axis=1).loc[START:END]
    df = df[~df.index.isin(excl)].dropna()
    y = df["bcp"].to_numpy()
    _, _, r2_setor = ols(y, df[[setor_nome]].to_numpy())

    rows = []
    for k in series:
        _, _, r2_alone = ols(y, df[[k]].to_numpy())
        if k == setor_nome:
            rows.append({"fator": k, "ticker": series[k][1], "R2 sozinho": r2_alone, "R2 a mais depois do setor": np.nan,
                         "t (com o setor)": np.nan, "decisão": "no modelo"})
            continue
        b, se, r2_both = ols(y, df[[setor_nome, k]].to_numpy())
        rows.append({"fator": k, "ticker": series[k][1], "R2 sozinho": r2_alone,
                     "R2 a mais depois do setor": r2_both - r2_setor, "t (com o setor)": b[2] / se[2], "decisão": ""})
    t = pd.DataFrame(rows)
    pd.set_option("display.width", 200)
    print(f"\n{len(df)} dias (sem dias de comunicados/acontecimentos PT); R2 do setor sozinho = {r2_setor:.3f}\n")
    print(t.to_string(index=False, float_format=lambda v: f"{v:.3f}"))
    print("\nLeitura: se 'R2 a mais' for pequeno (ex.: < 0.01) e |t| < 2, o fator já está no setor ou não mexe no BCP.")
    print("Cuidado com o PSI: o próprio BCP faz parte do índice (com um peso grande), por isso o PSI explica o BCP")
    print("em parte por construção. Um R2 alto do PSI não prova que o 'mercado português' mexe no BCP.")
    out = ROOT / "data" / "processed" / "testar_fatores.xlsx"
    t.to_excel(out, index=False)
    print(f"Guardado em {out}")


if __name__ == "__main__":
    main()
