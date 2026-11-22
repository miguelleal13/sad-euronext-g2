"""Triagem (screening) dos outros parâmetros sem dados que não entraram na ANOVA.

Desenho de Plackett-Burman com 12 combinações: mede o efeito principal de até 11 fatores com só 12 corridas
diferentes. Usamos 10 parâmetros + 1 coluna "fantasma" (nenhum parâmetro): o efeito da coluna fantasma mostra o
tamanho de um efeito que é só ruído, para comparar.
Cada parâmetro em 2 níveis: -50% e +50% do valor do modelo final. Os 6 parâmetros da ANOVA ficam no valor calibrado.
Nota: num Plackett-Burman as interações misturam-se com os efeitos principais; serve para triar (ver se algum
parâmetro mexe muito), não para medir interações.

Uso: python scripts/triagem_desenho.py  -> escreve data/processed/triagem_desenho.csv (para a Margarida)
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
BASE = {   # valores do modelo final (sandbox/matilde/Euronext_real.alp)
    "chartRate": 0.2,        # decisões por minuto de cada trend follower
    "fundRate": 0.2,         # decisões por minuto de cada fundamentalista
    "herdThreshold": 2,      # avisos de vizinhos que põem um trend follower em pânico
    "panicDuration": 10,     # minutos de pânico
    "maWindow": 50,          # memória da média móvel (min)
    "orderLife": 35,         # vida média de uma ordem (min)
    "mmSpread": 0.004,       # spread do criador de mercado
    "mmQty": 2000,           # quantidade cotada pelo criador de mercado
    "activitySigma": 0.05,   # parte aleatória da atividade diária
    "noiseRate": 1.0,        # ordens por minuto de cada noise trader
}
INTEGER = {"herdThreshold", "mmQty"}
PB12 = [1, 1, -1, 1, 1, 1, -1, -1, -1, 1, -1]   # linha geradora do Plackett-Burman de 12 corridas


def main():
    rows = [PB12[-i:] + PB12[:-i] for i in range(11)] + [[-1] * 11]
    names = list(BASE) + ["fantasma"]
    out = []
    for k, signs in enumerate(rows, start=1):
        r = {"scenario": f"triagem{k:02d}"}
        for n, x in zip(names, signs):
            if n != "fantasma":
                v = BASE[n] * (1 + 0.5 * x)
                r[n] = int(round(v)) if n in INTEGER else round(v, 6)
        r.update({f"x_{n}": x for n, x in zip(names, signs)})
        out.append(r)
    d = pd.DataFrame(out)
    path = ROOT / "data" / "processed" / "triagem_desenho.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    d.to_csv(path, sep=";", index=False)
    print(d[["scenario"] + list(BASE)].to_string(index=False))
    print(f"\n{len(d)} combinações. Guardado em {path}")


if __name__ == "__main__":
    main()
