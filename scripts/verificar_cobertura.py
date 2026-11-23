"""Verifica quanto do movimento do BCP é coberto pelas fontes identificadas, no treino (2023-24) e no teste (2025-26).

NÃO serve para acrescentar notícias a dedo: serve para reportar se as regras de escolha das notícias cobrem os dois
períodos de forma parecida. Se a cobertura for semelhante, as regras funcionam igual no treino e no teste.

Para cada período:
  - parte da variância do BCP no setor+Portugal, nas notícias da lista e no resto (não identificado);
  - os dias com |retorno| > 3% classificados pela fonte principal:
      notícia            - dia de reação a um comunicado/acontecimento da lista
      setor/Portugal     - sem notícia, e o choque do setor+Portugal tem o mesmo sinal e pelo menos metade do movimento
      não identificado   - o resto
Lê data/processed/choques_reais.csv (treino) e choques_reais_teste.csv (teste).
Uso: python scripts/verificar_cobertura.py     -> escreve data/processed/cobertura.xlsx
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PERIODS = [("treino 2023-24", "choques_reais.csv"), ("teste 2025-26", "choques_reais_teste.csv")]


def main():
    p = pd.read_csv(ROOT / "data" / "raw" / "bcp_daily.csv", index_col=0, parse_dates=True)
    r = np.log(p["Adj Close"]).diff().rename("r")
    summary, bigdays = [], []
    for name, fname in PERIODS:
        f = ROOT / "data" / "processed" / fname
        if not f.exists():
            print(f"AVISO: falta {fname}")
            continue
        c = pd.read_csv(f, sep=";", parse_dates=["data"]).set_index("data")
        if "choque_portugal" not in c:
            c["choque_portugal"] = 0.0
        x = c.join(r, how="inner").dropna(subset=["r"])
        x["tipo"] = x["tipo"].fillna("")
        x["mercado"] = x["choque_setor"] + x["choque_portugal"]
        news = x["choque_noticia"] != 0
        x["resto"] = x["r"] - x["r"].mean() - x["mercado"] - x["choque_noticia"]
        tot = x["r"].var() * len(x)
        big = x[x["r"].abs() > 0.03].copy()

        def fonte(row):
            if row["choque_noticia"] != 0:
                return "notícia"
            if np.sign(row["mercado"]) == np.sign(row["r"]) and abs(row["mercado"]) >= 0.5 * abs(row["r"]):
                return "setor/Portugal"
            return "não identificado"
        big["fonte"] = big.apply(fonte, axis=1)
        cnt = big["fonte"].value_counts()
        summary.append({
            "período": name, "dias": len(x), "dias com |r| > 3%": len(big),
            "% variância setor+Portugal": round(100 * (x["mercado"] ** 2).sum() / tot, 1),
            "% variância notícias da lista": round(100 * (x.loc[news, "choque_noticia"] ** 2).sum() / tot, 1),
            "% variância não identificada": round(100 * (x.loc[~news, "resto"] ** 2).sum() / tot, 1),
            "dias grandes: notícia": int(cnt.get("notícia", 0)),
            "dias grandes: setor/Portugal": int(cnt.get("setor/Portugal", 0)),
            "dias grandes: não identificado": int(cnt.get("não identificado", 0)),
        })
        big["período"] = name
        bigdays.append(big.reset_index()[["período", "data", "r", "mercado", "choque_noticia", "tipo", "fonte"]])
    s = pd.DataFrame(summary)
    b = pd.concat(bigdays) if bigdays else pd.DataFrame()
    pd.set_option("display.width", 220)
    print(s.T.to_string(header=False))
    if len(b):
        print("\nMaiores dias do teste e fonte principal:")
        t = b[b["período"].str.startswith("teste")]
        print(t.reindex(t["r"].abs().sort_values(ascending=False).index).head(20)
              .to_string(index=False, float_format=lambda v: f"{v:+.4f}"))
    out = ROOT / "data" / "processed" / "cobertura.xlsx"
    with pd.ExcelWriter(out) as xw:
        s.to_excel(xw, sheet_name="resumo", index=False)
        b.to_excel(xw, sheet_name="dias_grandes", index=False)
    print(f"\nGuardado em {out}")


if __name__ == "__main__":
    main()
