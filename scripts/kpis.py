"""KPIs dos cenários (proposta: volatilidade, liquidez e recuperação).

Lê model/Euronext_Main/output/precos.csv e halts.csv e escreve data/processed/kpis.xlsx com 3 folhas:
  halts  - uma linha por interrupção: volatilidade e spread 2/5/10 min antes e depois, gap do leilão
  runs   - uma linha por corrida: queda máxima, volume, tempo em interrupção, recuperação de metade da queda
  resumo - média e intervalo de confiança de 95% por cenário (label)
  esma   - validação (ESMA, 2020): em cada cenário, % de interrupções em que a volatilidade desce
           e o spread alarga depois da reserva (janelas de 2, 5 e 10 min)

Uso: python scripts/kpis.py                 (lê model/Euronext_Main/output)
     python scripts/kpis.py C:/pasta/output  (lê outra pasta, ex.: a da Margarida)
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "model" / "Euronext_Main" / "output"
PRICES = OUT_DIR / "precos.csv"
HALTS = OUT_DIR / "halts.csv"
RESULT = ROOT / "data" / "processed" / "kpis.xlsx"
WINDOWS = [2, 5, 10]


def load():
    p = pd.read_csv(PRICES, sep=";", names=["label", "run", "time", "price", "bid", "ask", "volume"],
                    dtype={"label": str, "run": str})
    p["ret"] = p.groupby("run")["price"].transform(lambda s: np.log(s).diff())
    p["rel_spread"] = (p["ask"] - p["bid"]) / ((p["ask"] + p["bid"]) / 2)
    h = (pd.read_csv(HALTS, sep=";", names=["label", "run", "start", "end", "prePrice", "auctionPrice"],
                     dtype={"label": str, "run": str})
         if HALTS.exists() and HALTS.stat().st_size > 0 else pd.DataFrame())
    return p, h


def halt_kpis(p, h):
    by_run = dict(tuple(p.groupby("run")))      # separa as corridas uma vez só (o ficheiro tem milhões de linhas)
    rows = []
    for _, x in h.iterrows():
        g = by_run.get(x["run"])
        if g is None:
            continue
        row = {"label": x["label"], "run": x["run"], "start": x["start"], "dur": x["end"] - x["start"],
               "gap_leilao": x["auctionPrice"] / x["prePrice"] - 1}
        for w in WINDOWS:
            before = g[(g["time"] >= x["start"] - w) & (g["time"] < x["start"])]
            after = g[(g["time"] > x["end"]) & (g["time"] <= x["end"] + w)]
            row[f"vol_antes_{w}"] = before["ret"].std()
            row[f"vol_depois_{w}"] = after["ret"].std()
            row[f"spread_antes_{w}"] = before["rel_spread"].mean()
            row[f"spread_depois_{w}"] = after["rel_spread"].mean()
        rows.append(row)
    return pd.DataFrame(rows)


def run_kpis(p, h):
    rows = []
    for (label, run), g in p.groupby(["label", "run"]):
        px, t = g["price"].to_numpy(), g["time"].to_numpy()
        peak = np.maximum.accumulate(px)
        dd = 1 - px / peak
        i = int(dd.argmax())
        peak_px, trough_px = peak[i], px[i]
        target = trough_px + 0.5 * (peak_px - trough_px)
        rec = np.where(px[i:] >= target)[0]
        hh = h[h["run"] == run] if not h.empty else h
        rows.append({
            "label": label, "run": run,
            "queda_maxima": dd.max(),
            "volume_total": g["volume"].iloc[-1],
            "n_interrupcoes": len(hh),
            "tempo_em_interrupcao": (hh["end"] - hh["start"]).sum() if len(hh) else 0.0,
            "min_recuperar_metade": t[i + rec[0]] - t[i] if len(rec) and dd.max() > 0 else np.nan,
            "curtose_ret_1min": g["ret"].kurt(),
            "spread_medio": g["rel_spread"].mean(),
        })
    return pd.DataFrame(rows)


def summary(runs):
    num = runs.drop(columns=["run"]).groupby("label")
    mean, std, n = num.mean(), num.std(), num.count()
    t = n.apply(lambda c: stats.t.ppf(0.975, c - 1))   # t de Student (com 10 corridas dá ~2.26 em vez de 1.96)
    ci = t * std / np.sqrt(n)
    return mean.add_suffix("_media").join(ci.add_suffix("_ic95")).join(n.iloc[:, :1].rename(columns=lambda _: "n_corridas"))


def esma(halts):
    """Validação ESMA: depois de uma interrupção a volatilidade deve descer e o spread alargar."""
    rows = []
    for label, g in halts.groupby("label"):
        row = {"label": label, "n_interrupcoes": len(g)}
        for w in WINDOWS:
            v = g.dropna(subset=[f"vol_antes_{w}", f"vol_depois_{w}"])
            s = g.dropna(subset=[f"spread_antes_{w}", f"spread_depois_{w}"])
            row[f"pct_vol_desce_{w}"] = (v[f"vol_depois_{w}"] < v[f"vol_antes_{w}"]).mean() if len(v) else np.nan
            row[f"pct_spread_alarga_{w}"] = (s[f"spread_depois_{w}"] > s[f"spread_antes_{w}"]).mean() if len(s) else np.nan
            row[f"vol_antes_{w}_media"] = v[f"vol_antes_{w}"].mean()
            row[f"vol_depois_{w}_media"] = v[f"vol_depois_{w}"].mean()
            row[f"spread_antes_{w}_media"] = s[f"spread_antes_{w}"].mean()
            row[f"spread_depois_{w}_media"] = s[f"spread_depois_{w}"].mean()
        rows.append(row)
    return pd.DataFrame(rows)


def main():
    p, h = load()
    halts = halt_kpis(p, h) if not h.empty else pd.DataFrame()
    runs = run_kpis(p, h)
    res = summary(runs)
    val = esma(halts) if not halts.empty else pd.DataFrame()
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(RESULT) as xw:
        halts.to_excel(xw, sheet_name="halts", index=False)
        runs.to_excel(xw, sheet_name="runs", index=False)
        res.to_excel(xw, sheet_name="resumo")
        val.to_excel(xw, sheet_name="esma", index=False)
    cols = [c for c in res.columns if c.startswith(("queda_maxima", "volume_total", "tempo_em", "n_corridas"))]
    print(res[cols].to_string(float_format=lambda x: f"{x:.4f}"))
    if not val.empty:
        print("\nValidação ESMA (janela de 5 min): % de interrupções em que a volatilidade desce / o spread alarga")
        print(val[["label", "n_interrupcoes", "pct_vol_desce_5", "pct_spread_alarga_5"]].to_string(index=False, float_format=lambda x: f"{x:.2f}"))
    print(f"\nGuardado em {RESULT}")


if __name__ == "__main__":
    main()
