"""Verificação ao minuto (passo 7 do guião): o modelo contra o BCP nos retornos de 1 minuto.

A calibração é toda com dados diários, mas os colares atuam ao minuto. Este script compara, nos
retornos de 1 minuto:
  - a agitação (desvio-padrão), a autocorrelação de um minuto para o seguinte (negativa = vaivém entre o
    preço de compra e o de venda, "bid-ask bounce"), os saltos grandes (curtose em excesso), a % de minutos sem variação
    e a % de minutos com |retorno| acima de 0.5%;
  - como a agitação se distribui ao longo do dia (variância média por blocos de 30 minutos,
    dividida pela média do dia, para comparar a FORMA e não o nível).

Regras (iguais para os dois lados):
  - retornos só dentro do mesmo dia (sem a noite): no modelo, dentro de cada bloco de 510 minutos;
    no BCP, dentro de cada sessão (08:00-16:30 de Lisboa = 510 minutos);
  - tiram-se os últimos 5 minutos de cada dia e os primeiros 5 da janela (o modelo não tem leilões);
  - minutos sem negócio: no BCP os minutos em falta são preenchidos com o último preço (retorno 0), como
    no modelo, que grava o preço todos os minutos. Os resultados saem também SEM os minutos de retorno 0
    nos dois lados, para mostrar que a conclusão não depende desta escolha.
Nível de preço e tick: o BCP está perto de 1,1 € com tick de 0,0005 € (cerca de 0,045% do preço); o modelo
está perto de 0,35 € com tick de 0,0001 € (cerca de 0,03%). Compara-se em retornos e o script mostra o
tick (inferido dos preços) em % do preço nos dois.
Horário: o Yahoo só tem os minutos do BCP das 09:00 às 16:30 (mais o leilão de fecho às 16:35, que fica de
fora); o modelo tem 08:00-16:30. Compara-se só a janela comum, 09:05-16:25.
Prints isolados impossíveis (saltam mais de 3% e voltam logo) são retirados dos dois lados.

Uso: python scripts/verificacao_minuto.py PASTA_DA_BASE [texto_do_label]
     PASTA_DA_BASE = pasta com o precos.csv da experiência Base
     texto_do_label = só usa as corridas cujo label contém este texto (ex.: o da Base com collarSet = 2)
Lê data/raw/bcp_1min.csv. Escreve data/processed/verificacao_minuto.xlsx
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import ler_precos

ROOT = Path(__file__).resolve().parent.parent
DAY, CUT = 510, 5
OPEN_MIN = 8 * 60                    # 08:00 em Lisboa = minuto 0 do dia do modelo
REAL_FIRST = 60                      # o Yahoo só tem dados do BCP a partir das 09:00 (minuto 60)
LO, HI = REAL_FIRST + CUT, DAY - CUT  # janela comparada nos dois: 09:05 a 16:25
BIG = 0.005                          # |retorno| > 0.5% num minuto


def stats(r, label):
    r = pd.Series(r).dropna()
    nz = r[r != 0]
    return {
        "série": label, "minutos": len(r),
        "desvio-padrão (todos)": r.std(), "curtose em excesso (todos)": r.kurt(),
        "autocorrelação lag 1": r.autocorr(1),
        "% minutos sem variação": 100 * (r == 0).mean(),
        "% minutos com |r| > 0.5%": 100 * (r.abs() > BIG).mean(),
        "desvio-padrão (sem zeros)": nz.std(), "curtose em excesso (sem zeros)": nz.kurt(),
    }


def profile(r, minute):
    """Variância média por bloco de 30 min, dividida pela média do dia (forma ao longo do dia)."""
    df = pd.DataFrame({"r2": np.asarray(r) ** 2, "bloco": (np.asarray(minute) // 30) * 30})
    v = df.groupby("bloco")["r2"].mean()
    return v / v.mean()


def tick_of(prices):
    """Tick inferido dos preços: a diferença positiva mais frequente entre preços distintos."""
    u = np.unique(np.round(np.asarray(prices, dtype=float), 6))
    dd = np.round(np.diff(u), 6)
    dd = dd[dd > 0]
    return float(pd.Series(dd).mode().iloc[0]) if len(dd) else np.nan


def real_returns():
    f = ROOT / "data" / "raw" / "bcp_1min.csv"
    d = pd.read_csv(f)
    tcol = d.columns[0]
    ts = pd.to_datetime(d[tcol], utc=True, errors="coerce")
    d = d.assign(ts=ts.dt.tz_convert("Europe/Lisbon")).dropna(subset=["ts"])
    pcol = next(c for c in ["Close", "close", "Adj Close", "price", "Price"] if c in d.columns)
    d = d[["ts", pcol]].rename(columns={pcol: "price"}).drop_duplicates("ts").sort_values("ts")
    d["dia"] = d["ts"].dt.date
    d["min"] = d["ts"].dt.hour * 60 + d["ts"].dt.minute - OPEN_MIN
    d = d[(d["min"] >= 0) & (d["min"] < DAY)]          # sem o leilão de fecho (16:30-16:35)
    rets, mins, price, spikes, used = [], [], [], 0, []
    for dia, g in d.groupby("dia"):
        g, k = ler_precos._drop_spikes(g.reset_index(drop=True))   # prints isolados impossíveis
        spikes += k
        if ((g["min"] >= LO) & (g["min"] < HI)).sum() < 100:     # dia com muitas falhas (ou incompleto)
            continue
        s = g.set_index("min")["price"].reindex(range(DAY)).ffill()  # minutos sem negócio = último preço
        r = np.log(s).diff()
        keep = (r.index > LO) & (r.index < HI)
        rets.append(r[keep].to_numpy()); mins.append(r.index[keep].to_numpy())
        price.append(g["price"].mean()); used.append(dia)
    if not rets:
        raise SystemExit("Nenhum dia completo no bcp_1min.csv (confirma o ficheiro).")
    return (np.concatenate(rets), np.concatenate(mins), len(used), float(np.mean(price)),
            min(used), max(used), spikes, tick_of(d["price"]))


def model_returns(folder, filtro):
    rets, mins, labels, nruns, price, ticks, mids = [], [], set(), 0, [], [], []
    for label, run, g in ler_precos.runs(Path(folder) / "precos.csv", filtro):
        labels.add(label); nruns += 1
        dia = ((g["time"] - 1) // DAY).astype(int)
        mn = ((g["time"] - 1) % DAY).astype(int)
        for _, idx in g.groupby(dia).groups.items():
            p = g.loc[idx, "price"].to_numpy(); m = mn.loc[idx].to_numpy()
            mid = ((g.loc[idx, "bid"] + g.loc[idx, "ask"]) / 2).to_numpy()
            ok_mid = (g.loc[idx, "ask"] > g.loc[idx, "bid"]).to_numpy()      # sem livro cruzado (reservas)
            r = np.diff(np.log(p)); mm = m[1:]
            rmid = np.diff(np.log(np.where(ok_mid & (mid > 0), mid, np.nan)))
            keep = (mm > LO) & (mm < HI) & (np.diff(m) == 1)
            rets.append(r[keep]); mins.append(mm[keep]); price.append(p.mean()); mids.append(rmid[keep])
        ticks.append(tick_of(g["price"]))
    if not rets:
        raise SystemExit("Nenhuma corrida encontrada (confirma a pasta e o texto do label).")
    return (np.concatenate(rets), np.concatenate(mins), sorted(labels), nruns, float(np.mean(price)),
            float(np.nanmedian(ticks)), np.concatenate(mids))


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    folder, filtro = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else "")
    rr, rm, ndays, preal, t0, t1, nspk, treal = real_returns()
    mr, mm, labels, nruns, pmod, tmod, mmid = model_returns(folder, filtro)
    print(f"BCP: {ndays} dias entre {t0:%d/%m/%Y} e {t1:%d/%m/%Y}; preço médio {preal:.3f} €; "
          f"{nspk} prints isolados impossíveis retirados; janela comparada 09:05-16:25 (o Yahoo não tem 08:00-09:00)")
    print(f"Modelo: {nruns} corridas; labels usados: {', '.join(labels)}; preço médio {pmod:.3f} €")
    if len(labels) > 1 and not filtro:
        print("AVISO: há mais do que um label (ex.: com e sem colares). Indica o texto do label da Base com collarSet = 2.")

    s = pd.DataFrame([stats(rr, "BCP real"), stats(mr, "modelo"),
                      stats(mmid, "modelo (preço médio compra/venda)")]).set_index("série").T
    s["modelo ÷ BCP"] = s["modelo"] / s["BCP real"]
    print("Nota: 'modelo (preço médio compra/venda)' usa (bid+ask)/2 em vez do último negócio, o que tira o vaivém "
          "entre os dois preços; o BCP do Yahoo só tem o preço dos negócios.")
    tick = pd.DataFrame({"BCP real": [treal, 100 * treal / preal], "modelo": [tmod, 100 * tmod / pmod]},
                        index=["tick inferido dos preços (€)", "tick em % do preço"])
    prof = pd.DataFrame({"BCP real": profile(rr, rm), "modelo": profile(mr, mm)})
    prof.index = [f"{OPEN_MIN // 60 + b // 60:02d}:{b % 60:02d}" for b in prof.index]
    pd.set_option("display.width", 200)
    print("\n" + s.to_string(float_format=lambda v: f"{v:.5f}"))
    print("\n" + tick.to_string(float_format=lambda v: f"{v:.4f}"))
    print("\nAgitação ao longo do dia (variância do bloco de 30 min ÷ média do dia; 1 = média):")
    print(prof.to_string(float_format=lambda v: f"{v:.2f}"))
    print(f"\nCorrelação entre as duas formas ao longo do dia: {prof['BCP real'].corr(prof['modelo']):.2f}")
    print("Nota: nos mercados reais a agitação costuma ser maior perto da abertura e do fecho (padrão em U). "
          "O modelo não tem nenhum mecanismo próprio para isso; se a forma não bater, fica como limitação.")

    out = ROOT / "data" / "processed" / "verificacao_minuto.xlsx"
    with pd.ExcelWriter(out) as xw:
        s.to_excel(xw, sheet_name="estatisticas")
        tick.to_excel(xw, sheet_name="tick")
        prof.to_excel(xw, sheet_name="ao_longo_do_dia")
        pd.DataFrame([("dias do BCP", ndays), ("período do BCP", f"{t0:%d/%m/%Y} a {t1:%d/%m/%Y}"),
                      ("corridas do modelo", nruns), ("labels do modelo", ", ".join(labels)),
                      ("minutos cortados no início e no fim de cada dia", CUT)],
                     columns=["medida", "valor"]).to_excel(xw, sheet_name="dados", index=False)
    print(f"\nGuardado em {out}")


if __name__ == "__main__":
    main()
