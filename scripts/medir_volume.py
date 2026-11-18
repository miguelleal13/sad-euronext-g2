"""Mede com os dados reais do BCP (2023-2024) a dinâmica do volume diário, para substituir parâmetros afinados.

Regressão (mínimos quadrados) do log do volume, em desvio da média móvel de 60 dias (tira tendências lentas):
  logvol_hoje = a + b1 * logvol_ontem + b2 * (comunicado hoje) + b3 * |r ontem| / 0.0165 + b4 * |choque do setor hoje| / 0.0165
  b1 -> persistência do volume            (no modelo: activityPersist)
  b2 -> salto do volume com um comunicado (no modelo: activityNewsJump)
  b3 -> "atenção": mais volume no dia a seguir a um dia de grande movimento (no modelo: mecanismo A2)
  b4 -> salto do volume com o choque do setor, por cada 1.65% (a média de |r| do BCP)
Mostra o erro-padrão e o t de cada coeficiente (|t| > 2 = significativo a ~5%).

Uso: python scripts/medir_volume.py   (lê data/raw/bcp_daily.csv e data/processed/choques_reais.csv)
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent


def main():
    d = pd.read_csv(ROOT / "data" / "raw" / "bcp_daily.csv", index_col=0, parse_dates=True)
    c = pd.read_csv(ROOT / "data" / "processed" / "choques_reais.csv", sep=";", parse_dates=["data"]).set_index("data")
    x = d.loc["2023-01-01":"2024-12-31"].copy()
    x["r"] = np.log(x["Adj Close"]).diff()
    x = x.join(c[["choque_setor", "choque_noticia"]], how="inner")
    lv = np.log(x["Volume"])
    dev = lv - lv.rolling(60, min_periods=20).mean()
    df = pd.DataFrame({"y": dev, "vol ontem": dev.shift(1),
                       "comunicado hoje": (x["choque_noticia"] != 0).astype(float),
                       "|r| ontem (atenção)": x["r"].abs().shift(1) / 0.0165,
                       "|setor| hoje": x["choque_setor"].abs() / 0.0165}).dropna()
    X = np.column_stack([np.ones(len(df)), df.drop(columns="y").to_numpy()])
    y = df["y"].to_numpy()
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    e = y - X @ b
    se = np.sqrt(np.diag(e @ e / (len(y) - X.shape[1]) * np.linalg.inv(X.T @ X)))
    out = pd.DataFrame({"coeficiente": b, "erro-padrão": se, "t": b / se},
                       index=["constante"] + list(df.columns[1:]))
    print(f"{len(df)} dias\n")
    print(out.to_string(float_format=lambda v: f"{v:+.3f}"))
    print(f"\nDesvio-padrão do resto (parte aleatória do volume): {e.std():.3f}")


if __name__ == "__main__":
    main()
