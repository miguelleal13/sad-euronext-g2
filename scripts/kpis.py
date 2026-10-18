"""KPIs dos cenários (proposta: volatilidade, liquidez e recuperação).

Lê model/output/precos.csv e model/output/halts.csv e escreve data/processed/kpis.xlsx com 3 folhas:
  halts  - uma linha por interrupção: volatilidade e spread 2/5/10 min antes e depois, gap do leilão
  runs   - uma linha por corrida: queda máxima, volume, tempo em interrupção, recuperação de metade da queda
  resumo - média e intervalo de confiança de 95% por cenário (label)

Uso: python scripts/kpis.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "model" / "output"
PRICES = OUT_DIR / "precos.csv"
HALTS = OUT_DIR / "halts.csv"
RESULT = ROOT / "data" / "processed" / "kpis.xlsx"
WINDOWS = [2, 5, 10]


def load():
    p = pd.read_csv(PRICES, sep=";", names=["label", "run", "time", "price", "bid", "ask", "volume"])
    p["ret"] = p.groupby("run")["price"].transform(lambda s: np.log(s).diff())
    p["rel_spread"] = (p["ask"] - p["bid"]) / ((p["ask"] + p["bid"]) / 2)
    h = (pd.read_csv(HALTS, sep=";", names=["label", "run", "start", "end", "prePrice", "auctionPrice"])
         if HALTS.exists() and HALTS.stat().st_size > 0 else pd.DataFrame())
    return p, h


def halt_kpis(p, h):
    rows = []
    for _, x in h.iterrows():
        g = p[p["run"] == x["run"]]
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
    ci = 1.96 * std / np.sqrt(n)
    return mean.add_suffix("_media").join(ci.add_suffix("_ic95")).join(n.iloc[:, :1].rename(columns=lambda _: "n_corridas"))


def main():
    p, h = load()
    halts = halt_kpis(p, h) if not h.empty else pd.DataFrame()
    runs = run_kpis(p, h)
    res = summary(runs)
    RESULT.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(RESULT) as xw:
        halts.to_excel(xw, sheet_name="halts", index=False)
        runs.to_excel(xw, sheet_name="runs", index=False)
        res.to_excel(xw, sheet_name="resumo")
    cols = [c for c in res.columns if c.startswith(("queda_maxima", "volume_total", "tempo_em", "n_corridas"))]
    print(res[cols].to_string(float_format=lambda x: f"{x:.4f}"))
    print(f"\nGuardado em {RESULT}")


if __name__ == "__main__":
    main()
