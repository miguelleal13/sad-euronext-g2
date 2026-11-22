"""Informação não identificada: os movimentos do BCP em 2023-2024 que nem o setor, nem o mercado português,
nem os comunicados/acontecimentos explicam (os ~42% da variância).

Porque entra no modelo: a ANOVA (32 combinações) e a triagem (12 combinações, 16 parâmetros no total) mostraram que
nenhum valor dos parâmetros dos agentes gera esta parte sem criar reversões (autocorrelação dos retornos ~ -0.2),
enquanto no BCP ela não tem memória (autocorrelação ~0). Comporta-se como informação nova ao acaso.

Como entra (sem copiar o preço): o modelo sorteia em cada dia um destes resíduos, por ordem aleatória e diferente em
cada réplica (reamostragem com reposição). Usa-se o tamanho e a forma real destes movimentos, não a sua ordem.

O que este script faz:
  1. resíduo de cada dia = retorno do BCP - média - choque do setor - choque Portugal - choque de comunicado,
     guardado só para os dias SEM comunicado/acontecimento (nesses dias o resíduo não inclui notícias);
  2. mede a subida do volume com o tamanho do resíduo (como medir_volume.py), para a atividade do modelo reagir
     a esta informação como reage ao setor;
  3. escreve data/processed/residuos_reais.csv (uma coluna: residuo) para o AnyLogic ler.

Uso: python scripts/residuos.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent


def main():
    p = pd.read_csv(ROOT / "data" / "raw" / "bcp_daily.csv", index_col=0, parse_dates=True)
    c = pd.read_csv(ROOT / "data" / "processed" / "choques_reais.csv", sep=";", parse_dates=["data"]).set_index("data")
    if "choque_portugal" not in c:
        c["choque_portugal"] = 0.0
    x = p.loc["2023-01-01":"2024-12-31"].copy()
    x["r"] = np.log(x["Adj Close"]).diff()
    x = x.join(c[["choque_setor", "choque_noticia", "choque_portugal"]], how="inner").dropna(subset=["r"])
    quiet = x["choque_noticia"] == 0
    res_all = x["r"] - x["choque_setor"] - x["choque_portugal"] - x["choque_noticia"]
    res_all = res_all - res_all[quiet].mean()
    res = res_all[quiet]

    # volume: subida com |resíduo| (mesma regressão de medir_volume.py, com o resíduo acrescentado)
    lv = np.log(x["Volume"])
    dev = lv - lv.rolling(60, min_periods=20).mean()
    df = pd.DataFrame({"y": dev, "vol ontem": dev.shift(1), "comunicado hoje": (~quiet).astype(float),
                       "|setor| hoje": x["choque_setor"].abs() / 0.0165,
                       "|resíduo| hoje": res_all.abs().where(quiet, 0.0) / 0.0165}).dropna()
    X = np.column_stack([np.ones(len(df)), df.drop(columns="y").to_numpy()])
    y = df["y"].to_numpy()
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    e = y - X @ b
    se = np.sqrt(np.diag(e @ e / (len(y) - X.shape[1]) * np.linalg.inv(X.T @ X)))
    coef = pd.DataFrame({"coeficiente": b, "t": b / se}, index=["constante"] + list(df.columns[1:]))

    tot = x["r"].var()
    print(f"Dias sem comunicado/acontecimento: {len(res)} de {len(x)}")
    print(f"Desvio-padrão diário do resíduo: {res.std():.4f}  (BCP: {x['r'].std():.4f})")
    print(f"Parte da variância do BCP: {res.var() * len(res) / (tot * len(x)):.3f}")
    print(f"Curtose do resíduo: {res.kurt():.2f}   autocorrelação: {res.autocorr():.3f}   "
          f"autocorrelação de |resíduo|: {res.abs().autocorr():.3f}")
    print("\nVolume (log, desvio da média de 60 dias):")
    print(coef.to_string(float_format=lambda v: f"{v:+.3f}"))
    out = ROOT / "data" / "processed" / "residuos_reais.csv"
    res.rename("residuo").to_frame().to_csv(out, sep=";", index=False)
    print(f"\n{len(res)} resíduos guardados em {out}")


if __name__ == "__main__":
    main()
