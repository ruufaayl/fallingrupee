"""
09_build_report.py — short project report (DOCX → PDF): problem, variables, equation, hypotheses, data, tests, results.
All numbers come from data/research/simple.json and research/outputs. Run: python scripts/09_build_report.py
"""
from __future__ import annotations

import json
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
O = ROOT / "research" / "outputs"
FIG = O / "figures"
OUT = ROOT / "report"
OUT.mkdir(exist_ok=True)
S = json.loads((ROOT / "data" / "research" / "simple.json").read_text())
desc = {v["variable"]: v for v in json.loads((O / "descriptive_statistics.json").read_text())["variables"]}
corr = json.loads((O / "correlations.json").read_text())
ts = json.loads((O / "timeseries.json").read_text())["series"]
A = S["asymmetry"]

doc = Document()
sec = doc.sections[0]
sec.page_height, sec.page_width = Cm(29.7), Cm(21.0)
sec.left_margin = sec.right_margin = Cm(2.2)
sec.top_margin = sec.bottom_margin = Cm(2.0)
st = doc.styles["Normal"]
st.font.name, st.font.size = "Calibri", Pt(11)
st.paragraph_format.space_after = Pt(6)
for lvl, size in ((1, 15), (2, 12.5)):
    hs = doc.styles[f"Heading {lvl}"]
    hs.font.name, hs.font.size, hs.font.bold = "Calibri", Pt(size), True
    hs.font.color.rgb = RGBColor(0x11, 0x12, 0x14)
N = {"t": 0, "f": 0}


def P(t, bold=False, italic=False, size=None, center=False):
    p = doc.add_paragraph()
    r = p.add_run(t)
    r.bold, r.italic = bold, italic
    if size:
        r.font.size = Pt(size)
    if center:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    return p


def shade(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr()
    s = OxmlElement("w:shd")
    s.set(qn("w:val"), "clear")
    s.set(qn("w:fill"), hexcolor)
    tcPr.append(s)


def table(header, rows, caption, size=10):
    N["t"] += 1
    P(f"Table {N['t']}. {caption}", bold=True, size=10)
    t = doc.add_table(rows=1, cols=len(header))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(header):
        c = t.rows[0].cells[i]
        c.text = ""
        run = c.paragraphs[0].add_run(h)
        run.bold, run.font.size = True, Pt(size)
        shade(c, "E8E2D6")
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            cells[i].paragraphs[0].add_run(str(v)).font.size = Pt(size)
    doc.add_paragraph()


def figure(path, caption, width=16):
    N["f"] += 1
    doc.add_picture(str(path), width=Cm(width))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    P(f"Figure {N['f']}. {caption}", italic=True, size=9, center=True)


# title
for _ in range(4):
    doc.add_paragraph()
P("THE PRICE OF A FALLING RUPEE", bold=True, size=26, center=True)
P("Exchange Rate, World Food Prices and Food Inflation in Pakistan (2015–2025)", italic=True, size=14, center=True)
doc.add_paragraph()
P("Macroeconomics — Final Semester Project", size=12, center=True)
doc.add_paragraph()
P("Group members:  1. ____________________   2. ____________________   3. ____________________", size=11, center=True)
P("Instructor: ____________________        Date: ____________________", size=11, center=True)
doc.add_paragraph()
P(f"Website: https://the-price-of-a-falling-rupee.vercel.app   ·   Dataset: Falling_Rupee_Dataset.xlsx", size=10, center=True)
doc.add_page_break()

doc.add_heading("1. Problem statement", 1)
P(S["problem"])
P(f"From January 2015 to December 2025: food prices +{desc['FOODCPI']['total_change_pct']:.0f}%, dollar rate +{desc['EXR']['total_change_pct']:.0f}%, "
  f"world food prices +{desc['GFOOD']['total_change_pct']:.0f}%. Food inflation peaked at {desc['FOOD_INF_YOY']['max']:.1f}% in May 2023.")
figure(FIG / "fig02_inflation_vs_depreciation.png", "Food inflation, rupee depreciation and world food price inflation (% per year).")

doc.add_heading("2. Research question", 1)
P(S["question"], bold=True)

doc.add_heading("3. Variables", 1)
table(["Role", "Variable", "Measured as", "Source"], [[v["role"], v["name"], v["measure"], v["source"]] for v in S["variables"]],
      "Dependent and independent variables.")

doc.add_heading("4. The equation", 1)
P(S["equation_general"], bold=True, size=13, center=True)
P("Each β is an elasticity: the % change in food prices when that variable changes by 1% (all variables in natural logs). The model is "
  "estimated as an ARDL (autoregressive distributed lag) model, which suits data that trend over time and lets effects build up over months; "
  "the equation above is its long-run form.")

doc.add_heading("5. Hypotheses", 1)
table(["#", "H₀ (null)", "H₁ (alternative)", "Test"], [[h["id"], h["h0"], h["h1"], h["test"]] for h in S["hypotheses"]], "Hypotheses.", size=9.5)
P("Decision rule: reject H₀ if the p-value is below 0.05 (5% significance level).")

doc.add_heading("6. Data", 1)
rows = []
for v, k in zip(S["variables"], ("FOODCPI", "EXR", "GFOOD", "TRANSCPI")):
    rows.append([v["name"], v["source"], f"{ts[k][0]:.2f}", f"{ts[k][-1]:.2f}", f"+{desc[k]['total_change_pct']:.0f}%"])
table(["Variable", "Source", "Jan 2015", "Dec 2025", "Change"], rows, "Data sources (monthly, Jan 2015 – Dec 2025, N = 132, no missing values).")
P("All four series are combined month by month in the attached Excel file (sheets: Combined Data, Sources, Model Variables, Summary Statistics).")
figure(FIG / "fig01_rebased_indices.png", "All four variables, January 2015 = 100.")

doc.add_heading("7. Descriptive statistics and correlation", 1)
rows = [[nm, f"{desc[k]['mean']:.1f}", f"{desc[k]['median']:.1f}", f"{desc[k]['sd']:.1f}", f"{desc[k]['min']:.1f}", f"{desc[k]['max']:.1f}", f"{desc[k]['cagr_pct']:.1f}%"]
        for k, nm in (("FOODCPI", "Food Prices"), ("EXR", "Dollar Rate"), ("GFOOD", "World Food Prices"), ("TRANSCPI", "Fuel & Transport Costs"))]
table(["Variable", "Mean", "Median", "Std. dev.", "Min", "Max", "Growth/yr"], rows, "Descriptive statistics.")
figure(FIG / "slide_corr.png", "Correlation matrix (log levels).", width=10)
P(f"Food prices and the dollar rate are almost perfectly correlated (r = {corr['levels_log']['matrix'][0][1]:.2f}). Because trending series always "
  "look correlated, we test the relationship formally below.")

doc.add_heading("8. Tests we ran", 1)
table(["Test", "What it checks", "H₀", "Result", "Decision"],
      [[t["name"], t["checks"], t["h0"] or "—", t["result"], t["decision"]] for t in S["tests"]], "Summary of all tests.", size=8.5)
table(["Variable", "ADF p (level)", "ADF p (1st diff.)", "Order"],
      [[u["name"], f"{u['level_p']:.3f}", "< 0.001" if u["diff_p"] < 0.001 else f"{u['diff_p']:.3f}", u["order"]] for u in S["unit_roots"]],
      "ADF unit root test.")

doc.add_heading("9. Results", 1)
P("Estimated long-run equation:", bold=True)
P(S["equation_estimated"], bold=True, size=12, center=True)
table(["Variable", "Coefficient", "Std. error", "p-value", "Meaning"],
      [[c["name"], f"{c['coef']:.2f}", f"{c['se']:.3f}", f"{c['p']:.3f}", c["plain"]] for c in S["coefficients"]], "Long-run coefficients.", size=9.5)
figure(FIG / "slide_coefs.png", "Long-run effects with 95% ranges (filled = significant at 5%).", width=14)
table(["#", "Result", "Decision"], [[h["id"], h["result"], h["decision"]] for h in S["hypotheses"]], "Hypothesis decisions.", size=9.5)
doc.add_heading("Asymmetry: rupee falling vs rupee rising", 2)
P(f"Using a nonlinear ARDL that splits the dollar rate into 'falling rupee' and 'rising rupee' parts: a 1% fall in the rupee raises food prices "
  f"by about {A['falling']:.2f}% in the long run (p = {A['falling_p']:.3f}). In the month the rupee rises, food prices do not fall "
  f"(+{A['impact_rising']:.2f}%). Wald test: short-run effects differ (p = {A['p_short']:.3f}); long-run difference not proven (p = {A['p_long']:.3f}).")
figure(FIG / "fig04_dynamic_multipliers.png", "Food price response to a 1% fall (red) and a 1% rise (green) of the rupee.")
figure(FIG / "fig05_stability_ardl.png", "CUSUM and CUSUM of squares — the model is stable.")

doc.add_heading("10. Conclusion", 1)
for i, a in enumerate(S["answer"], 1):
    P(f"{i}. {a}")
P("Policy: keep the rupee stable; support poor households directly instead of waiting for the rupee to recover; diversify food and input imports.")
P("Limits: the model shows strong, tested links, not proof of cause and effect; PBS changed the CPI base year in 2019; few months of a "
  "strong rupee make the 'recovery' effect uncertain.")

doc.add_heading("References", 1)
for r in [
    "Pesaran, M. H., Shin, Y., & Smith, R. J. (2001). Bounds testing approaches to the analysis of level relationships. Journal of Applied Econometrics, 16(3), 289–326.",
    "Shin, Y., Yu, B., & Greenwood-Nimmo, M. (2014). Modelling asymmetric cointegration and dynamic multipliers in a nonlinear ARDL framework. In Festschrift in Honor of Peter Schmidt (pp. 281–314). Springer.",
    "Dickey, D. A., & Fuller, W. A. (1979). Distribution of the estimators for autoregressive time series with a unit root. Journal of the American Statistical Association, 74(366), 427–431.",
    "Pakistan Bureau of Statistics. Monthly Review on Price Indices. https://www.pbs.gov.pk/price-statistics/",
    "World Bank. Global Economic Monitor (DPANUSSPB). https://databank.worldbank.org/source/global-economic-monitor-(gem)",
    "FAO. FAO Food Price Index. https://www.fao.org/worldfoodsituation/foodpricesindex/en/",
    "International Monetary Fund. Consumer Price Index dataset (Pakistan), via DBnomics. https://db.nomics.world/IMF/CPI",
]:
    P(r, size=9.5)

out = OUT / "The_Price_of_a_Falling_Rupee_Report.docx"
doc.save(out)
print("wrote", out.relative_to(ROOT), "tables", N["t"], "figures", N["f"])
