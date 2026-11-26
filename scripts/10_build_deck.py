"""
10_build_deck.py — the presentation (PPTX, 16:9), split across three presenters, with the spoken script for every slide in the
speaker notes. Main model: OLS regression on monthly % changes (scripts/14_simple_regression.py). Numbers come from
data/research/simple.json and research/outputs.
Run: python scripts/10_build_deck.py   (PDF: soffice --headless --convert-to pdf presentation/*.pptx --outdir presentation)
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

matplotlib.use("Agg")
ROOT = Path(__file__).resolve().parents[1]
O = ROOT / "research" / "outputs"
FIG = O / "figures"
OUT = ROOT / "presentation"
OUT.mkdir(exist_ok=True)
S = json.loads((ROOT / "data" / "research" / "simple.json").read_text())
R = json.loads((O / "simple_regression.json").read_text())
desc = json.loads((O / "descriptive_statistics.json").read_text())
D = {v["variable"]: v for v in desc["variables"]}
C = {c["code"]: c for c in S["coefficients"]}
A, FIT, DG = S["asymmetry"], S["fit"], R["diagnostics"]
H = {h["id"]: h for h in S["hypotheses"]}
pv = lambda p: "< 0.001" if p < 0.001 else f"{p:.3f}"
SITE = "the-price-of-a-falling-rupee.vercel.app"

INK, PAPER, DIM, GOLD, RED, GREEN, BLUE, AMBER, MUTED, PANEL = (
    RGBColor(0x0B, 0x0C, 0x0E), RGBColor(0xF1, 0xEC, 0xE2), RGBColor(0xC9, 0xC3, 0xB7), RGBColor(0xC9, 0xA2, 0x4A),
    RGBColor(0xE5, 0x48, 0x4D), RGBColor(0x00, 0xA8, 0x88), RGBColor(0x33, 0x8C, 0xED), RGBColor(0xD2, 0x8E, 0x05),
    RGBColor(0x9A, 0x95, 0x8B), RGBColor(0x17, 0x19, 0x1C))
MEMBER = {1: ("MEMBER 1", ""), 2: ("MEMBER 2", ""), 3: ("MEMBER 3", "")}

# ----------------------------------------------------------------------------------------- figures for the slides
FIG.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
BG = "#f6f2ea"


def save(fig, name):
    fig.tight_layout()
    fig.savefig(FIG / name, dpi=200, facecolor=BG)
    plt.close(fig)


def heat(mat, labels, title_, name, size=(6.2, 5.2)):
    m = np.array(mat)
    fig, ax = plt.subplots(figsize=size, facecolor=BG)
    ax.set_facecolor(BG)
    ax.imshow(m, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(labels)), labels, fontsize=9, rotation=0)
    ax.set_yticks(range(len(labels)), labels, fontsize=9)
    for i in range(len(labels)):
        for j in range(len(labels)):
            ax.text(j, i, f"{m[i, j]:.2f}", ha="center", va="center", fontsize=12, fontweight="bold", color="white" if abs(m[i, j]) > 0.6 else "#111")
    ax.set_title(title_, loc="left", fontweight="bold")
    save(fig, name)


heat(R["correlation_levels"]["matrix"], ["Food\nPrices", "Dollar\nRate", "World\nFood", "Fuel &\nTransport"], "Levels (index values)", "slide_corr.png")
heat(R["correlation_changes"]["matrix"], ["Food\nInf.", "Rupee\nDep. (t−1)", "World\nFood (t−1)", "Fuel\n(t−1)", "Food\nInf. (t−1)"],
     "Monthly % changes (regression variables)", "slide_corr_changes.png", size=(7, 5.6))

cols = {"RupeeDep_lag1": "#d28e05", "WorldFoodInf_lag1": "#00a888", "FuelInf_lag1": "#338ced", "FoodInf_lag1": "#a07a2a"}
fig, ax = plt.subplots(figsize=(8, 4.2), facecolor=BG)
ax.set_facecolor(BG)
for i, c in enumerate(S["coefficients"]):
    y = len(S["coefficients"]) - 1 - i
    col = cols[c["code"]]
    ax.plot(c["ci"], [y, y], color=col, lw=4, alpha=0.45, solid_capstyle="round")
    ax.scatter(c["coef"], y, s=180, color=col if c["significant"] else BG, edgecolor=col, lw=2.5, zorder=3)
    ax.text(max(x["ci"][1] for x in S["coefficients"]) + 0.03, y, f"{c['coef']:.2f}  (p = {pv(c['p'])})", va="center", fontsize=11)
ax.axvline(0, color="#555", lw=1)
ax.set_yticks(range(len(S["coefficients"]))[::-1], [c["name"].replace(" (last month)", "\n(last month)") for c in S["coefficients"]], fontsize=10)
ax.set_xlabel("Coefficient with 95% range (crossing 0 = not significant)")
ax.set_xlim(min(x["ci"][0] for x in S["coefficients"]) - 0.05, max(x["ci"][1] for x in S["coefficients"]) + 0.42)
ax.set_title("Filled dot = significant at 5%", loc="left", fontsize=11, color="#555")
save(fig, "slide_coefs.png")

f = R["fitted"]
fig, ax = plt.subplots(figsize=(10, 3.6), facecolor=BG)
ax.set_facecolor(BG)
x = np.arange(len(f["dates"]))
ax.plot(x, f["actual"], color="#222", lw=1.6, label="Actual food inflation")
ax.plot(x, f["fitted"], color="#c9a24a", lw=2, label="Predicted by the regression")
ax.axhline(0, color="#999", lw=0.8)
ax.set_xticks(x[::12], [d[:4] for d in f["dates"][::12]])
ax.set_ylabel("% per month")
ax.legend(frameon=False, loc="upper left")
save(fig, "slide_fit.png")

fig, ax = plt.subplots(figsize=(7, 3.2), facecolor=BG)
ax.set_facecolor(BG)
for y, (nm, cf, ci, p, col) in enumerate((("Rupee rises\n(appreciation)", A["app_coef"], A["app_ci"], A["app_p"], "#00a888"),
                                          ("Rupee falls\n(depreciation)", A["dep_coef"], A["dep_ci"], A["dep_p"], "#e5484d"))):
    ax.plot(ci, [y, y], color=col, lw=5, alpha=0.45, solid_capstyle="round")
    ax.scatter(cf, y, s=220, color=col if p < 0.05 else BG, edgecolor=col, lw=2.5, zorder=3)
    ax.text(ci[1] + 0.03, y, f"{cf:.2f} (p = {pv(p)})", va="center", fontsize=12)
ax.axvline(0, color="#555", lw=1)
ax.set_yticks([0, 1], ["Rupee rises\n(appreciation)", "Rupee falls\n(depreciation)"], fontsize=11)
ax.set_xlim(min(A["app_ci"][0], A["dep_ci"][0]) - 0.05, max(A["app_ci"][1], A["dep_ci"][1]) + 0.45)
ax.set_xlabel("Effect on next month's food inflation (95% range)")
save(fig, "slide_asym.png")

# ----------------------------------------------------------------------------------------- slide helpers
prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]
SLIDE_NO = [0]


def slide(member: int, script: str):
    SLIDE_NO[0] += 1
    s = prs.slides.add_slide(BLANK)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = INK
    s.notes_slide.notes_text_frame.text = f"[{MEMBER[member][0]} speaks]\n\n{script}"
    tag = MEMBER[member][0]
    text(s, 10.3, 0.35, 2.4, 0.35, tag, 10, GOLD, font="Consolas", align=PP_ALIGN.RIGHT)
    text(s, 0.7, 7.02, 10, 0.3, f"The Price of a Falling Rupee · {SITE}", 8, MUTED, font="Consolas")
    text(s, 12.0, 7.02, 0.7, 0.3, str(SLIDE_NO[0]), 9, MUTED, font="Consolas", align=PP_ALIGN.RIGHT)
    return s


def text(s, x, y, w, h, t, size=18, color=PAPER, bold=False, italic=False, font="Georgia", align=PP_ALIGN.LEFT):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    for i, line in enumerate(t if isinstance(t, list) else [t]):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        runs = line if isinstance(line, list) else [(line, color)]
        for txt, col in runs:
            r = p.add_run()
            r.text = txt
            r.font.size, r.font.color.rgb, r.font.bold, r.font.italic, r.font.name = Pt(size), col, bold, italic, font
        p.space_after = Pt(size * 0.5)
    return tb


def title(s, kick, head, size=34):
    text(s, 0.7, 0.35, 9, 0.4, kick.upper(), 11, GOLD, font="Consolas")
    text(s, 0.7, 0.8, 12, 1.0, head, size)


def box(s, x, y, w, h, fill=PANEL, line=None):
    shp = s.shapes.add_shape(1, Inches(x), Inches(y), Inches(w), Inches(h))
    shp.fill.solid()
    shp.fill.fore_color.rgb = fill
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
    return shp


def table(s, x, y, w, rows, col_w, size=12, head_fill=RGBColor(0x2A, 0x2E, 0x34)):
    t = s.shapes.add_table(len(rows), len(rows[0]), Inches(x), Inches(y), Inches(w), Inches(0.4 * len(rows))).table
    for j, cw in enumerate(col_w):
        t.columns[j].width = Inches(cw)
    for i, row in enumerate(rows):
        for j, v in enumerate(row):
            cell = t.cell(i, j)
            cell.fill.solid()
            cell.fill.fore_color.rgb = head_fill if i == 0 else (PANEL if i % 2 else RGBColor(0x11, 0x13, 0x15))
            tf = cell.text_frame
            tf.text = str(v)
            for p in tf.paragraphs:
                for r in p.runs:
                    r.font.size = Pt(size)
                    r.font.name = "Calibri"
                    r.font.bold = i == 0
                    r.font.color.rgb = GOLD if i == 0 else PAPER
    return t


def pic(s, path, x, y, w=None, h=None):
    kw = {}
    if w:
        kw["width"] = Inches(w)
    if h:
        kw["height"] = Inches(h)
    s.shapes.add_picture(str(path), Inches(x), Inches(y), **kw)


def divider(member, what):
    SLIDE_NO[0] += 1
    s = prs.slides.add_slide(BLANK)
    s.background.fill.solid()
    s.background.fill.fore_color.rgb = INK
    text(s, 0.7, 2.6, 12, 0.6, MEMBER[member][0], 16, GOLD, font="Consolas")
    text(s, 0.7, 3.2, 12, 1.2, what, 44)
    s.notes_slide.notes_text_frame.text = f"[Handover to {MEMBER[member][0]}] One sentence: “I will now take you through {what.lower()}.”"



# ========================================================================================= MEMBER 1
s = slide(1, (f"Assalam-o-Alaikum. Our project is called The Price of a Falling Rupee. Between 2015 and 2025, food prices in Pakistan went up "
              f"{D['FOODCPI']['total_change_pct']:.0f} percent. The dollar rate went up {D['EXR']['total_change_pct']:.0f} percent. World food prices "
              f"went up only {D['GFOOD']['total_change_pct']:.0f} percent. So we asked: is the weak rupee driving our food inflation? I will introduce "
              "the problem, our variables, our equation and our hypotheses. Then my teammates will show the data, the tests and the results."))
text(s, 0.7, 1.2, 12, 0.5, "MACROECONOMICS FINAL PROJECT · PAKISTAN · 2015–2025", 12, GOLD, font="Consolas")
text(s, 0.7, 1.8, 12, 2.2, ["THE PRICE OF A", "FALLING RUPEE"], 54, bold=True)
text(s, 0.7, 4.3, 11.5, 0.8, "Does a weaker rupee make food more expensive in Pakistan?", 24, DIM, italic=True)
for i, (v, k, c) in enumerate(((D["FOODCPI"]["total_change_pct"], "Food prices", RED), (D["EXR"]["total_change_pct"], "Dollar rate", AMBER),
                               (D["GFOOD"]["total_change_pct"], "World food prices", GREEN))):
    text(s, 0.7 + 3.9 * i, 5.3, 3.6, 0.8, f"+{v:.0f}%", 40, c, font="Consolas")
    text(s, 0.7 + 3.9 * i, 6.2, 3.6, 0.4, k.upper() + " · 2015→2025", 11, MUTED, font="Consolas")
text(s, 0.7, 6.6, 12, 0.3, "Member 1 · Member 2 · Member 3", 11, MUTED, font="Consolas")

s = slide(1, ("Here is the problem. Food is about one third of what a Pakistani family spends. From 2015 to 2025 food prices nearly tripled, and "
              f"food inflation reached {D['FOOD_INF_YOY']['max']:.1f} percent in May 2023. In the graph, the red line is food inflation and the "
              "yellow line is how fast the rupee lost value. They rise and fall together. The green line — world food prices — follows a different "
              "pattern. That is our problem statement."))
title(s, "Problem statement", "Food nearly tripled in price. Why?")
text(s, 0.7, 1.75, 5.2, 4.6, [S["problem"], "", "Food = 34.58% of the national CPI basket (PBS)."], 16, DIM)
pic(s, FIG / "fig02_inflation_vs_depreciation.png", 6.1, 1.7, w=6.6)

s = slide(1, ("Our research question: does a weaker rupee, along with world food prices and fuel costs, raise food inflation in Pakistan — and "
              "does a stronger rupee bring it back down? People say prices go up like a rocket and come down like a feather; we test that too."))
title(s, "Research question", "What we wanted to find out")
box(s, 0.7, 2.0, 11.9, 2.4, line=GOLD)
text(s, 1.1, 2.3, 11.2, 2.0, S["question"], 28)
text(s, 0.7, 4.8, 12, 1.2, ["Part 1 → Which factors raise food inflation, and by how much?", "Part 2 → Does a rising rupee have the opposite effect of a falling rupee?"], 18, DIM)

s = slide(1, ("These are our variables. The dependent variable is Food Inflation — the monthly percentage change in Pakistan's food price "
              "index. We have four independent variables. X1, Rupee Depreciation: the monthly change in rupees per dollar — positive means the "
              "rupee got weaker. X2, World Food Inflation from the FAO. X3, Fuel and Transport Inflation from the transport price index. And X4, "
              "last month's food inflation — this is the autoregressive term, because price rises tend to continue. All the X variables are taken "
              "from the previous month, because prices need time to react."))
title(s, "Variables", "Dependent and independent variables")
colors = [RED, AMBER, GREEN, BLUE, GOLD]
for i, v in enumerate(S["variables"]):
    x = 0.7 + i * 2.43
    box(s, x, 1.9, 2.28, 4.7)
    box(s, x, 1.9, 2.28, 0.08, fill=colors[i])
    text(s, x + 0.15, 2.1, 2.0, 0.4, v["role"].upper(), 9, MUTED, font="Consolas")
    text(s, x + 0.15, 2.5, 2.0, 0.6, v["symbol"], 28, colors[i], font="Consolas")
    text(s, x + 0.15, 3.2, 2.0, 0.9, v["name"], 15, bold=True)
    text(s, x + 0.15, 4.2, 2.0, 1.6, v["measure"], 11, DIM)
    text(s, x + 0.15, 5.85, 2.0, 0.7, v["source"], 9, MUTED)

s = slide(1, ("Our data is monthly, from January 2015 to December 2025 — 132 months, no missing values. It comes from the Pakistan Bureau of "
              "Statistics, the World Bank and the FAO. We combined everything into one Excel file. The 'Regression Data' sheet has the exact "
              "monthly percentage changes we used, so anyone can re-run our regression."))
title(s, "Data", "132 months · 4 official sources", 32)
ts = json.loads((O / "timeseries.json").read_text())["series"]
rows = [["Series", "Source", "Unit", "Jan 2015", "Dec 2025"]]
for nm, k, src, unit in (("Food Prices", "FOODCPI", "Pakistan Bureau of Statistics", "Index (2015-16 = 100)"),
                         ("Dollar Rate", "EXR", "World Bank (GEM)", "Rupees per US dollar"),
                         ("World Food Prices", "GFOOD", "FAO", "Index (2014–16 = 100)"),
                         ("Fuel & Transport", "TRANSCPI", "Pakistan Bureau of Statistics", "Index (2015-16 = 100)")):
    rows.append([nm, src, unit, f"{ts[k][0]:.2f}", f"{ts[k][-1]:.2f}"])
table(s, 0.7, 1.9, 11.9, rows, [2.4, 3.4, 3.5, 1.3, 1.3], size=13)
text(s, 0.7, 4.4, 12, 1.6, ["Monthly · January 2015 – December 2025 · N = 132 · no missing values",
                            "Variables in the model = monthly % change of each series (X’s from the previous month).",
                            "Excel: Falling_Rupee_Dataset.xlsx → Combined Data · Regression Data · Sources · Summary Statistics"], 15, DIM)

s = slide(1, ("This is our one equation — a standard regression. Food inflation on the left. On the right: rupee depreciation, world food "
              "inflation, fuel inflation and last month's food inflation, each with a beta. Each beta tells us how many percentage points food "
              "inflation moves when that variable moves by one point. For example, if beta-one were 0.5, a 1 percent weaker rupee would mean food "
              "prices 0.5 percent higher the next month. We estimate it with ordinary least squares, OLS."))
title(s, "The model", "One equation (OLS regression)")
box(s, 0.7, 2.0, 11.9, 2.6, line=GOLD)
text(s, 1.0, 2.25, 11.3, 2.3, [[("Food Inflation", RED), (" = β₀ + β₁ ", PAPER), ("Rupee Depreciation", AMBER), (" + β₂ ", PAPER), ("World Food Inflation", GREEN)],
                               [(" + β₃ ", PAPER), ("Fuel & Transport Inflation", BLUE), (" + β₄ ", PAPER), ("Last Month’s Food Inflation", GOLD), (" + error", PAPER)]],
     26, align=PP_ALIGN.CENTER)
text(s, 0.7, 5.0, 12, 1.5, ["All variables are monthly % changes; the X’s are from the previous month.",
                            "β₄ is the autoregressive (AR) term: food inflation depends on its own past value."], 16, DIM)

s = slide(1, ("These are our six hypotheses. H-zero always says 'no effect'; H-one says 'there is an effect'. H1 to H4 test each beta with a "
              "t-test. H5 tests the whole model with the F-test. H6 asks whether a rising rupee has the same effect as a falling rupee. Our rule: if "
              "the p-value is below 0.05, we reject H-zero. Now my teammate will show the data and the tests."))
title(s, "Hypotheses", "H₀ (no effect) vs H₁ (effect)")
rows = [["", "H₀", "H₁", "Test"]] + [[h["id"], h["h0"], h["h1"], h["test"]] for h in S["hypotheses"]]
table(s, 0.7, 1.7, 11.9, rows, [0.6, 4.7, 4.0, 2.6], size=11)
text(s, 0.7, 6.4, 12, 0.5, "Decision rule: p-value < 0.05 → reject H₀ (significant at 5%).", 15, GOLD)

# ========================================================================================= MEMBER 2
divider(2, "The data and the tests before the regression")
s = slide(2, ("Thank you. This graph sets all four series to 100 in January 2015. Food prices — red — end near "
              f"{100 + D['FOODCPI']['total_change_pct']:.0f}, the dollar rate — yellow — near {100 + D['EXR']['total_change_pct']:.0f}, but world food "
              f"prices — green — only near {100 + D['GFOOD']['total_change_pct']:.0f}. Food prices climb with the rupee, especially in 2019 and 2022–23."))
title(s, "Graph", "All four series, January 2015 = 100")
pic(s, FIG / "fig01_rebased_indices.png", 0.9, 1.6, w=11.4)

s = slide(2, ("These are the descriptive statistics: average, middle value, spread, lowest and highest. Food prices grew about "
              f"{D['FOODCPI']['cagr_pct']:.1f} percent a year, the dollar rate {D['EXR']['cagr_pct']:.1f} percent, world food prices only "
              f"{D['GFOOD']['cagr_pct']:.1f} percent. On average, food prices rose about {D['FOOD_INF_MOM']['mean']:.2f} percent every month."))
title(s, "Descriptive statistics", "Summary of the data (N = 132)")
rows = [["Variable", "Mean", "Median", "Std. dev.", "Min", "Max", "Growth / year"]]
for k, nm in (("FOODCPI", "Food Prices"), ("EXR", "Dollar Rate"), ("GFOOD", "World Food Prices"), ("TRANSCPI", "Fuel & Transport")):
    d = D[k]
    rows.append([nm, f"{d['mean']:.1f}", f"{d['median']:.1f}", f"{d['sd']:.1f}", f"{d['min']:.1f}", f"{d['max']:.1f}", f"{d['cagr_pct']:.1f}%"])
mm = D["FOOD_INF_MOM"]
rows.append(["Food Inflation (% per month)", f"{mm['mean']:.2f}", f"{mm['median']:.2f}", f"{mm['sd']:.2f}", f"{mm['min']:.2f}", f"{mm['max']:.2f}", "—"])
table(s, 0.7, 1.9, 11.9, rows, [3.4, 1.4, 1.4, 1.4, 1.4, 1.4, 1.5], size=14)

cl, cc = R["correlation_levels"]["matrix"], R["correlation_changes"]["matrix"]
s = slide(2, (f"The correlation matrix shows how closely variables move together, from minus one to plus one. On the left, in levels, food "
              f"prices and the dollar rate have r = {cl[0][1]:.2f} — almost perfect. But anything that rises over time looks correlated, so levels can "
              f"mislead. On the right are the monthly changes we actually use: food inflation and last month's rupee depreciation have r = "
              f"{cc[0][1]:.2f}. Positive, and realistic for monthly data."))
title(s, "Correlation", "Which variables move together?")
pic(s, FIG / "slide_corr.png", 0.6, 1.6, h=4.9)
pic(s, FIG / "slide_corr_changes.png", 6.6, 1.5, h=5.1)

s = slide(2, ("Next, stationarity, with the ADF unit root test. H-zero says the series is non-stationary — it keeps trending. In levels all "
              "p-values are above 0.05, so all four are non-stationary. That is a problem: regressing trending data can give fake results. So we use "
              "monthly percentage changes. For the changes, all p-values are below 0.001 — stationary. Our regression is safe."))
title(s, "Stationarity · ADF unit root test", "Stationary or non-stationary?")
rows = [["Variable", "Level: p-value", "Level", "% change: p-value", "% change"]] + [
    [u["name"], f"{u['level_p']:.3f}", u["level_result"], pv(u["change_p"]), u["change_result"]] for u in S["stationarity"]]
table(s, 0.7, 1.9, 11.9, rows, [3.4, 2.0, 2.2, 2.2, 2.1], size=14)
text(s, 0.7, 4.4, 12, 1.6, ["H₀: the series is non-stationary (has a unit root). Reject if p < 0.05.",
                            "Levels → non-stationary · monthly % changes → stationary → the regression uses % changes."], 16, DIM)

vmax = max(v["vif"] for v in S["vif"])
s = slide(2, (f"Last check before the regression: multicollinearity. If the X variables are too similar, the regression cannot separate their "
              f"effects. We measure it with the Variance Inflation Factor. A VIF above 10 is a problem. Our highest VIF is {vmax:.2f} — close to 1 — "
              "so there is no multicollinearity. Now my teammate will present the regression results."))
title(s, "Multicollinearity · VIF", "Are the X variables too similar?")
rows = [["Independent variable", "VIF", "Tolerance (1/VIF)"]] + [[v["name"], f"{v['vif']:.2f}", f"{v['tolerance']:.3f}"] for v in S["vif"]]
table(s, 0.7, 1.9, 8.5, rows, [5.0, 1.5, 2.0], size=15)
box(s, 9.6, 1.9, 3.0, 2.4, line=GOLD)
text(s, 9.8, 2.05, 2.7, 2.2, ["Rule", "VIF > 10 → problem", f"Ours ≤ {vmax:.2f}", "→ no multicollinearity"], 16)

# ========================================================================================= MEMBER 3
divider(3, "The regression results and diagnostic tests")
rd = C["RupeeDep_lag1"]
s = slide(3, ("Thank you. Here is the regression output. The rupee depreciation coefficient is "
              f"{rd['coef']:.2f} with a p-value of {pv(rd['p'])}: if the rupee falls 1 percent, food prices rise about {rd['coef']:.2f} percent the "
              f"next month. Last month's food inflation has {C['FoodInf_lag1']['coef']:.2f}, p = {pv(C['FoodInf_lag1']['p'])}: food inflation carries "
              f"over. World food inflation and fuel inflation are not significant. The F-test p-value is {pv(FIT['F_p'])}, so the model as a whole is "
              f"significant. R-squared is {FIT['r2']:.2f}: monthly food prices also jump with weather and harvests, so a low R-squared is normal here."))
title(s, "Result · OLS regression", "The estimated equation")
box(s, 0.7, 1.7, 11.9, 1.5, line=GOLD)
sg = lambda v: f" + {v:.2f} " if v >= 0 else f" − {abs(v):.2f} "
text(s, 0.9, 1.85, 11.5, 1.3, [[("Food Inflation", RED), (f" = {S['constant']:.2f}" + sg(rd['coef']), PAPER), ("Rupee Dep.", AMBER),
                                (sg(C['WorldFoodInf_lag1']['coef']), PAPER), ("World Food Inf.", GREEN), (sg(C['FuelInf_lag1']['coef']), PAPER),
                                ("Fuel Inf.", BLUE), (sg(C['FoodInf_lag1']['coef']), PAPER), ("Last Month's Food Inf.", GOLD)]], 22, align=PP_ALIGN.CENTER)
rows = [["Variable", "Coefficient", "Std. error", "t", "p-value", "Significant?"]] + [
    [c["name"], f"{c['coef']:.3f}", f"{c['se']:.3f}", f"{c['t']:.2f}", pv(c["p"]), "Yes" if c["significant"] else "No"] for c in S["coefficients"]]
table(s, 0.7, 3.45, 11.9, rows, [4.4, 1.6, 1.5, 1.1, 1.5, 1.8], size=13)
text(s, 0.7, 6.15, 12, 0.6, f"N = {S['n']} · R² = {FIT['r2']:.3f} · adj. R² = {FIT['adj_r2']:.3f} · F({FIT['df'][0]}, {FIT['df'][1]}) = {FIT['F']:.2f}, p = {pv(FIT['F_p'])}", 15, GOLD, font="Consolas")

s = slide(3, ("This chart shows each coefficient with its 95 percent range. If the range crosses the zero line, the effect is not significant. "
              "Rupee depreciation and last month's food inflation are clearly above zero. World food and fuel ranges cross zero."))
title(s, "Result", "How big is each effect?")
pic(s, FIG / "slide_coefs.png", 0.7, 1.7, h=4.0)
text(s, 9.0, 1.8, 3.8, 4.5, [c["plain"] for c in S["coefficients"]], 12, DIM)

s = slide(3, ("Here is the decision for every hypothesis. H1, rupee: p below 0.05, reject H-zero — a weaker rupee raises food inflation. H2, world "
              "food, and H3, fuel: p above 0.05, we fail to reject — no clear monthly effect. H4, autoregression: reject — food inflation persists. "
              "H5, the F-test: reject — the model is significant. H6, asymmetry: we fail to reject — explained on the next slides."))
title(s, "Hypothesis results", "Decision for every hypothesis")
rows = [["", "Question", "Result", "Decision"]] + [[h["id"], h["question"], h["result"], h["decision"]] for h in S["hypotheses"]]
table(s, 0.7, 1.7, 11.9, rows, [0.6, 4.1, 5.0, 2.2], size=11)

s = slide(3, ("Before trusting the result, we checked the assumptions. Autocorrelation: Durbin-Watson is "
              f"{DG['durbin_watson']:.2f}, close to the ideal 2, and the Breusch-Godfrey test p is {pv(DG['bg12']['p'])} — no autocorrelation. "
              f"Heteroskedasticity: Breusch-Pagan p = {pv(DG['bp']['p'])} and White p = {pv(DG['white']['p'])} — constant variance. Normality: "
              f"Jarque-Bera p = {pv(DG['jb']['p'])} — errors are normal. Specification: Ramsey RESET p = {pv(DG['reset']['p'])} — correct form. "
              "Every diagnostic test passes, so our results can be trusted."))
title(s, "Diagnostic tests", "Can we trust the regression?")
rows = [["Problem checked", "Test", "H₀", "Result", "Decision"],
        ["Autocorrelation", "Durbin-Watson", "No autocorrelation", f"DW = {DG['durbin_watson']:.2f} (≈ 2)", "✓ No problem"],
        ["Autocorrelation", "Breusch-Godfrey LM (12 lags)", "No autocorrelation", f"p = {pv(DG['bg12']['p'])}", "✓ Fail to reject H₀"],
        ["Heteroskedasticity", "Breusch-Pagan-Godfrey", "Constant variance", f"p = {pv(DG['bp']['p'])}", "✓ Fail to reject H₀"],
        ["Heteroskedasticity", "White", "Constant variance", f"p = {pv(DG['white']['p'])}", "✓ Fail to reject H₀"],
        ["Normality", "Jarque-Bera", "Errors are normal", f"p = {pv(DG['jb']['p'])}", "✓ Fail to reject H₀"],
        ["Specification", "Ramsey RESET", "Correct functional form", f"p = {pv(DG['reset']['p'])}", "✓ Fail to reject H₀"],
        ["Multicollinearity", "VIF", "—", f"max VIF = {vmax:.2f}", "✓ Below 10"]]
table(s, 0.7, 1.7, 11.9, rows, [2.3, 3.0, 2.4, 2.2, 2.0], size=12)
pic(s, FIG / "slide_fit.png", 2.6, 5.15, h=1.75)

s = slide(3, ("Now the second part of our question. We split last month's rupee change into months when the rupee fell and months when it rose. "
              f"When the rupee falls, the effect is {A['dep_coef']:.2f}, p = {pv(A['dep_p'])} — significant. When the rupee rises, the effect is "
              f"{A['app_coef']:.2f}, p = {pv(A['app_p'])} — basically zero. So a falling rupee raises food prices, but a rising rupee does not bring them "
              f"down. However, the Wald F-test of equal effects has p = {pv(A['p'])}, so we cannot statistically prove the difference — the rupee rose "
              f"in only {A['app_months']} months."))
title(s, "Asymmetry · Wald F-test", "Rupee falls vs rupee rises")
pic(s, FIG / "slide_asym.png", 0.7, 1.7, w=7.4)
text(s, 8.4, 1.8, 4.4, 4.6, [f"Rupee falls: {A['dep_coef']:.2f} (p = {pv(A['dep_p'])}) ✓", f"Rupee rises: {A['app_coef']:.2f} (p = {pv(A['app_p'])}) ✗",
                             f"Same effect? F = {A['F']:.2f}, p = {pv(A['p'])}", "→ Fail to reject H₀", "",
                             "Prices go up when the rupee falls; no evidence they come down when it rises."], 15, DIM)

s = slide(3, ("To conclude. One: a weaker rupee raises food inflation the next month — our main finding. Two: food inflation has momentum. "
              "Three: world food and fuel prices showed no clear monthly effect. Four: a rising rupee did not bring food prices down. And the model "
              "passes every diagnostic test. For policy: keep the rupee stable, treat a falling rupee as an early warning, and help poor families "
              "directly. Thank you — we are happy to take questions."))
title(s, "Conclusion", "What we found")
text(s, 0.7, 1.7, 12, 4.2, [f"{i + 1}.  {a}" for i, a in enumerate(S["answer"])], 15)
text(s, 0.7, 6.0, 12, 0.9, ["Policy: keep the rupee stable · a falling rupee is an early warning for food inflation · help poor families directly."], 14, GOLD)

s = slide(3, "Close here and invite questions. All three members stand together for the Q&A.")
text(s, 0.7, 2.2, 12, 2, ["A currency can recover in a season.", "The price of bread remembers."], 44, align=PP_ALIGN.CENTER)
text(s, 0.7, 4.7, 12, 0.6, SITE, 16, GOLD, font="Consolas", align=PP_ALIGN.CENTER)
text(s, 0.7, 5.4, 12, 0.6, "Thank you · Questions", 22, MUTED, align=PP_ALIGN.CENTER)

out = OUT / "The_Price_of_a_Falling_Rupee_Deck.pptx"
prs.save(out)
print("wrote", out.relative_to(ROOT), len(prs.slides), "slides")
