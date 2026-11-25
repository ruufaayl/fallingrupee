"""
04_figures.py — publication figures (PNG, 200 dpi) for the report and slide deck, drawn only from
research/outputs/*.json so the figures cannot disagree with the reported numbers.
Run: python scripts/04_figures.py
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

matplotlib.use("Agg")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research" / "outputs"
FIG = OUT / "figures"
FIG.mkdir(parents=True, exist_ok=True)

INK, GRAPHITE, PAPER = "#111214", "#4a4d52", "#f6f2ea"
GOLD, RED, GREEN, BLUE, MUTE = "#b08d3c", "#b23a2e", "#4f7a5a", "#3d5a80", "#9a958c"
plt.rcParams.update({
    "figure.facecolor": PAPER, "axes.facecolor": PAPER, "savefig.facecolor": PAPER,
    "font.family": "DejaVu Serif", "font.size": 10, "axes.edgecolor": GRAPHITE, "axes.labelcolor": INK,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": "#ddd6c8",
    "grid.linewidth": 0.6, "xtick.color": GRAPHITE, "ytick.color": GRAPHITE, "axes.titleweight": "bold",
    "axes.titlesize": 12, "axes.titlelocation": "left", "legend.frameon": False,
})
SRC = "Sources: PBS, IMF CPI & IFS (via DBnomics), World Bank GEM & Pink Sheet, FAO. Author's calculations."


def load(n):
    return json.loads((OUT / f"{n}.json").read_text())


def finish(fig, name, src=SRC):
    fig.text(0.01, 0.005, src, fontsize=7, color=MUTE, ha="left", va="bottom")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(FIG / name, dpi=200)
    plt.close(fig)
    print("  figures/" + name)


ts = load("timeseries")
d = pd.PeriodIndex(ts["dates"], freq="M").to_timestamp()
R = ts["rebased_2015m01"]
S = ts["series"]

# 1 — rebased indices
fig, ax = plt.subplots(figsize=(9, 4.6))
for k, c, lab in (("FOODCPI", RED, "Pakistan food CPI"), ("EXR", GOLD, "PKR per US dollar"),
                  ("TRANSCPI", BLUE, "Transport CPI (energy proxy)"), ("GFOOD", GREEN, "FAO world food price index")):
    ax.plot(d, R[k], color=c, lw=2 if k in ("FOODCPI", "EXR") else 1.4, label=lab)
    off = {"FOODCPI": 7, "TRANSCPI": -7}.get(k, 0)
    ax.annotate(f"{R[k][-1]:.0f}", (d[-1], R[k][-1]), xytext=(4, off), textcoords="offset points", color=c,
                fontsize=9, va="center", fontweight="bold")
ax.axhline(100, color=GRAPHITE, lw=0.8)
ax.set_title("Eleven years in one chart: food prices moved with the rupee, not with world food prices")
ax.set_ylabel("Index, January 2015 = 100")
ax.legend(loc="upper left")
finish(fig, "fig01_rebased_indices.png")

# 2 — inflation vs depreciation
fig, ax = plt.subplots(figsize=(9, 4.6))
ax.fill_between(d, 0, S["FOOD_INF_YOY"], color=RED, alpha=0.18, lw=0)
ax.plot(d, S["FOOD_INF_YOY"], color=RED, lw=2, label="Food inflation, YoY %")
ax.plot(d, S["EXR_DEP_YOY"], color=GOLD, lw=1.6, label="Rupee depreciation vs USD, YoY %")
ax.plot(d, S["GFOOD_YOY"], color=GREEN, lw=1.2, ls="--", label="FAO food price index, YoY %")
ax.axhline(0, color=GRAPHITE, lw=0.8)
i = int(np.nanargmax(S["FOOD_INF_YOY"]))
ax.annotate(f"Peak {S['FOOD_INF_YOY'][i]:.1f}%\n{ts['dates'][i]}", (d[i], S["FOOD_INF_YOY"][i]), xytext=(-90, -10),
            textcoords="offset points", fontsize=8, arrowprops=dict(arrowstyle="-", color=GRAPHITE))
ax.set_title("Food inflation and the exchange rate, year on year")
ax.set_ylabel("Percent")
ax.legend(loc="upper left")
finish(fig, "fig02_inflation_vs_depreciation.png")

# 3 — partial sums
fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
axes[0].plot(d, np.log(S["EXR"]), color=INK, lw=1.8)
axes[0].set_title("ln(PKR per USD)")
axes[1].plot(d, S["LEXR_POS"], color=RED, lw=1.8, label="EXR⁺ cumulative depreciation")
axes[1].plot(d, S["LEXR_NEG"], color=GREEN, lw=1.8, label="EXR⁻ cumulative appreciation")
axes[1].axhline(0, color=GRAPHITE, lw=0.8)
axes[1].set_title("NARDL partial-sum decomposition")
axes[1].legend(loc="upper left", fontsize=8)
finish(fig, "fig03_partial_sums.png")

# 4 — dynamic multipliers
m = load("multipliers")
h = np.array(m["horizon"])
pos, neg = np.array(m["pos"]), np.array(m["neg"])
fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2))
ax = axes[0]
ax.fill_between(h, m["pos_lo95"], m["pos_hi95"], color=RED, alpha=0.12, lw=0)
ax.plot(h, pos, color=RED, lw=2.2, label="1% depreciation")
ax.fill_between(h, -np.array(m["neg_hi95"]), -np.array(m["neg_lo95"]), color=GREEN, alpha=0.12, lw=0)
ax.plot(h, -neg, color=GREEN, lw=2.2, label="1% appreciation")
ax.axhline(0, color=GRAPHITE, lw=0.8)
ax.set_title("Cumulative response of food CPI (%)")
ax.set_xlabel("Months after the exchange-rate change")
ax.legend(loc="lower left")
ax = axes[1]
ax.fill_between(h, m["asym_lo95"], m["asym_hi95"], color=GOLD, alpha=0.22, lw=0, label="95% band")
ax.plot(h, m["asym"], color=INK, lw=2, label="Asymmetry m⁺ − m⁻")
ax.axhline(0, color=GRAPHITE, lw=0.8)
ax.set_title("Asymmetry and its uncertainty")
ax.set_xlabel("Months")
ax.legend(loc="lower left")
finish(fig, "fig04_dynamic_multipliers.png")

# 5/6 — stability
for mid, fname in (("ardl_results", "fig05_stability_ardl.png"), ("nardl_results", "fig06_stability_nardl.png")):
    st = load(mid)["stability"]
    dd = pd.PeriodIndex(st["dates"], freq="M").to_timestamp()
    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.8))
    axes[0].plot(dd, st["cusum"], color=INK, lw=1.8, label="CUSUM")
    axes[0].plot(dd, st["cusum_lo"], color=RED, lw=1, ls="--", label="5% significance")
    axes[0].plot(dd, st["cusum_hi"], color=RED, lw=1, ls="--")
    axes[0].set_title(f"CUSUM — {'stable' if st['cusum_within_bounds'] else 'crosses bound'}")
    axes[0].legend(fontsize=8)
    e = np.array(st["cusumsq_expected"])
    axes[1].plot(dd, st["cusumsq"], color=INK, lw=1.8, label="CUSUM of squares")
    axes[1].plot(dd, e + st["cusumsq_c0"], color=RED, lw=1, ls="--", label="5% significance")
    axes[1].plot(dd, e - st["cusumsq_c0"], color=RED, lw=1, ls="--")
    axes[1].set_title(f"CUSUMSQ — {'stable' if st['cusumsq_within_bounds'] else 'crosses bound'}")
    axes[1].legend(fontsize=8)
    fig.suptitle(load(mid)["label"], x=0.01, ha="left", fontsize=10, color=GRAPHITE)
    finish(fig, fname)

# 7 — actual vs fitted
a = load("nardl_results")["fitted"]
dd = pd.PeriodIndex(a["dates"], freq="M").to_timestamp()
fig, axes = plt.subplots(2, 1, figsize=(9, 5), sharex=True, gridspec_kw={"height_ratios": [2, 1]})
axes[0].plot(dd, a["actual"], color=INK, lw=1.8, label="Actual ln food CPI")
axes[0].plot(dd, a["fitted"], color=GOLD, lw=1.2, ls="--", label="NARDL fitted")
axes[0].legend()
axes[0].set_title("NARDL fit and residuals")
axes[1].bar(dd, a["resid"], width=20, color=[RED if v < 0 else BLUE for v in a["resid"]])
axes[1].axhline(0, color=GRAPHITE, lw=0.8)
finish(fig, "fig07_fit_residuals.png")

# 8 — robustness forest plot
rob = load("robustness")["nardl_specifications"]
rows = [r for r in rob if "long_run" in r]
fig, ax = plt.subplots(figsize=(9, 5.6))
y = np.arange(len(rows))[::-1]
for yy, r in zip(y, rows):
    p = r["long_run"]["LEXR_POS"]
    n = r["long_run"]["LEXR_NEG"]
    ax.scatter(p["coef"], yy + 0.15, color=RED, s=40 if p["p"] < 0.05 else 18,
               edgecolor=RED, facecolor=RED if p["p"] < 0.05 else "none", zorder=3)
    ax.scatter(n["coef"], yy - 0.15, color=GREEN, s=40 if n["p"] < 0.05 else 18,
               edgecolor=GREEN, facecolor=GREEN if n["p"] < 0.05 else "none", zorder=3)
ax.set_yticks(y)
ax.set_yticklabels([r["id"] for r in rows], fontsize=8)
ax.axvline(0, color=GRAPHITE, lw=0.8)
ax.set_xlabel("Long-run elasticity of food CPI")
ax.set_title("Robustness: long-run pass-through (filled = significant at 5%)")
ax.scatter([], [], color=RED, label="Depreciation (L⁺)")
ax.scatter([], [], color=GREEN, label="Appreciation (L⁻)")
ax.legend(loc="lower right")
finish(fig, "fig08_robustness_forest.png")

# 9 — correlation heatmap
c = load("correlations")["first_differences_log"]
M = np.array(c["matrix"])
fig, ax = plt.subplots(figsize=(5.2, 4.4))
im = ax.imshow(M, cmap="RdBu_r", vmin=-1, vmax=1)
lab = ["Δ food CPI", "Δ PKR/USD", "Δ FAO FFPI", "Δ transport"]
ax.set_xticks(range(4))
ax.set_xticklabels(lab, rotation=30, ha="right")
ax.set_yticks(range(4))
ax.set_yticklabels(lab)
ax.grid(False)
for i in range(4):
    for j in range(4):
        ax.text(j, i, f"{M[i, j]:.2f}", ha="center", va="center", fontsize=9,
                color="white" if abs(M[i, j]) > 0.6 else INK)
ax.set_title("Correlations of monthly log changes")
finish(fig, "fig09_correlations.png")
print("done")
