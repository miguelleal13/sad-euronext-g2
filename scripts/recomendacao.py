"""Tabela de recomendação a partir da grelha do Cenário 4 (choque de -10%, 48 combinações x 30 réplicas).

Para cada nº de chartists (n) e duração da reserva curta (h), compara cada conjunto de colares com o mercado
sem colares: queda evitada (pontos percentuais), teste t de Welch, tempo em reserva e volume.

Lê data/processed/kpis_choque_cenario4b_n13.xlsx e kpis_choque_cenario4_n20a60.xlsx (gerados por kpis_choque.py)
Escreve data/processed/recomendacao.xlsx com 2 folhas:
  diferencas  - todas as comparações (colares vs. sem colares) por n e h
  tabela      - a tabela da recomendação: queda evitada e tempo em reserva para n = 13, 30 e 60
Uso: python scripts/recomendacao.py
"""
from pathlib import Path

import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
PROC = ROOT / "data" / "processed"
FILES = ["kpis_choque_cenario4b_n13.xlsx", "kpis_choque_cenario4_n20a60.xlsx"]
NAMES = {1: "2% / 5%", 2: "3% / 8% (Euronext)", 3: "5% / 10%"}
KPIS = ["queda_max_dia", "queda_30min", "ret_fecho"]


def main():
    runs = pd.concat([pd.read_excel(PROC / f, sheet_name="runs") for f in FILES])
    rows = []
    for (n, h), g in runs.groupby(["n_chartists", "reserva_min"]):
        base = g[g["colares"] == 0]
        for c, nome in NAMES.items():
            x = g[g["colares"] == c]
            row = {"n_chartists": n, "reserva_min": h, "colares": nome, "queda_sem_colares": base["queda_max_dia"].mean()}
            for k in KPIS:   # queda evitada em pontos percentuais (positivo = colares reduzem a queda)
                row[f"{k}_evitada_pp"] = 100 * (x[k].mean() - base[k].mean())
                row[f"{k}_p"] = stats.ttest_ind(x[k], base[k], equal_var=False).pvalue
            row["volume_var_pct"] = 100 * (x["volume_total"].mean() / base["volume_total"].mean() - 1)
            row["n_reservas"] = x["n_reservas"].mean()
            row["tempo_reserva_pct"] = 100 * x["pct_tempo_reserva"].mean()
            rows.append(row)
    d = pd.DataFrame(rows)

    def cell(r):
        star = "*" if r["queda_max_dia_p"] < 0.05 else ""
        return f"{r['queda_max_dia_evitada_pp']:+.1f} pp{star} / {r['tempo_reserva_pct']:.1f}%"

    t = d[d["n_chartists"].isin([13, 30, 60])].copy()
    t["valor"] = t.apply(cell, axis=1)
    tab = t.pivot_table(index=["colares", "reserva_min"], columns="n_chartists", values="valor", aggfunc="first")
    tab.columns = [f"n = {c}" for c in tab.columns]
    with pd.ExcelWriter(PROC / "recomendacao.xlsx") as xw:
        d.to_excel(xw, sheet_name="diferencas", index=False)
        tab.reset_index().to_excel(xw, sheet_name="tabela", index=False)
    print("Queda máxima evitada no dia do choque (pp, * = p < 0.05) / % do tempo em reserva\n")
    print(tab.to_string())
    print(f"\nGuardado em {PROC / 'recomendacao.xlsx'}")


if __name__ == "__main__":
    main()
