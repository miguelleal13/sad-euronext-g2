"""Análise da triagem (Plackett-Burman): efeito principal de cada parâmetro em cada um dos 7 factos.

Para comparar com a ANOVA: mostra também o efeito do parâmetro mais forte da ANOVA na mesma escala (passar de -50%
para +50%). Um parâmetro da triagem "conta" se o efeito for significativo (p < 0.05) e claramente maior do que o da
coluna fantasma.

Uso: python scripts/triagem.py PASTA     (pasta com o precos.csv das corridas triagem01..triagem12)
Escreve data/processed/triagem.xlsx
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
from anova import FACTS, run_facts  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def main():
    folder = Path(sys.argv[1])
    design = pd.read_csv(ROOT / "data" / "processed" / "triagem_desenho.csv", sep=";")
    factors = [c[2:] for c in design.columns if c.startswith("x_")]
    runs = run_facts(folder / "precos.csv", prefix="triagem")
    runs["scenario"] = runs["label"].str.extract(r"^(triagem\d+)")[0]
    df = runs.merge(design, on="scenario", how="inner")
    print(f"{len(df)} corridas em {df['scenario'].nunique()} combinações")
    sheets, summary = {}, []
    for fact in FACTS:
        y = df[fact].to_numpy(float)
        ok = ~np.isnan(y)
        y = y[ok]
        X = df.loc[ok, [f"x_{f}" for f in factors]].to_numpy(float)
        n, ss_tot = len(y), ((y - y.mean()) ** 2).sum()
        rows, ss_model = [], 0.0
        for i, f in enumerate(factors):
            x = X[:, i]
            ss = (y @ x) ** 2 / (x @ x)
            ss_model += ss
            rows.append({"parâmetro": f, "efeito (-50% -> +50%)": 2 * (y @ x) / (x @ x), "SS": ss})
        df_err = n - 1 - len(factors)
        ms_err = (ss_tot - ss_model) / df_err
        t = pd.DataFrame(rows)
        t["% da variância"] = 100 * t["SS"] / ss_tot
        t["p"] = stats.f.sf(t["SS"] / ms_err, 1, df_err)
        t = t.sort_values("% da variância", ascending=False)
        sheets[fact] = t
        sig = t[(t["p"] < 0.05) & (t["parâmetro"] != "fantasma")]
        summary.append({"facto": fact, "parâmetros com p < 0.05": ", ".join(sig["parâmetro"]),
                        "maior efeito": t.iloc[0]["parâmetro"], "% da variância": round(t.iloc[0]["% da variância"], 1),
                        "% do fantasma": round(t.loc[t["parâmetro"] == "fantasma", "% da variância"].iloc[0], 1)})
        print(f"\n== {fact}")
        print(t.to_string(index=False, float_format=lambda v: f"{v:.4g}"))
    res = ROOT / "data" / "processed" / "triagem.xlsx"
    with pd.ExcelWriter(res) as xw:
        pd.DataFrame(summary).to_excel(xw, sheet_name="resumo", index=False)
        df.to_excel(xw, sheet_name="corridas", index=False)
        for fact, t in sheets.items():
            t.to_excel(xw, sheet_name=fact[:31], index=False)
    print("\n" + pd.DataFrame(summary).to_string(index=False))
    print(f"\nGuardado em {res}")


if __name__ == "__main__":
    main()
