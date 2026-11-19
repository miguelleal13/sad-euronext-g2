"""Desenho da ANOVA: 6 parâmetros sem dados, cada um em 2 níveis (-50% e +50% do valor calibrado).

Desenho fatorial fracionado 2^(6-1) de resolução VI: os fatores A a E fazem um fatorial completo (32 combinações)
e o fator F = A x B x C x D x E. Assim estimam-se todos os efeitos principais e todas as interações de 2 fatores
sem se confundirem entre si.

Os valores calibrados (BASE) são os do modelo final. Se a ronda 9 mudar algum (ex.: nChartists), muda-se aqui.
Cada combinação tem um nome de cenário (anova01 ... anova32) para pôr no parâmetro `scenario` do Main:
o label das corridas começa por esse nome, e é assim que o anova.py as identifica.

Uso: python scripts/anova_desenho.py      -> escreve data/processed/anova_desenho.csv (para a Margarida)
"""
import itertools
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
BASE = {   # valor calibrado de cada parâmetro sem dados
    "nChartists": 13,
    "nFundamentalists": 40,
    "nNoise": 30,
    "noiseSigma": 0.002,
    "fundBand": 0.01,
    "trendThreshold": 0.005,
}
INTEGER = {"nChartists", "nFundamentalists", "nNoise"}


def level(name, x):
    v = BASE[name] * (1 + 0.5 * x)          # x = -1 -> -50%, x = +1 -> +50%
    return int(round(v)) if name in INTEGER else round(v, 6)


def main():
    names = list(BASE)
    rows = []
    for k, signs in enumerate(itertools.product([-1, 1], repeat=5), start=1):
        f = signs[0] * signs[1] * signs[2] * signs[3] * signs[4]       # gerador F = ABCDE
        coded = list(signs) + [f]
        row = {"scenario": f"anova{k:02d}"}
        row.update({n: level(n, x) for n, x in zip(names, coded)})
        row.update({f"x_{n}": x for n, x in zip(names, coded)})
        rows.append(row)
    d = pd.DataFrame(rows)
    out = ROOT / "data" / "processed" / "anova_desenho.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    d.to_csv(out, sep=";", index=False)
    print(d[["scenario"] + names].to_string(index=False))
    print(f"\n{len(d)} combinações. Guardado em {out}")


if __name__ == "__main__":
    main()
