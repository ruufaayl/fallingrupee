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
      "Dependent and independent variables (all monthly % changes; X's from the previous month).", size=9.5)

doc.add_heading("4. The equation", 1)
P(S["equation_general"], bold=True, size=12, center=True)
P("Estimated by ordinary least squares (OLS). Every variable is a monthly % change; the X variables are taken from the previous month because "
  "prices take time to react. β₄ is the autoregressive term (last month's food inflation).")

doc.add_heading("5. Hypotheses", 1)
table(["#", "H₀ (null)", "H₁ (alternative)", "Test"], [[h["id"], h["h0"], h["h1"], h["test"]] for h in S["hypotheses"]], "Hypotheses.", size=9.5)
P("Decision rule: reject H₀ if the p-value is below 0.05 (5% significance level).")

doc.add_heading("6. Data", 1)
rows = []
for nm, k, src in (("Food Prices", "FOODCPI", "PBS"), ("Dollar Rate (PKR per USD)", "EXR", "World Bank GEM"), ("World Food Prices", "GFOOD", "FAO"),
                   ("Fuel & Transport Costs", "TRANSCPI", "PBS")):
    rows.append([nm, src, f"{ts[k][0]:.2f}", f"{ts[k][-1]:.2f}", f"+{desc[k]['total_change_pct']:.0f}%"])
table(["Series", "Source", "Jan 2015", "Dec 2025", "Change"], rows, "Data sources (monthly, Jan 2015 – Dec 2025, N = 132, no missing values).")
P("All series and the regression variables (monthly % changes) are in the attached Excel file (sheets: Combined Data, Regression Data, Sources, Summary Statistics).")
figure(FIG / "fig01_rebased_indices.png", "All four series, January 2015 = 100.")

doc.add_heading("7. Tests before the regression", 1)
rows = [[nm, f"{desc[k]['mean']:.1f}", f"{desc[k]['median']:.1f}", f"{desc[k]['sd']:.1f}", f"{desc[k]['min']:.1f}", f"{desc[k]['max']:.1f}", f"{desc[k]['cagr_pct']:.1f}%"]
        for k, nm in (("FOODCPI", "Food Prices"), ("EXR", "Dollar Rate"), ("GFOOD", "World Food Prices"), ("TRANSCPI", "Fuel & Transport Costs"))]
table(["Variable", "Mean", "Median", "Std. dev.", "Min", "Max", "Growth/yr"], rows, "Descriptive statistics.")
figure(FIG / "slide_corr_changes.png", "Correlation matrix of the regression variables (monthly % changes).", width=11)
table(["Variable", "ADF p (level)", "Level", "ADF p (% change)", "% change"],
      [[u["name"], f"{u['level_p']:.3f}", u["level_result"], "< 0.001" if u["change_p"] < 0.001 else f"{u['change_p']:.3f}", u["change_result"]] for u in S["stationarity"]],
      "Stationarity — ADF unit root test (H₀: non-stationary).")
table(["Independent variable", "VIF", "Tolerance"], [[v["name"], f"{v['vif']:.2f}", f"{v['tolerance']:.3f}"] for v in S["vif"]],
      "Multicollinearity — variance inflation factors (problem if VIF > 10).")

doc.add_heading("8. Regression results", 1)
P(S["equation_estimated"], bold=True, size=11.5, center=True)
F_ = S["fit"]
table(["Variable", "Coefficient", "Std. error", "t", "p-value", "Significant"],
      [["Constant", f"{S['constant']:.3f}", "", "", "", ""]] +
      [[c["name"], f"{c['coef']:.3f}", f"{c['se']:.3f}", f"{c['t']:.2f}", f"{c['p']:.3f}", "Yes" if c["significant"] else "No"] for c in S["coefficients"]],
      f"OLS regression, N = {S['n']}. R² = {F_['r2']:.3f}, adj. R² = {F_['adj_r2']:.3f}, F = {F_['F']:.2f} (p = {F_['F_p']:.4f}).", size=9.5)
figure(FIG / "slide_coefs.png", "Coefficients with 95% ranges (filled = significant at 5%).", width=14)
table(["#", "Result", "Decision"], [[h["id"], h["result"], h["decision"]] for h in S["hypotheses"]], "Hypothesis decisions.", size=9.5)

doc.add_heading("9. Diagnostic tests", 1)
table(["Test", "What it checks", "H₀", "Result", "Decision"],
      [[t["name"], t["checks"], t["h0"] or "—", t["result"], t["decision"]] for t in S["tests"] if t["group"] == "Diagnostics"], "Diagnostic tests.", size=8.5)
figure(FIG / "slide_fit.png", "Actual vs predicted monthly food inflation.")
figure(FIG / "slide_asym.png", "Asymmetry: effect of a falling vs a rising rupee (95% ranges).", width=12)

doc.add_heading("10. Conclusion", 1)
for i, a in enumerate(S["answer"], 1):
    P(f"{i}. {a}")
P("Policy: keep the rupee stable; treat a falling rupee as an early warning of food inflation; support poor households directly.")
P("Limits: the model shows a tested link with a time order, not proof of cause; it explains about 10% of monthly swings (weather, harvests "
  "and policy also matter); the rupee rose in few months, so the 'recovery' effect is uncertain.")

doc.add_heading("References", 1)
for r in [
    "Durbin, J., & Watson, G. S. (1950). Testing for serial correlation in least squares regression: I. Biometrika, 37(3/4), 409–428.",
    "Breusch, T. S. (1978). Testing for autocorrelation in dynamic linear models. Australian Economic Papers, 17(31), 334–355.",
    "Breusch, T. S., & Pagan, A. R. (1979). A simple test for heteroscedasticity and random coefficient variation. Econometrica, 47(5), 1287–1294.",
    "White, H. (1980). A heteroskedasticity-consistent covariance matrix estimator and a direct test for heteroskedasticity. Econometrica, 48(4), 817–838.",
    "Jarque, C. M., & Bera, A. K. (1980). Efficient tests for normality, homoscedasticity and serial independence of regression residuals. Economics Letters, 6(3), 255–259.",
    "Ramsey, J. B. (1969). Tests for specification errors in classical linear least-squares regression analysis. Journal of the Royal Statistical Society B, 31(2), 350–371.",
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
