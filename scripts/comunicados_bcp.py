"""Junta ao data/raw/noticias_bcp.csv os comunicados oficiais do BCP de 2025 e 2026 (para o teste).

O site do BCP bloqueia pedidos automáticos, por isso as páginas são guardadas à mão no browser:
  1. abrir https://ind.millenniumbcp.pt/pt/Institucional/investidores/Pages/Comunicados_2025.aspx
  2. Ctrl+S -> "Página Web, apenas HTML" -> guardar como data/raw/comunicados_bcp_2025.html
  3. o mesmo para 2026 (Comunicados_2026.aspx -> data/raw/comunicados_bcp_2026.html)
Este script lê essas páginas, classifica cada comunicado com as mesmas regras de 2023-2024 e acrescenta-os ao
noticias_bcp.csv (sem duplicar o que já lá estiver). As regras de classificação são as mesmas do treino.

Uso: python scripts/comunicados_bcp.py              (2025 e 2026)
     python scripts/comunicados_bcp.py 2020 2021    (outros anos)
"""
import csv
import html
import io
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
NEWS = RAW / "noticias_bcp.csv"


def tipo(t, c):   # mesmas regras usadas para 2023-2024
    t = t.lower()
    if "resultados consolidados" in t or "plano estratégico" in t:
        return "resultados BCP"
    if "resultados do bank millennium" in t or "millennium bim" in t:
        return "resultados subsidiárias"
    if any(k in t for k in ["provisões", "itens específicos", "moratórias", "plano de recuperação"]):
        return "Polónia (riscos legais CHF)"
    if "rating" in t or "upgrade" in t or "notação" in t:
        return "rating"
    if any(k in t for k in ["chiado", "bank of america", "participação", "alienação de títulos pela",
                            "aquisição de títulos pela"]):
        return "acionistas"
    if "dirigentes" in c.lower() or "remuneração variável" in t:
        return "transações de dirigentes"
    if any(k in t for k in ["emissão", "reembolso", "at1", "tier", "mrel", "obrigações", "requisitos",
                            "reserva de fundos", "fundos de reestruturação"]):
        return "capital e dívida"
    if "dividendo" in t:
        return "dividendos"
    return "governação e outros"


def parse(path, year):
    s = path.read_text(encoding="utf-8", errors="ignore")
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", s, flags=re.S)
    lines = [x.strip() for x in html.unescape(re.sub(r"<[^>]+>", "\n", t)).split("\n") if x.strip()]
    out = []
    for k, x in enumerate(lines):
        if re.fullmatch(rf"\d{{2}}/\d{{2}}/{year}", x) and k + 2 < len(lines):
            d, m, y = x.split("/")
            title, cat = lines[k + 1], lines[k + 2]
            url = f"https://ind.millenniumbcp.pt/pt/Institucional/investidores/Pages/Comunicados_{year}.aspx"
            out.append([f"{y}-{m}-{d}", tipo(title, cat), 1, title.replace(";", ","), url])
    return out


def main():
    rows = []
    years = [int(y) for y in sys.argv[1:]] or [2025, 2026]
    for year in years:
        p = RAW / f"comunicados_bcp_{year}.html"
        if not p.exists():
            print(f"AVISO: falta {p.name} (ver instruções no topo do script)")
            continue
        r = parse(p, year)
        print(f"{year}: {len(r)} comunicados")
        rows += r
    with open(NEWS, encoding="utf-8") as f:
        old = f.read().rstrip("\n").split("\n")
    header, body = old[0], old[1:]
    keys = {(b.split(";")[0], b.split(";")[3]) for b in body}
    new = []
    for r in rows:
        if (r[0], r[3]) not in keys:
            buf = io.StringIO()
            csv.writer(buf, delimiter=";", lineterminator="").writerow(r)
            new.append(buf.getvalue())
    body = sorted(body + new)
    NEWS.write_text(header + "\n" + "\n".join(body) + "\n", encoding="utf-8")
    print(f"{len(new)} comunicados novos acrescentados; total {len(body)} linhas em {NEWS.name}")


if __name__ == "__main__":
    main()
