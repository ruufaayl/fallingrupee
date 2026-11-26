"""
10_build_deck.py — the presentation (PPTX, 16:9), split across three presenters, with the spoken script for every slide in the
speaker notes. All numbers come from data/research/simple.json and research/outputs.
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
desc = json.loads((O / "descriptive_statistics.json").read_text())
corr = json.loads((O / "correlations.json").read_text())
ardl = json.loads((O / "ardl_results.json").read_text())
D = {v["variable"]: v for v in desc["variables"]}
C = {c["code"]: c for c in S["coefficients"]}
A = S["asymmetry"]
H = {h["id"]: h for h in S["hypotheses"]}
T = {t["name"]: t for t in S["tests"]}
ECM = ardl["ecm_regression"]
SITE = "the-price-of-a-falling-rupee.vercel.app"

INK, PAPER, DIM, GOLD, RED, GREEN, BLUE, AMBER, MUTED, PANEL = (
    RGBColor(0x0B, 0x0C, 0x0E), RGBColor(0xF1, 0xEC, 0xE2), RGBColor(0xC9, 0xC3, 0xB7), RGBColor(0xC9, 0xA2, 0x4A),
    RGBColor(0xE5, 0x48, 0x4D), RGBColor(0x00, 0xA8, 0x88), RGBColor(0x33, 0x8C, 0xED), RGBColor(0xD2, 0x8E, 0x05),
    RGBColor(0x9A, 0x95, 0x8B), RGBColor(0x17, 0x19, 0x1C))
MEMBER = {1: ("MEMBER 1", "Problem · Variables · Equation · Hypotheses"), 2: ("MEMBER 2", "Data · Graphs · Tests"),
          3: ("MEMBER 3", "Results · Diagnostics · Conclusion")}

# ----------------------------------------------------------------------------------------- extra simple figures
FIG.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11, "axes.spines.top": False, "axes.spines.right": False})


def save(fig, name):
    fig.tight_layout()
    fig.savefig(FIG / name, dpi=200, facecolor="#f6f2ea")
    plt.close(fig)


m = np.array(corr["levels_log"]["matrix"])
lab = ["Food Prices", "Dollar Rate", "World Food\nPrices", "Fuel &\nTransport"]
fig, ax = plt.subplots(figsize=(6.2, 5.2), facecolor="#f6f2ea")
ax.set_facecolor("#f6f2ea")
im = ax.imshow(m, cmap="RdBu_r", vmin=-1, vmax=1)
ax.set_xticks(range(4), lab, fontsize=10)
ax.set_yticks(range(4), lab, fontsize=10)
for i in range(4):
    for j in range(4):
        ax.text(j, i, f"{m[i, j]:.2f}", ha="center", va="center", fontsize=13, fontweight="bold", color="white" if abs(m[i, j]) > 0.6 else "#111")
ax.set_title("Correlation matrix (log levels)", loc="left", fontweight="bold")
save(fig, "slide_corr.png")

fig, ax = plt.subplots(figsize=(8, 3.8), facecolor="#f6f2ea")
ax.set_facecolor("#f6f2ea")
cols = ["#d28e05", "#00a888", "#338ced"]
for i, c in enumerate(S["coefficients"]):
    y = 2 - i
    ax.plot(c["ci"], [y, y], color=cols[i], lw=4, alpha=0.45, solid_capstyle="round")
    ax.scatter(c["coef"], y, s=180, color=cols[i] if c["significant"] else "#f6f2ea", edgecolor=cols[i], lw=2.5, zorder=3)
    ax.text(c["ci"][1] + 0.03, y, f"{c['coef']:.2f}  (p = {c['p']:.3f})", va="center", fontsize=11)
ax.axvline(0, color="#555", lw=1)
ax.set_yticks([2, 1, 0], [c["name"] for c in S["coefficients"]], fontsize=12)
ax.set_xlabel("Long-run effect on food prices (elasticity) with 95% range")
ax.set_xlim(min(-0.4, S["coefficients"][2]["ci"][0] - 0.1), max(c["ci"][1] for c in S["coefficients"]) + 0.55)
ax.set_title("Filled dot = significant at 5%", loc="left", fontsize=11, color="#555")
save(fig, "slide_coefs.png")

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
s = slide(1, (f"Assalam-o-Alaikum. Our project is called The Price of a Falling Rupee. In one line: between 2015 and 2025, food prices in "
              f"Pakistan went up {D['FOODCPI']['total_change_pct']:.0f} percent. The dollar rate went up {D['EXR']['total_change_pct']:.0f} percent. "
              f"But world food prices went up only {D['GFOOD']['total_change_pct']:.0f} percent. So we asked: is the weak rupee the reason our food "
              "became so expensive? I will introduce the problem, our variables, our equation and our hypotheses. Then my teammates will show "
              "the data, the tests and the results."))
text(s, 0.7, 1.2, 12, 0.5, "MACROECONOMICS FINAL PROJECT · PAKISTAN · 2015–2025", 12, GOLD, font="Consolas")
text(s, 0.7, 1.8, 12, 2.2, ["THE PRICE OF A", "FALLING RUPEE"], 54, bold=True)
text(s, 0.7, 4.3, 11.5, 0.8, "Does a weaker rupee make food more expensive in Pakistan?", 24, DIM, italic=True)
for i, (v, k, c) in enumerate(((D["FOODCPI"]["total_change_pct"], "Food prices", RED), (D["EXR"]["total_change_pct"], "Dollar rate", AMBER),
                               (D["GFOOD"]["total_change_pct"], "World food prices", GREEN))):
    text(s, 0.7 + 3.9 * i, 5.3, 3.6, 0.8, f"+{v:.0f}%", 40, c, font="Consolas")
    text(s, 0.7 + 3.9 * i, 6.2, 3.6, 0.4, k.upper() + " · 2015→2025", 11, MUTED, font="Consolas")
text(s, 0.7, 6.6, 12, 0.3, "Member 1 · Member 2 · Member 3", 11, MUTED, font="Consolas")

s = slide(1, ("Here is the problem. Food is about one third of what a normal Pakistani family spends. From 2015 to 2025 food prices nearly "
              f"tripled. Food inflation hit {max(x for x in [D['FOOD_INF_YOY']['max']]):.1f} percent in May 2023 — the highest in our sample. "
              "At the same time the rupee became much weaker against the dollar. Look at the graph: the red line is food inflation, the yellow "
              "line is how fast the rupee was losing value. They rise and fall together. The green line — world food prices — does not follow "
              "the same pattern. That is our problem statement."))
title(s, "Problem statement", "Food nearly tripled in price. Why?")
text(s, 0.7, 1.75, 5.2, 4.6, [S["problem"], "", "Food = 34.58% of the national CPI basket (PBS)."], 16, DIM)
pic(s, FIG / "fig02_inflation_vs_depreciation.png", 6.1, 1.7, w=6.6)

s = slide(1, ("Our research question has two parts. First: do a weaker rupee, world food prices and fuel costs raise food prices in Pakistan? "
              "Second: when the rupee gets stronger again, do food prices come back down? The second part is important because people often "
              "say prices go up like a rocket and come down like a feather."))
title(s, "Research question", "What we wanted to find out")
box(s, 0.7, 2.0, 11.9, 2.4, line=GOLD)
text(s, 1.1, 2.3, 11.2, 2.0, S["question"], 28)
text(s, 0.7, 4.8, 12, 1.2, ["Part 1 → Which factors raise food prices, and by how much?", "Part 2 → Is the effect the same when the rupee rises as when it falls?"], 18, DIM)

s = slide(1, ("These are our variables. The dependent variable — the thing we are explaining — is Food Prices, Pakistan's national food "
              "price index from the Pakistan Bureau of Statistics. We have three independent variables, the possible causes. X1 is the Dollar "
              "Rate — how many rupees you need to buy one dollar; a higher number means a weaker rupee. X2 is World Food Prices, the FAO index "
              "of world prices of wheat, oil, sugar, dairy and meat. X3 is Fuel and Transport Costs — the transport price index, which is mostly "
              "petrol and diesel."))
title(s, "Variables", "Dependent and independent variables")
cols = [RED, AMBER, GREEN, BLUE]
for i, v in enumerate(S["variables"]):
    x = 0.7 + i * 3.05
    box(s, x, 1.9, 2.85, 4.6)
    box(s, x, 1.9, 2.85, 0.08, fill=cols[i])
    text(s, x + 0.2, 2.1, 2.5, 0.4, v["role"].upper(), 10, MUTED, font="Consolas")
    text(s, x + 0.2, 2.5, 2.5, 0.6, v["symbol"], 30, cols[i], font="Consolas")
    text(s, x + 0.2, 3.2, 2.5, 0.8, v["name"], 17, bold=True)
    text(s, x + 0.2, 4.15, 2.5, 1.6, v["measure"], 12, DIM)
    text(s, x + 0.2, 5.7, 2.5, 0.7, "Source: " + v["source"], 10, MUTED)

s = slide(1, ("Our data is monthly, from January 2015 to December 2025 — that is 132 months, with no missing values. Every variable comes "
              "from an official source: the Pakistan Bureau of Statistics, the World Bank and the FAO. We combined all of them month by month "
              "into one Excel sheet, which we have submitted. It shows every value and where it came from."))
title(s, "Data", "132 months · 4 official sources", 32)
rows = [["Variable", "Source", "Unit", "Jan 2015", "Dec 2025"]]
for v, k in zip(S["variables"], ("FOODCPI", "EXR", "GFOOD", "TRANSCPI")):
    ts = json.loads((O / "timeseries.json").read_text())["series"][k]
    rows.append([v["name"], v["source"], v["measure"], f"{ts[0]:.2f}", f"{ts[-1]:.2f}"])
table(s, 0.7, 1.9, 11.9, rows, [2.4, 3.2, 3.7, 1.3, 1.3], size=12)
text(s, 0.7, 4.6, 12, 1.4, ["Monthly · January 2015 – December 2025 · N = 132 · no missing values",
                            "Combined dataset: Falling_Rupee_Dataset.xlsx (sheets: Combined Data · Sources · Model Variables · Summary Statistics)"], 15, DIM)

s = slide(1, ("This is the one equation of our project. Food prices on the left. On the right, the three causes, each with a beta. The beta "
              "tells us how strongly that cause moves food prices. We use logarithms, so each beta is an elasticity — a percentage effect. For "
              "example, if beta-one is 0.5, then a 10 percent weaker rupee means about 5 percent more expensive food."))
title(s, "The model", "One equation")
box(s, 0.7, 2.0, 11.9, 2.4, line=GOLD)
text(s, 1.0, 2.35, 11.3, 1.9, [[("Food Prices", RED), (" = β₀ + β₁ ", PAPER), ("Dollar Rate", AMBER), (" + β₂ ", PAPER), ("World Food Prices", GREEN),
                                (" + β₃ ", PAPER), ("Fuel & Transport Costs", BLUE), (" + error", PAPER)]], 30, align=PP_ALIGN.CENTER)
text(s, 0.7, 4.8, 12, 1.5, ["β = how much food prices change (in %) when that variable changes by 1%.",
                            "Estimated with an ARDL model — a regression that handles data that trend over time and lets effects build up over months."], 16, DIM)

s = slide(1, ("These are our five hypotheses. In each one, H-zero says there is no effect, and H-one says there is an effect. H1 is about the "
              "dollar rate, H2 world food prices, H3 fuel costs. H4 asks whether these variables are tied together in the long run. H5 asks "
              "whether a falling rupee and a rising rupee have the same effect. Our rule is simple: if the p-value is below 0.05, we reject "
              "H-zero. Now my teammate will show the data and the tests."))
title(s, "Hypotheses", "H₀ (no effect) vs H₁ (effect)")
rows = [["", "H₀", "H₁", "Test"]] + [[h["id"], h["h0"], h["h1"], h["test"]] for h in S["hypotheses"]]
table(s, 0.7, 1.75, 11.9, rows, [0.6, 4.6, 4.3, 2.4], size=11)
text(s, 0.7, 6.3, 12, 0.5, "Decision rule: p-value < 0.05 → reject H₀ (significant at 5%).", 15, GOLD)

# ========================================================================================= MEMBER 2
divider(2, "The data and the tests")
s = slide(2, ("Thank you. I'll start with the data itself. This graph sets all four variables to 100 in January 2015 so we can compare them. "
              f"Food prices — red — end at about {100 + D['FOODCPI']['total_change_pct']:.0f}. The dollar rate — yellow — ends at about "
              f"{100 + D['EXR']['total_change_pct']:.0f}. They climb together, especially in 2019 and in 2022–23. World food prices — green — end at "
              f"only about {100 + D['GFOOD']['total_change_pct']:.0f}. Just by looking, food prices follow the rupee, not the world."))
title(s, "Graph", "All four variables, January 2015 = 100")
pic(s, FIG / "fig01_rebased_indices.png", 0.9, 1.6, w=11.4)

s = slide(2, ("These are the descriptive statistics. For each variable: the average, the middle value, how spread out it is, and the lowest "
              f"and highest values. The key column is the last one. Food prices grew about {D['FOODCPI']['cagr_pct']:.1f} percent every year on "
              f"average, the dollar rate about {D['EXR']['cagr_pct']:.1f} percent, but world food prices only about {D['GFOOD']['cagr_pct']:.1f} percent."))
title(s, "Descriptive statistics", "Summary of the data (N = 132)")
rows = [["Variable", "Mean", "Median", "Std. dev.", "Min", "Max", "Growth / year"]]
for k, nm in (("FOODCPI", "Food Prices"), ("EXR", "Dollar Rate"), ("GFOOD", "World Food Prices"), ("TRANSCPI", "Fuel & Transport Costs")):
    d = D[k]
    rows.append([nm, f"{d['mean']:.1f}", f"{d['median']:.1f}", f"{d['sd']:.1f}", f"{d['min']:.1f}", f"{d['max']:.1f}", f"{d['cagr_pct']:.1f}%"])
table(s, 0.7, 1.9, 11.9, rows, [3.2, 1.4, 1.4, 1.5, 1.4, 1.4, 1.6], size=14)
text(s, 0.7, 4.7, 12, 1, f"Food inflation averaged {D['FOOD_INF_YOY']['mean']:.1f}% a year and peaked at {D['FOOD_INF_YOY']['max']:.1f}% (May 2023).", 16, DIM)

s = slide(2, ("The correlation matrix shows how closely each pair of variables moves together, from minus one to plus one. Food prices and "
              f"the dollar rate have a correlation of {corr['levels_log']['matrix'][0][1]:.2f} — almost perfect. But correlation is not enough: two "
              "things that both rise over time will always look correlated. That is why we need the proper tests that come next."))
title(s, "Correlation matrix", "Which variables move together?")
pic(s, FIG / "slide_corr.png", 0.8, 1.6, h=5.3)
text(s, 7.4, 2.0, 5.3, 4.5, [f"Food Prices vs Dollar Rate: r = {corr['levels_log']['matrix'][0][1]:.2f}",
                             f"Food Prices vs World Food Prices: r = {corr['levels_log']['matrix'][0][2]:.2f}",
                             f"Food Prices vs Fuel & Transport: r = {corr['levels_log']['matrix'][0][3]:.2f}", "",
                             "High correlation shows they move together — it does not prove cause. The tests do that job."], 16, DIM)

s = slide(2, ("Test one is the ADF unit root test. It checks whether a variable has a stable average or keeps trending upward. H-zero says it "
              "is not stationary. In levels, all p-values are above 0.05, so the variables trend. After we take the monthly change, all p-values "
              "are below 0.05, so they become stationary. We call this I(1). This matters because ordinary regression on trending data can "
              "give fake results. The ARDL method we use is designed exactly for I(1) data."))
title(s, "Test 1 · ADF unit root", "Do the variables trend over time?")
rows = [["Variable", "p-value (level)", "p-value (1st difference)", "Result"]] + [
    [u["name"], f"{u['level_p']:.3f}", "< 0.001" if u["diff_p"] < 0.001 else f"{u['diff_p']:.3f}", u["order"]] for u in S["unit_roots"]]
table(s, 0.7, 1.9, 11.9, rows, [3.6, 2.6, 3.2, 2.5], size=14)
text(s, 0.7, 4.4, 12, 1.6, ["H₀: the variable has a unit root (not stationary).",
                            "Level p > 0.05 → trends · 1st difference p < 0.05 → stationary → all variables are I(1).",
                            "→ ARDL is the right method (no variable is I(2))."], 16, DIM)

b = ardl["bounds_test"]
s = slide(2, (f"Test two is the ARDL Bounds Test. It answers H4: are the variables tied together in the long run? H-zero says no. Our F "
              f"statistic is {b['F']:.2f}. The critical value at 5 percent is {b['asymptotic']['5%']['F_I1']}. Our F is bigger, so we reject H-zero: "
              f"there is a long-run relationship. Then the error correction term is {ECM['speed_of_adjustment']:.2f}. It is negative and "
              f"significant, which means when food prices move away from the long-run path, about {-100*ECM['speed_of_adjustment']:.0f} percent of "
              f"the gap closes every month — half the gap is gone in about {ECM['half_life_months']:.1f} months. Now my teammate will present the results."))
title(s, "Test 2 · Bounds test & ECM", "Are the variables tied together in the long run?")
box(s, 0.7, 1.9, 5.8, 3.0, line=GOLD)
text(s, 1.0, 2.1, 5.3, 2.7, ["ARDL Bounds Test", f"F = {b['F']:.2f}", f"5% critical value (upper) = {b['asymptotic']['5%']['F_I1']}",
                             "F > critical value → Reject H₀", "→ long-run relationship EXISTS"], 18)
box(s, 6.8, 1.9, 5.8, 3.0, line=GOLD)
text(s, 7.1, 2.1, 5.3, 2.7, ["Error Correction Term (ECT)", f"ECT = {ECM['speed_of_adjustment']:.3f} (p < 0.001)",
                             f"≈ {-100*ECM['speed_of_adjustment']:.0f}% of any gap closes each month",
                             f"Half-life ≈ {ECM['half_life_months']:.1f} months", "Negative & significant → stable"], 18)
text(s, 0.7, 5.3, 12, 1, "H₀ (bounds): no long-run relationship. H₀ (ECT): no adjustment back to the long-run path.", 14, MUTED)

# ========================================================================================= MEMBER 3
divider(3, "The results and the conclusion")
s = slide(3, ("Thank you. Here is our main result — the estimated equation. The numbers replace the betas. For the dollar rate the number is "
              f"{C['LEXR']['coef']:.2f}: if the dollar rate rises 10 percent, food prices rise about 6.3 percent in the long run. For world food prices "
              f"it is {C['LGFOOD']['coef']:.2f}: a 10 percent rise means about 5.9 percent higher food prices. Fuel and transport costs have "
              f"{C['LTRANSCPI']['coef']:.2f}, but its p-value is {C['LTRANSCPI']['p']:.2f}, so we cannot say it is different from zero."))
title(s, "Result", "The estimated equation")
box(s, 0.7, 1.8, 11.9, 1.8, line=GOLD)
text(s, 1.0, 2.1, 11.3, 1.5, [[("Food Prices", RED), (f" = {S['constant']:.2f} + {C['LEXR']['coef']:.2f} ", PAPER), ("Dollar Rate", AMBER),
                               (f" + {C['LGFOOD']['coef']:.2f} ", PAPER), ("World Food Prices", GREEN), (f" + {C['LTRANSCPI']['coef']:.2f} ", PAPER),
                               ("Fuel & Transport", BLUE)]], 28, align=PP_ALIGN.CENTER)
pic(s, FIG / "slide_coefs.png", 0.9, 3.8, h=3.05)
text(s, 7.9, 3.9, 4.8, 3, [c["plain"] for c in S["coefficients"]], 14, DIM)

s = slide(3, ("This table gives the decision for every hypothesis. H1, dollar rate: p is 0.004, below 0.05, so we reject H-zero — a weaker rupee "
              "does raise food prices. H2, world food prices: p is 0.002, reject H-zero. H3, fuel costs: p is 0.36, above 0.05, so we fail to "
              "reject H-zero — no clear effect. H4: the bounds test rejected H-zero, so there is a long-run relationship. H5 has two answers: in "
              "the short run the effects are different, but in the long run we cannot tell."))
title(s, "Hypothesis results", "Decision for every hypothesis")
rows = [["", "Question", "Result", "Decision"]] + [[h["id"], h["question"], h["result"], h["decision"]] for h in S["hypotheses"]]
table(s, 0.7, 1.75, 11.9, rows, [0.6, 4.0, 4.4, 2.9], size=11)

s = slide(3, ("This is the second part of our question: does food become cheaper when the rupee recovers? We split the rupee into 'falling' and "
              f"'rising' months. When the rupee falls 1 percent, food prices end up about {A['falling']:.2f} percent higher, and this is significant. "
              "But in the month the rupee gets stronger, food prices do not fall — they actually still go up a little. The Wald test confirms "
              f"the short-run effects are different, p = {A['p_short']:.3f}. In the long run the p-value is {A['p_long']:.2f}, so we cannot prove a "
              "difference — there were too few months of a strong rupee. Simple message: prices go up fast, and do not come down quickly."))
title(s, "Asymmetry · Wald test", "When the rupee falls vs when it recovers")
pic(s, FIG / "fig04_dynamic_multipliers.png", 0.7, 1.6, w=7.6)
text(s, 8.6, 1.8, 4.2, 5, [f"Rupee falls 1% → food +{A['falling']:.2f}% (p = {A['falling_p']:.3f}) ✓",
                           f"Rupee rises 1% → same month food +{A['impact_rising']:.2f}% (did not fall)",
                           f"Wald short run: p = {A['p_short']:.3f} → different", f"Wald long run: p = {A['p_long']:.2f} → can't tell",
                           "", "Rockets up, feathers down."], 15, DIM)

s = slide(3, ("Before trusting the result we checked the model. Serial correlation — Breusch-Godfrey — passed. Heteroskedasticity — Breusch-"
              "Pagan — passed. The functional form — Ramsey RESET — passed. Stability — CUSUM — the line stays inside the bands, so the "
              "relationship was stable from 2015 to 2025. Only normality, Jarque-Bera, failed, because of a few extreme months like May 2024. "
              "With 128 months this does not change our conclusions."))
title(s, "Diagnostic tests", "Can we trust the model?")
rows = [["Test", "Checks", "p-value / result", "Decision", ""]]
for nm in ("Breusch-Godfrey (Serial Correlation)", "Breusch-Pagan-Godfrey (Heteroskedasticity)", "Jarque-Bera (Normality)",
           "Ramsey RESET (Model Form)", "CUSUM & CUSUM of Squares (Stability)"):
    t = T[nm]
    rows.append([nm, t["checks"], t["result"], t["decision"], "✓ pass" if t["pass"] else "✗ issue"])
table(s, 0.7, 1.75, 11.9, rows, [3.1, 3.6, 2.4, 1.8, 1.0], size=11)
pic(s, FIG / "fig05_stability_ardl.png", 3.2, 5.0, h=1.9)

s = slide(3, ("To conclude. One: a weaker rupee raises food prices — this is our strongest finding. Two: world food prices matter too, but the "
              "rupee matters more for Pakistan. Three: fuel costs had no clear effect in our model. Four: when the rupee recovers, food prices "
              "do not come back down quickly. For policy: keep the rupee stable, support poor families directly instead of waiting for the "
              "rupee to recover, and diversify food imports. A limit: our model shows strong links, not proof of cause. Thank you — we are "
              "happy to take questions."))
title(s, "Conclusion", "What we found")
text(s, 0.7, 1.8, 12, 3.6, [f"{i + 1}.  {a}" for i, a in enumerate(S["answer"])], 17)
text(s, 0.7, 5.5, 12, 1.2, ["Policy: keep the rupee stable · help poor families directly · diversify food imports.",
                            "Limit: strong links, not proof of cause and effect."], 15, GOLD)

s = slide(3, "Close here and invite questions. All three members stand together for the Q&A.")
text(s, 0.7, 2.2, 12, 2, ["A currency can recover in a season.", "The price of bread remembers."], 44, align=PP_ALIGN.CENTER)
text(s, 0.7, 4.7, 12, 0.6, SITE, 16, GOLD, font="Consolas", align=PP_ALIGN.CENTER)
text(s, 0.7, 5.4, 12, 0.6, "Thank you · Questions", 22, MUTED, align=PP_ALIGN.CENTER)

out = OUT / "The_Price_of_a_Falling_Rupee_Deck.pptx"
prs.save(out)
print("wrote", out.relative_to(ROOT), len(prs.slides), "slides")
