"""
10_build_deck.py — presentation deck (PPTX, 16:9) built from the results registry, with speaker notes.
Run: python scripts/10_build_deck.py   (PDF: soffice --headless --convert-to pdf presentation/*.pptx --outdir presentation)
"""
from __future__ import annotations

import json
import math
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.util import Emu, Inches, Pt

ROOT = Path(__file__).resolve().parents[1]
O = ROOT / "research" / "outputs"
FIG = O / "figures"
OUT = ROOT / "presentation"
OUT.mkdir(exist_ok=True)
J = lambda n: json.loads((O / f"{n}.json").read_text())
ardl, nardl, ols, desc, rob = J("ardl_results"), J("nardl_results"), J("ols_results"), J("descriptive_statistics"), J("robustness")
F = json.loads((ROOT / "data" / "research" / "findings.json").read_text())
H, RC = F["headline_numbers"], F["robustness_counts"]
LA = {x["variable"]: x for x in ardl["long_run"]}
LN = {x["variable"]: x for x in nardl["long_run"]}
AS, BA, BN = nardl["asymmetry"], ardl["bounds_test"], nardl["bounds_test"]
ECA = ardl["ecm_regression"]
SITE = "https://the-price-of-a-falling-rupee.vercel.app"

INK, PAPER, DIM, GOLD, RED, GREEN, MUTED = (RGBColor(0x0B, 0x0C, 0x0E), RGBColor(0xF1, 0xEC, 0xE2), RGBColor(0xC9, 0xC3, 0xB7),
                                            RGBColor(0xC9, 0xA2, 0x4A), RGBColor(0xE5, 0x48, 0x4D), RGBColor(0x00, 0xA8, 0x88),
                                            RGBColor(0x9A, 0x95, 0x8B))
f = lambda x, d=2: f"{x:.{d}f}".replace("-", "−")
fp = lambda p: "< 0.001" if p < 0.001 else f"{p:.3f}"

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]


def slide(notes=""):
    s = prs.slides.add_slide(BLANK)
    bg = s.background.fill
    bg.solid()
    bg.fore_color.rgb = INK
    if notes:
        s.notes_slide.notes_text_frame.text = notes
    return s


def text(s, x, y, w, h, t, size=18, color=PAPER, bold=False, italic=False, font="Georgia", align=PP_ALIGN.LEFT):
    tb = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    lines = t if isinstance(t, list) else [t]
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        r = p.add_run()
        r.text = line
        r.font.size, r.font.color.rgb, r.font.bold, r.font.italic, r.font.name = Pt(size), color, bold, italic, font
        p.space_after = Pt(size * 0.45)
    return tb


def kicker(s, n, label):
    text(s, 0.7, 0.45, 10, 0.4, f"{n:02d}   {label.upper()}", size=11, color=GOLD, font="Consolas")


def footer(s):
    text(s, 0.7, 7.0, 12, 0.3, f"The Price of a Falling Rupee · {SITE.replace('https://', '')} · Python estimates, EViews verification pending",
         size=8, color=MUTED, font="Consolas")


def pic(s, path, x, y, w):
    s.shapes.add_picture(str(path), Inches(x), Inches(y), width=Inches(w))


def stat(s, x, y, value, label, color=PAPER, w=3.6):
    text(s, x, y, w, 0.9, value, size=40, color=color, font="Consolas")
    text(s, x, y + 0.95, w, 0.8, label, size=11, color=MUTED, font="Consolas")


# 1 title
s = slide("Open with the question. Pause on the three numbers: food +194%, rupee +178%, world food +23%. The gap between the last two is the puzzle.")
text(s, 0.7, 1.3, 12, 0.5, "AN ECONOMETRIC INVESTIGATION · PAKISTAN · 2015–2025", size=12, color=GOLD, font="Consolas")
text(s, 0.7, 1.8, 12, 2.6, ["THE PRICE OF A", "FALLING RUPEE"], size=54, bold=True)
text(s, 0.7, 4.45, 11, 0.8, "Why do food prices rise when the rupee falls — and why don't they fall when it recovers?", size=22, color=DIM, italic=True)
stat(s, 0.7, 5.35, f"+{f(H['food_cpi_change_pct'],0)}%", "FOOD PRICES IN PAKISTAN", RED)
stat(s, 4.6, 5.35, f"+{f(H['exr_change_pct'],0)}%", "RUPEES PER US DOLLAR", GOLD)
stat(s, 8.5, 5.35, f"+{f(H['gfood_change_pct'],0)}%", "WORLD FOOD PRICES (FAO)", GREEN)
footer(s)

# 2 problem
s = slide("Food is 34.58% of the national CPI. Peak food inflation 48.7% in May 2023. The chart shows co-movement — the models test it.")
kicker(s, 2, "The problem")
text(s, 0.7, 0.95, 12, 1, "A third of the budget, tripled in price.", size=36)
pic(s, FIG / "fig01_rebased_indices.png", 0.7, 1.9, 7.6)
text(s, 8.6, 2.0, 4.2, 4.6, [
    f"Food CPI: +{f(H['food_cpi_change_pct'],0)}% (CAGR {f(H['food_cagr_pct'],1)}%)",
    f"Peak food inflation: {f(H['food_infl_peak'],1)}% ({H['food_infl_peak_date']})",
    "Food weight in national CPI: 34.58% (PBS)",
    f"Rupee depreciated in {desc['exchange_rate_months']['depreciating']} of 131 months; appreciated in {desc['exchange_rate_months']['appreciating']}",
    "World food prices rose far less than Pakistani food prices",
], size=15, color=DIM)
footer(s)

# 3 question & hypotheses
s = slide("State the three research questions and the hypotheses H1–H3 so the examiner knows what will be tested.")
kicker(s, 3, "Research questions")
text(s, 0.7, 1.0, 12, 0.8, "What we set out to test", size=36)
text(s, 0.7, 2.0, 12, 4.6, [
    "RQ1  How far do depreciation, world food prices and energy costs explain food inflation?",
    "RQ2  Is there a long-run equilibrium — and how fast do prices return to it?",
    "RQ3  Does depreciation have a stronger or more persistent effect than appreciation?",
    "",
    "H1  Pass-through exists (long-run elasticity > 0)     H2  It is incomplete (< 1)     H3  It is asymmetric",
], size=20, color=DIM)
footer(s)

# 4 mechanism
s = slide("Walk the chain left to right. Direct channel: imported finished foods. Indirect: inputs, energy, wholesale. Lags motivate ARDL.")
kicker(s, 4, "Transmission mechanism")
text(s, 0.7, 1.0, 12, 0.8, "From the currency market to the kitchen table", size=34)
boxes = ["Rupee depreciation", "Imported food & inputs", "Production & transport costs", "Wholesale markets", "Consumer food prices"]
for i, b in enumerate(boxes):
    x = 0.7 + i * 2.5
    shp = s.shapes.add_shape(1, Inches(x), Inches(3.0), Inches(2.1), Inches(1.2))
    shp.fill.solid()
    shp.fill.fore_color.rgb = RGBColor(0x15, 0x17, 0x1A)
    shp.line.color.rgb = RED if i == 4 else GOLD if i == 0 else RGBColor(0x3A, 0x3F, 0x46)
    tf = shp.text_frame
    tf.text = b
    tf.paragraphs[0].runs[0].font.size = Pt(15)
    tf.paragraphs[0].runs[0].font.color.rgb = PAPER
    if i < 4:
        text(s, x + 2.1, 3.3, 0.4, 0.5, "→", size=24, color=GOLD)
text(s, 0.7, 4.7, 12, 1.6, ["+ World food prices enter at the import stage.", "+ Domestic energy costs enter production and transport — and themselves move with the rupee."],
     size=17, color=DIM)
footer(s)

# 5 data
s = slide("Emphasise provenance: SHA-256 logged raw files, 10 validation checks, and the 2019 CPI base change handled transparently.")
kicker(s, 5, "The data room")
text(s, 0.7, 1.0, 12, 0.8, "132 months · 0 missing · every number traceable", size=32)
text(s, 0.7, 2.0, 12, 4.6, [
    "Food CPI — PBS national CPI, food & non-alcoholic beverages (IMF CPI dataset to Jul 2025; PBS reviews Aug–Dec 2025)",
    "Exchange rate — PKR per USD, period average (World Bank GEM; cross-checked with IMF IFS, r = 0.99997)",
    "World food prices — FAO Food Price Index (2014–16 = 100)",
    "Energy — national transport CPI (motor fuel); housing & utilities CPI and Brent in robustness",
    "Base year: PBS 2015-16 national CPI from Jul 2019; earlier months are the IMF's back-linked series → tested with a step dummy and a post-2019 sample",
], size=16, color=DIM)
footer(s)

# 6 OLS & unit roots
eg = ols["spurious_regression_check"]["engle_granger"]
s = slide("The OLS R² is a trap. DW far below R² and Engle–Granger p = 0.16 → possible spurious regression. All variables I(1), none I(2) → ARDL admissible.")
kicker(s, 6, "Econometric engine I")
text(s, 0.7, 1.0, 12, 0.8, "Why simple OLS is not enough", size=34)
stat(s, 0.7, 2.2, f(ols["r2"], 3), "OLS R²")
stat(s, 4.6, 2.2, f(ols["dw"], 2), "DURBIN–WATSON", RED)
stat(s, 8.5, 2.2, fp(eg["p"]), "ENGLE–GRANGER p-VALUE", RED)
text(s, 0.7, 4.4, 12, 2.2, ["R² > DW: the Granger–Newbold signature of a possibly spurious regression.",
                            "ADF, PP and KPSS: every series is I(1); none is I(2) → the ARDL bounds test is valid."], size=18, color=DIM)
footer(s)

# 7 ARDL
s = slide("Both PSS tests reject at 5% with asymptotic and finite-sample bounds. Elasticities: EXR 0.64, FAO 0.61; energy insignificant. Half-life ~5.4 months.")
kicker(s, 7, "Econometric engine II")
text(s, 0.7, 1.0, 12, 0.8, f"ARDL{tuple(ardl['selection']['chosen_order'])}: a long-run equilibrium exists", size=32)
stat(s, 0.7, 2.1, f(BA["F"]), f"BOUNDS F (5% I(1) BOUND {BA['asymptotic']['5%']['F_I1']})", GOLD)
stat(s, 4.6, 2.1, f(BA["t"]), f"BOUNDS t (5% I(1) BOUND {BA['asymptotic']['5%']['t_I1']})", GOLD)
stat(s, 8.5, 2.1, f(ECA["speed_of_adjustment"], 3), f"SPEED OF ADJUSTMENT · HALF-LIFE {f(ECA['half_life_months'],1)} MO", GOLD)
text(s, 0.7, 4.3, 12, 2.3, [
    f"Long-run elasticity, exchange rate: {f(LA['LEXR']['coef'])} (p = {fp(LA['LEXR']['p'])})",
    f"Long-run elasticity, world food prices: {f(LA['LGFOOD']['coef'])} (p = {fp(LA['LGFOOD']['p'])})",
    f"Long-run elasticity, energy (transport CPI): {f(LA['LTRANSCPI']['coef'])} (p = {fp(LA['LTRANSCPI']['p'])}) — not significant",
], size=18, color=DIM)
footer(s)

# 8 NARDL decomposition
s = slide("Explain partial sums: EXR⁺ collects every depreciation, EXR⁻ every appreciation. Appreciations are fewer and smaller — limits precision.")
kicker(s, 8, "The asymmetry investigation")
text(s, 0.7, 1.0, 12, 0.8, "When the rupee falls, prices rise. What happens when it recovers?", size=24)
pic(s, FIG / "fig03_partial_sums.png", 0.7, 2.1, 7.8)
text(s, 8.8, 2.1, 4.0, 4.5, ["ln EXR = ln EXR₀ + EXR⁺ + EXR⁻", "", f"NARDL{tuple(nardl['selection']['chosen_order'])}",
                             f"Bounds F = {f(BN['F'])} → reject", f"Bounds t = {f(BN['t'])} → do not reject", "→ long-run NARDL results read with caution"],
     size=16, color=DIM)
footer(s)

# 9 multipliers
s = slide("Key slide. Depreciation response builds to ~0.5. Appreciation: prices rise on impact, then reverse — but bands are wide.")
kicker(s, 9, "Dynamic multipliers")
text(s, 0.7, 1.0, 12, 0.8, "Rockets on impact; feathers — maybe — later", size=32)
pic(s, FIG / "fig04_dynamic_multipliers.png", 0.7, 1.9, 11.9)
footer(s)

# 10 symmetry tests
s = slide("Do not declare asymmetry from different numbers — test it. Long-run symmetry not rejected; impact symmetry rejected.")
kicker(s, 10, "Wald tests")
text(s, 0.7, 1.0, 12, 0.8, "Testing symmetry, not eyeballing it", size=34)
stat(s, 0.7, 2.1, f(LN["LEXR_POS"]["coef"]), f"L⁺ DEPRECIATION (p = {fp(LN['LEXR_POS']['p'])})", RED)
stat(s, 4.6, 2.1, f(LN["LEXR_NEG"]["coef"]), f"L⁻ APPRECIATION (p = {fp(LN['LEXR_NEG']['p'])})", GREEN)
stat(s, 8.5, 2.1, fp(AS["short_run"]["p_impact"]), "IMPACT SYMMETRY p → REJECTED", GOLD)
text(s, 0.7, 4.3, 12, 2.3, [
    f"Long-run symmetry: Wald χ²(1) = {f(AS['long_run']['wald_chi2'])}, p = {fp(AS['long_run']['p_chi2'])} → not rejected",
    f"Impact symmetry: F = {f(AS['short_run']['F_impact'])}, p = {fp(AS['short_run']['p_impact'])} → rejected: prices do not fall in the month the rupee appreciates",
    "Failing to reject long-run symmetry ≠ evidence of symmetry: the appreciation estimate is imprecise.",
], size=17, color=DIM)
footer(s)

# 11 diagnostics
s = slide("Diagnostics clean except normality (a few extreme months; fixed by May-2024 dummy). NARDL CUSUMSQ crosses → variance change.")
kicker(s, 11, "Credibility")
text(s, 0.7, 1.0, 12, 0.8, "Trying to break our own model", size=34)
pic(s, FIG / "fig06_stability_nardl.png", 0.7, 1.9, 7.6)
diag = [d for d in nardl["diagnostics"] if d.get("p") is not None]
text(s, 8.6, 2.0, 4.3, 4.8, [f"{d['test']}: p = {fp(d['p'])}{' ✗' if d['reject_5pct'] else ' ✓'}" for d in diag], size=12, color=DIM, font="Consolas")
footer(s)

# 12 robustness
s = slide("Depreciation effect positive in all specs, significant in most; appreciation never significant.")
kicker(s, 12, "Robustness")
text(s, 0.7, 1.0, 12, 0.8, f"{RC['n_specs']} alternative specifications", size=34)
pic(s, FIG / "fig08_robustness_forest.png", 0.7, 1.9, 7.0)
text(s, 8.1, 2.1, 4.8, 4.6, [f"L⁺ positive: {RC['pos_positive']}/{RC['n_specs']}", f"L⁺ significant: {RC['pos_significant']}/{RC['n_specs']}",
                             f"L⁻ significant: {RC['neg_significant']}/{RC['n_specs']}", f"Long-run symmetry rejected: {RC['lr_symmetry_rejected']}/{RC['n_specs']}",
                             f"Impact symmetry rejected: {RC['impact_symmetry_rejected']}/{RC['n_specs']}",
                             "Weakest under event dummies incl. 2019M07 step and pre-2024 sample"], size=16, color=DIM)
footer(s)

# 13 conclusions & policy
dF = math.log(1 + H["food_cpi_change_pct"] / 100)
share = 100 * LA["LEXR"]["coef"] * math.log(1 + H["exr_change_pct"] / 100) / dF
s = slide("Accounting decomposition, not causal attribution. Policy: stability, targeted relief, diversify imports, competition in wholesale.")
kicker(s, 13, "Conclusion")
text(s, 0.7, 1.0, 12, 0.8, "The rupee's fall is paid for at the market", size=34)
text(s, 0.7, 2.0, 12, 4.6, [
    f"Long-run pass-through ≈ {f(LA['LEXR']['coef'])}: the rupee is associated with ≈ {f(share,0)}% of the log rise in food prices (accounting decomposition).",
    "Depreciation reliably raises food prices; appreciation does not bring a detectable, equivalent fall.",
    "Policy: exchange-rate stability is food policy · targeted relief over waiting for recovery · diversify edible-oil & pulse imports · competition in wholesale.",
    "Limits: observational data (no causal claim) · CPI base change 2019 · few appreciation episodes · EViews confirmation pending.",
], size=18, color=DIM)
footer(s)

# 14 close
s = slide("Close with the line, then invite questions. Point to the live site and the EViews package.")
text(s, 0.7, 2.3, 12, 2.4, ["A currency can recover in a season.", "The price of bread remembers."], size=48, align=PP_ALIGN.CENTER)
text(s, 0.7, 5.0, 12, 0.6, SITE, size=16, color=GOLD, font="Consolas", align=PP_ALIGN.CENTER)
text(s, 0.7, 5.6, 12, 0.6, "Questions", size=20, color=MUTED, align=PP_ALIGN.CENTER)

out = OUT / "The_Price_of_a_Falling_Rupee_Deck.pptx"
prs.save(out)
print("wrote", out.relative_to(ROOT), len(prs.slides), "slides")
