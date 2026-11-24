"""Teste fora da amostra: compara o modelo corrido com os choques de 2025-2026 com os factos do BCP em 2025-2026.

Os factos-alvo do teste são calculados exatamente como os do treino (target_stats.compute), mas no período de teste.
Os critérios de "bate" são os mesmos de docs/FACTOS_ESTILIZADOS.md, aplicados aos valores do BCP no teste.

Uso: python scripts/compare_teste.py PASTA                                   (teste 2025-2026, label "teste")
     python scripts/compare_teste.py PASTA teste2020 2020-01-01 2021-12-31   (outro período: prefixo do label, início, fim)
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from compare_model import FACTS, model_stats  # noqa: E402
from target_stats import compute  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TEST = ("2025-01-01", "2026-12-31")


def main():
    folder = Path(sys.argv[1])
    prefix = sys.argv[2] if len(sys.argv) > 2 else "teste"
    period = (sys.argv[3], sys.argv[4]) if len(sys.argv) > 4 else TEST
    real = compute(*period)
    model, median, n = model_stats(prefix, folder / "precos.csv")
    rows = [{"facto": k, "BCP teste": real[k], "modelo": model[k], "mediana": median[k],
             "bate": "sim" if ok(real[k], model[k]) else "NAO"} for k, ok in FACTS]
    t = pd.DataFrame(rows)
    print(f"Teste {real['periodo']}: {n} corridas\n")
    print(t.to_string(index=False, float_format=lambda v: f"{v:.4f}"))
    print(f"\nFactos que batem: {(t['bate'] == 'sim').sum()} / {len(t)}")
    out = ROOT / "data" / "processed" / (f"{prefix}_{period[0][:4]}_{period[1][:4]}.xlsx" if len(sys.argv) > 4
                                         else "teste_2025_2026.xlsx")
    t.to_excel(out, index=False)
    print(f"Guardado em {out}")


if __name__ == "__main__":
    main()
