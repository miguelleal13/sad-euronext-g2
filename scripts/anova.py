"""ANOVA dos 7 factos estilizados em função dos 6 parâmetros sem dados (desenho de anova_desenho.py).

Para cada corrida calcula os 7 factos (como compare_model.py). Depois, para cada facto, decompõe a variância entre
corridas: efeitos principais dos 6 fatores e as 15 interações de 2 fatores (ortogonais no desenho 2^(6-1) VI).
  % da variância - parte da variação do facto explicada por esse efeito (soma de quadrados / total)
  p              - teste F contra o erro (réplicas + interações de ordem superior)
  efeito         - quanto muda o facto em média ao passar do nível -50% para +50%

Uso: python scripts/anova.py PASTA     (pasta com o precos.csv das corridas anova01..anova32)
Escreve data/processed/anova.xlsx (folhas: corridas, um resumo e uma folha por facto)
"""
import itertools
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
from target_stats import stats_from_returns  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DAY = 510
COLS = ["label", "run", "time", "price", "bid", "ask", "volume"]
FACTS = ["volatilidade_diaria", "curtose_excesso", "autocorr_abs_retornos_lag1", "autocorr_retornos_lag1",
         "pct_dias_var_maior_3pct", "corr_volume_absret", "autocorr_volume_lag1"]


def run_facts(path):
    rows, carry = [], None

    def one(g):
        daily = g.assign(day=((g["time"] - 1) // DAY).astype(int)).groupby("day").agg(
            price=("price", "last"), cumvol=("volume", "last"))
        s = stats_from_returns(np.log(daily["price"]).diff(), daily["cumvol"].diff())
        return {"label": g["label"].iloc[0], "run": g["run"].iloc[0], **{k: s[k] for k in FACTS}}

    for chunk in pd.read_csv(path, sep=";", names=COLS, dtype={"label": str, "run": str}, chunksize=2_000_000):
        chunk = chunk[chunk["label"].str.startswith("anova")]
        if carry is not None:
            chunk = pd.concat([carry, chunk])
        if chunk.empty:
            continue
        last = chunk["run"].iloc[-1]
        done, carry = chunk[chunk["run"] != last], chunk[chunk["run"] == last]
        rows += [one(g) for _, g in done.groupby("run", sort=False)]
    if carry is not None and len(carry):
        rows += [one(g) for _, g in carry.groupby("run", sort=False)]
    return pd.DataFrame(rows)


def main():
    folder = Path(sys.argv[1])
    design = pd.read_csv(ROOT / "data" / "processed" / "anova_desenho.csv", sep=";")
    factors = [c[2:] for c in design.columns if c.startswith("x_")]
    runs = run_facts(folder / "precos.csv")
    runs["scenario"] = runs["label"].str.extract(r"^(anova\d+)")[0]
    df = runs.merge(design, on="scenario", how="inner")
    print(f"{len(df)} corridas em {df['scenario'].nunique()} combinações")

    terms = [(f,) for f in factors] + list(itertools.combinations(factors, 2))
    out, summary = {}, []
    for fact in FACTS:
        y = df[fact].to_numpy(float)
        ok = ~np.isnan(y)
        y, X = y[ok], df.loc[ok, [f"x_{f}" for f in factors]].to_numpy(float)
        col = {f: X[:, i] for i, f in enumerate(factors)}
        n, ss_tot = len(y), ((y - y.mean()) ** 2).sum()
        rows, ss_model = [], 0.0
        for t in terms:
            x = np.prod([col[f] for f in t], axis=0)
            ss = (y @ x) ** 2 / (x @ x)
            ss_model += ss
            rows.append({"efeito": " x ".join(t), "SS": ss, "efeito médio (-50% -> +50%)": 2 * (y @ x) / (x @ x)})
        df_err = n - 1 - len(terms)
        ms_err = (ss_tot - ss_model) / df_err
        t = pd.DataFrame(rows)
        t["% da variância"] = 100 * t["SS"] / ss_tot
        t["p"] = stats.f.sf(t["SS"] / ms_err, 1, df_err)
        t = t.sort_values("% da variância", ascending=False)
        out[fact] = t
        top = t.iloc[0]
        summary.append({"facto": fact, "maior efeito": top["efeito"], "% da variância": round(top["% da variância"], 1),
                        "efeitos com p < 0.05": ", ".join(t.loc[t["p"] < 0.05, "efeito"]),
                        "% sem explicação (erro)": round(100 * (ss_tot - ss_model) / ss_tot, 1)})
        print(f"\n== {fact}")
        print(t.head(8).to_string(index=False, float_format=lambda v: f"{v:.4g}"))
    res = ROOT / "data" / "processed" / "anova.xlsx"
    with pd.ExcelWriter(res) as xw:
        pd.DataFrame(summary).to_excel(xw, sheet_name="resumo", index=False)
        df.to_excel(xw, sheet_name="corridas", index=False)
        for fact, t in out.items():
            t.to_excel(xw, sheet_name=fact[:31], index=False)
    print("\n" + pd.DataFrame(summary).to_string(index=False))
    print(f"\nGuardado em {res}")


if __name__ == "__main__":
    main()
