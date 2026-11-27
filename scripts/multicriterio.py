"""Passo 12 do guião: análise multicritério dos conjuntos de colares (regras fixadas em docs/KPIS_CENARIOS.md).

Junta as corridas de várias experiências (folha "runs" de data/processed/kpis_choque_<nome>.xlsx) e, para cada
condição de mercado (tudo o que não é decisão: nº de chartists, manada, parâmetros da sensibilidade), compara
as alternativas de decisão: limiar dinâmico, limiar estático e duração da reserva curta (sem colares incluído).

Critérios (fixados antes das corridas):
  estabilidade = média de: queda máxima no dia do choque (maior = melhor), probabilidade de crash (menor = melhor),
                 tempo até recuperar metade da queda (menor = melhor)
  liquidez     = média de: spread no dia do choque (menor = melhor), volume no dia do choque (maior = melhor),
                 minutos em reserva no dia do choque (menor = melhor)
Cada indicador é normalizado entre 0 e 1 dentro da condição de mercado (1 = melhor alternativa). Pesos
estabilidade/liquidez 50/50, com 70/30 e 30/70 como robustez. Uma alternativa só é recomendada se ficar em
1.º lugar com os três pesos.
Também mostra (marcado como variante, NÃO fixada antes) o resultado sem o tempo de recuperação, porque no
mercado normal esse indicador mede sobretudo o acaso (a queda inclui os -10% da notícia, que são permanentes).

Uso: python scripts/multicriterio.py cenario2_comstartday cenarioLimiar [cenario4 ...]
Escreve data/processed/multicriterio.xlsx
"""
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
COLLARS = {0: (np.nan, np.nan), 1: (0.02, 0.05), 2: (0.03, 0.08), 3: (0.05, 0.10)}
STAB = [("queda_max_dia", +1), ("crash", -1), ("recupera_meia_min", -1)]
LIQ = [("spread_dia_choque", -1), ("volume_dia_choque", +1), ("min_reserva_dia_choque", -1)]
WEIGHTS = [(0.5, 0.5), (0.7, 0.3), (0.3, 0.7)]


def num(label, key):
    m = re.search(rf"_{key}([\d.]+)(?=_|$)", label)
    return float(m.group(1)) if m else np.nan


def market(label):
    """Condição de mercado: o label sem o cenário e sem as variáveis de decisão (c, d, s, h)."""
    s = "_" + re.sub(r"^[^_]+_", "", label)
    return re.sub(r"_(c\d+|d[\d.]+|s[\d.]+|h[\d.]+)(?=_|$)", "", s).lstrip("_")


def alternative(row):
    c = int(row["colares"])
    if c == 0:
        return "sem colares", np.nan, np.nan, np.nan
    d, s = (num(row["label"], "d"), num(row["label"], "s")) if c == 4 else COLLARS[c]
    h = num(row["label"], "h")
    return f"dinâmico {d:.0%} / estático {s:.0%} / reserva {h:g} min", d, s, h


def score(t, crits):
    parts = []
    for k, sign in crits:
        x = t[k]
        rng = x.max() - x.min()
        parts.append(pd.Series(0.5, index=t.index) if rng == 0 else ((x - x.min()) / rng if sign > 0 else (x.max() - x) / rng))
    return pd.concat(parts, axis=1).mean(axis=1)


def analyse(runs, stab):
    rows = []
    for mk, g in runs.groupby("mercado"):
        t = g.groupby("alternativa").agg(
            dinamico=("dinamico", "first"), estatico=("estatico", "first"), reserva=("reserva", "first"),
            n=("run", "nunique"), **{k: (k, "mean") for k, _ in stab + LIQ})
        t["estabilidade"] = score(t, stab)
        t["liquidez"] = score(t, LIQ)
        for ws, wl in WEIGHTS:
            t[f"nota {int(ws*100)}/{int(wl*100)}"] = ws * t["estabilidade"] + wl * t["liquidez"]
            t[f"lugar {int(ws*100)}/{int(wl*100)}"] = t[f"nota {int(ws*100)}/{int(wl*100)}"].rank(ascending=False, method="min").astype(int)
        firsts = {t[f"lugar {int(a*100)}/{int(b*100)}"].idxmin() for a, b in WEIGHTS}
        t["recomendada (1.º com os 3 pesos)"] = [(a in firsts and len(firsts) == 1) for a in t.index]
        t.insert(0, "mercado", mk)
        rows.append(t.reset_index().sort_values("lugar 50/50"))
    return pd.concat(rows, ignore_index=True)


def main():
    names = sys.argv[1:]
    if not names:
        raise SystemExit(__doc__)
    runs = pd.concat([pd.read_excel(ROOT / "data" / "processed" / f"kpis_choque_{n}.xlsx", sheet_name="runs")
                      .assign(experiencia=n) for n in names], ignore_index=True)
    alt = runs.apply(alternative, axis=1, result_type="expand")
    runs[["alternativa", "dinamico", "estatico", "reserva"]] = alt
    runs.loc[runs["colares"] == 0, "reserva"] = np.nan
    runs["mercado"] = runs["label"].map(market)
    # a mesma alternativa pode vir de duas experiências com as mesmas sementes (ex.: c2 do Cenário 2 e d3%/s8% dos
    # Limiares): fica só uma vez, para não contar as mesmas corridas a dobrar
    runs = runs.sort_values("experiencia").drop_duplicates(["mercado", "alternativa", "run"])
    key = runs.groupby(["mercado", "alternativa"])["experiencia"].transform("first")
    runs = runs[runs["experiencia"] == key]
    main_t = analyse(runs, STAB)
    var_t = analyse(runs, [s for s in STAB if s[0] != "recupera_meia_min"])
    out = ROOT / "data" / "processed" / "multicriterio.xlsx"
    with pd.ExcelWriter(out) as xw:
        main_t.to_excel(xw, sheet_name="fixada", index=False)
        var_t.to_excel(xw, sheet_name="variante_sem_recuperacao", index=False)
    pd.set_option("display.width", 250)
    show = ["mercado", "alternativa", "n", "queda_max_dia", "crash", "min_reserva_dia_choque", "estabilidade",
            "liquidez", "lugar 50/50", "lugar 70/30", "lugar 30/70", "recomendada (1.º com os 3 pesos)"]
    for title, t in [("REGRA FIXADA ANTES", main_t), ("VARIANTE (sem o tempo de recuperação; não fixada antes)", var_t)]:
        print(f"\n=== {title} ===")
        print(t[show].to_string(index=False, float_format=lambda v: f"{v:.3f}"))
    print(f"\nGuardado em {out}")


if __name__ == "__main__":
    main()
