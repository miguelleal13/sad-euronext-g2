"""Limiares de crash tirados dos dados: quanto cai o BCP dentro de um dia normal.

Um crash nos cenários é o preço cair MAIS do que a informação justifica. O choque de informação é -10%,
por isso a pergunta é: quanto mais do que isso? Em vez de escolher um número, usamos o próprio BCP:
  queda dentro do dia = mínimo do dia / fecho do dia anterior - 1     (2023-2024, dados diários)
  limiar principal  = -10% + percentil 99 dessa queda  (o BCP só a ultrapassa em 1% dos dias)
  limiar alternativo = -10% + percentil 95             (teste de robustez: 5% dos dias)
A incerteza do percentil 99 (que depende dos poucos piores dias) é medida por bootstrap em blocos de
10 dias (3000 reamostragens), como nos intervalos dos factos estilizados.

Uso: python scripts/limiar_crash.py          (lê data/raw/bcp_daily.csv)
Escreve data/processed/limiar_crash.xlsx e mostra o comando para o kpis_choque.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
START, END = "2023-01-01", "2024-12-31"
CHOQUE = -0.10
BLOCK, REPS, SEED = 10, 3000, 1


def boot_quantile(x, q):
    rng = np.random.default_rng(SEED)
    n, out = len(x), []
    for _ in range(REPS):
        idx = []
        while len(idx) < n:
            s = rng.integers(0, n - BLOCK + 1)
            idx.extend(range(s, s + BLOCK))
        out.append(np.quantile(x[idx[:n]], q))
    return np.quantile(out, [0.025, 0.975])


def main():
    p = pd.read_csv(ROOT / "data" / "raw" / "bcp_daily.csv", index_col=0, parse_dates=True)
    d = (p["Low"] / p["Close"].shift() - 1).loc[START:END].dropna()   # mesma base (não ajustada)
    x = d.to_numpy()
    q99, q95, q90 = np.quantile(x, 0.01), np.quantile(x, 0.05), np.quantile(x, 0.10)
    lo99, hi99 = boot_quantile(x, 0.01)
    lim99, lim95 = CHOQUE + q99, CHOQUE + q95
    rows = [
        ("dias", len(x)),
        ("queda média dentro do dia", x.mean()),
        ("queda que só 10% dos dias ultrapassam (percentil 90)", q90),
        ("queda que só 5% dos dias ultrapassam (percentil 95)", q95),
        ("queda que só 1% dos dias ultrapassam (percentil 99)", q99),
        ("percentil 99: intervalo de 95% (bootstrap em blocos)", f"{lo99:.2%} a {hi99:.2%}"),
        ("pior queda dentro do dia", x.min()),
        ("dia da pior queda", str(d.idxmin().date())),
        ("choque de informação", CHOQUE),
        ("LIMIAR DE CRASH PRINCIPAL (-10% + percentil 99)", lim99),
        ("limiar principal: intervalo de 95%", f"{CHOQUE + lo99:.2%} a {CHOQUE + hi99:.2%}"),
        ("LIMIAR ALTERNATIVO, robustez (-10% + percentil 95)", lim95),
    ]
    t = pd.DataFrame(rows, columns=["medida", "valor"])
    print(t.to_string(index=False, formatters={"valor": lambda v: f"{v:.2%}" if isinstance(v, float) else str(v)}))
    print(f"\nCrash (principal)   = queda máxima no dia do choque abaixo de {lim99:.1%}")
    print(f"Crash (robustez)    = queda máxima no dia do choque abaixo de {lim95:.1%}")
    print(f"\nPara o kpis_choque.py:  python scripts\\kpis_choque.py PASTA 30600 {lim99:.4f} {lim95:.4f}")
    out = ROOT / "data" / "processed" / "limiar_crash.xlsx"
    t.to_excel(out, index=False)
    print(f"Guardado em {out}")


if __name__ == "__main__":
    main()
