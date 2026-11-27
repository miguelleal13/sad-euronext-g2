"""Passo 11 do guião: efeito dos colares em cada cenário, com testes (fixados em docs/KPIS_CENARIOS.md).

Para cada ficheiro data/processed/kpis_choque_<nome>.xlsx (folha "runs"), agrupa as corridas por tudo o que
NÃO são os colares (o label sem o "_cX") e compara cada conjunto de colares com "sem colares" (c0):
  - indicadores contínuos: média sem e com colares, diferença, intervalo de 95% da diferença e teste t de Welch;
  - crash (limiar principal e de robustez): nº de corridas com crash e teste exato de Fisher.
Regra de leitura fixada antes: uma conclusão sobre o crash só é robusta se tiver o mesmo sentido com os dois
limiares e com a queda a mais.

Quando uma experiência não tem corridas sem colares (ex.: Limiares, só com colares personalizados), usa as
corridas sem colares de outra experiência com as mesmas condições (mesmos parâmetros fora dos colares e as mesmas
sementes), indicada com --base (ex.: o Cenário 2).

Uso: python scripts/resultados_cenarios.py cenario2_comstartday cenario3_comStartDay ...
     python scripts/resultados_cenarios.py cenarioLimiar --base cenario2_comstartday
Escreve data/processed/resultados_cenarios.xlsx (folhas "continuos" e "crash")
"""
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
KPIS = ["queda_max_dia", "queda_a_mais", "queda_30min", "ret_fecho", "ret_5d", "recupera_meia_min",
        "spread_dia_choque", "spread_5d", "volume_dia_choque", "volume_5d", "min_reserva_dia_choque",
        "n_reservas_dia_choque"]


def welch(x, y):
    x, y = x.dropna(), y.dropna()
    if len(x) < 2 or len(y) < 2:
        return np.nan, np.nan, np.nan
    d = y.mean() - x.mean()
    vx, vy = x.var() / len(x), y.var() / len(y)
    se = np.sqrt(vx + vy)
    if se == 0:
        return d, d, d, 1.0
    dfree = (vx + vy) ** 2 / (vx ** 2 / (len(x) - 1) + vy ** 2 / (len(y) - 1))
    q = stats.t.ppf(0.975, dfree)
    return d, d - q * se, d + q * se, 2 * stats.t.sf(abs(d / se), dfree)


def cond(label):
    """Condições fora dos colares: sem o nome do cenário, o conjunto de colares e os limiares personalizados."""
    s = "_" + re.sub(r"^[^_]+_", "", label)
    return re.sub(r"_(c\d+|d[\d.]+|s[\d.]+)(?=_|$)", "", s).lstrip("_")


def load(name):
    return pd.read_excel(ROOT / "data" / "processed" / f"kpis_choque_{name}.xlsx", sheet_name="runs")


def main():
    args = sys.argv[1:]
    if not args:
        raise SystemExit(__doc__)
    bases = []
    if "--base" in args:
        i = args.index("--base")
        bases, args = args[i + 1:], args[:i]
    ref = pd.concat([load(b) for b in bases]) if bases else pd.DataFrame(columns=["label", "colares"])
    if len(ref):
        ref = ref[ref["colares"] == 0].assign(cond=lambda d: d["label"].map(cond))
    cont, crash = [], []
    for name in args:
        r = load(name)
        r["grupo"] = r["label"].map(lambda s: re.sub(r"_c\d+", "", s))
        for grupo, g in r.groupby("grupo"):
            base = g[g["colares"] == 0]
            if base.empty and len(ref):
                base = ref[ref["cond"] == cond(g["label"].iloc[0])]
            if base.empty:
                print(f"  AVISO: {grupo} sem corridas sem colares para comparar")
                continue
            for c, h in g[g["colares"] != 0].groupby("colares"):
                for k in KPIS:
                    if k not in g:
                        continue
                    d, lo, hi, p = (list(welch(base[k], h[k])) + [np.nan] * 4)[:4]
                    cont.append({"experiência": name, "cenário": grupo, "colares": int(c), "indicador": k,
                                 "sem colares": base[k].mean(), "com colares": h[k].mean(), "diferença": d,
                                 "IC95 inf": lo, "IC95 sup": hi, "p (Welch)": p,
                                 "n sem": base[k].notna().sum(), "n com": h[k].notna().sum()})
                for col, lim in [("crash", "principal"), ("crash_alt", "robustez")]:
                    if col not in g:
                        continue
                    a, b = int(base[col].sum()), int(h[col].sum())
                    na, nb = len(base), len(h)
                    p = stats.fisher_exact([[a, na - a], [b, nb - b]])[1]
                    crash.append({"experiência": name, "cenário": grupo, "colares": int(c), "limiar": lim,
                                  "crashes sem": f"{a}/{na}", "crashes com": f"{b}/{nb}",
                                  "prob. sem": a / na, "prob. com": b / nb, "p (Fisher)": p})
    cont, crash = pd.DataFrame(cont), pd.DataFrame(crash)
    out = ROOT / "data" / "processed" / "resultados_cenarios.xlsx"
    with pd.ExcelWriter(out) as xw:
        cont.to_excel(xw, sheet_name="continuos", index=False)
        crash.to_excel(xw, sheet_name="crash", index=False)
    pd.set_option("display.width", 250)
    show = cont[cont["indicador"].isin(["queda_max_dia", "ret_fecho", "spread_dia_choque", "volume_dia_choque",
                                        "min_reserva_dia_choque"])]
    print(show.to_string(index=False, float_format=lambda v: f"{v:.4f}"))
    print("\n" + crash.to_string(index=False, float_format=lambda v: f"{v:.3f}"))
    print(f"\nGuardado em {out}")


if __name__ == "__main__":
    main()
