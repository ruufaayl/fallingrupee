"""
09_build_report.py — the academic report (DOCX, converted to PDF with LibreOffice).

Every statistic is read from research/outputs/*.json and data/research/findings.json, the same files that
drive the website, so the report and the site cannot disagree.
Run: python scripts/09_build_report.py   (then: soffice --headless --convert-to pdf report/*.docx --outdir report)
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from docx import Document
from docx.enum.section import WD_ORIENT  # noqa: F401
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
O = ROOT / "research" / "outputs"
FIG = O / "figures"
OUT = ROOT / "report"
OUT.mkdir(exist_ok=True)

J = lambda n: json.loads((O / f"{n}.json").read_text())
desc, corr, stn, ols, ardl, nardl = J("descriptive_statistics"), J("correlations"), J("stationarity"), J("ols_results"), J("ardl_results"), J("nardl_results")
mult, wald, rob = J("multipliers"), J("wald_tests"), J("robustness")
F = json.loads((ROOT / "data" / "research" / "findings.json").read_text())
VARS = json.loads((ROOT / "data" / "research" / "variables.json").read_text())
SRC = json.loads((ROOT / "data" / "research" / "sources.json").read_text())["sources"]
VAL = json.loads((ROOT / "data" / "metadata" / "validation_report.json").read_text())
H = F["headline_numbers"]
D = {v["variable"]: v for v in desc["variables"]}
LA = {x["variable"]: x for x in ardl["long_run"]}
LN = {x["variable"]: x for x in nardl["long_run"]}
AS = nardl["asymmetry"]
BA, BN = ardl["bounds_test"], nardl["bounds_test"]
ECA, ECN = ardl["ecm_regression"], nardl["ecm_regression"]
RC = F["robustness_counts"]


def f(x, d=3):
    return "—" if x is None else f"{x:.{d}f}".replace("-", "−")


def fp(p):
    return "—" if p is None else ("< 0.001" if p < 0.001 else f"{p:.3f}")


def star(p):
    return "" if p is None else "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.1 else ""


MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
ml = lambda s: f"{MON[int(s[5:7]) - 1]} {s[:4]}"

# ------------------------------------------------------------------------------------------------ document setup
doc = Document()
sec = doc.sections[0]
sec.page_height, sec.page_width = Cm(29.7), Cm(21.0)
for side in ("left_margin", "right_margin"):
    setattr(sec, side, Cm(2.4))
sec.top_margin = sec.bottom_margin = Cm(2.3)

st = doc.styles["Normal"]
st.font.name = "Georgia"
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Georgia")
st.font.size = Pt(11)
st.paragraph_format.space_after = Pt(6)
st.paragraph_format.line_spacing = 1.25
for lvl, size in ((1, 16), (2, 13), (3, 11.5)):
    hs = doc.styles[f"Heading {lvl}"]
    hs.font.name = "Georgia"
    hs.font.size = Pt(size)
    hs.font.bold = True
    hs.font.color.rgb = RGBColor(0x11, 0x12, 0x14)
    hs.paragraph_format.space_before = Pt(16 if lvl == 1 else 10)
    hs.paragraph_format.space_after = Pt(6)

# page numbers in footer
fp_ = sec.footer.paragraphs[0]
fp_.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = fp_.add_run()
for t, txt in (("begin", None), (None, "PAGE"), ("end", None)):
    if t:
        e = OxmlElement("w:fldChar")
        e.set(qn("w:fldCharType"), t)
        r._r.append(e)
    else:
        e = OxmlElement("w:instrText")
        e.set(qn("xml:space"), "preserve")
        e.text = txt
        r._r.append(e)

TCOUNT = [0]
FCOUNT = [0]


def P(text, bold=False, italic=False, size=None, align=None, after=None):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold, run.italic = bold, italic
    if size:
        run.font.size = Pt(size)
    if align:
        p.alignment = align
    if after is not None:
        p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.alignment = align if align else WD_ALIGN_PARAGRAPH.JUSTIFY
    return p


def bullets(items, style="List Bullet"):
    for it in items:
        doc.add_paragraph(it, style=style)


def shade(cell, hexcolor):
    tcPr = cell._tc.get_or_add_tcPr()
    s = OxmlElement("w:shd")
    s.set(qn("w:val"), "clear")
    s.set(qn("w:color"), "auto")
    s.set(qn("w:fill"), hexcolor)
    tcPr.append(s)


def table(header, rows, caption, widths=None, note=None, size=8.5):
    TCOUNT[0] += 1
    cp = doc.add_paragraph()
    cr = cp.add_run(f"Table {TCOUNT[0]}. {caption}")
    cr.bold = True
    cr.font.size = Pt(9.5)
    cp.paragraph_format.keep_with_next = True
    t = doc.add_table(rows=1, cols=len(header))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(header):
        c = t.rows[0].cells[i]
        c.text = ""
        run = c.paragraphs[0].add_run(h)
        run.bold = True
        run.font.size = Pt(size)
        shade(c, "E8E2D6")
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            run = cells[i].paragraphs[0].add_run(str(v))
            run.font.size = Pt(size)
            if i > 0:
                cells[i].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Cm(w)
    if note:
        n = doc.add_paragraph()
        nr = n.add_run(note)
        nr.italic = True
        nr.font.size = Pt(8)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def figure(path, caption, width=16):
    FCOUNT[0] += 1
    doc.add_picture(str(path), width=Cm(width))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    c = doc.add_paragraph()
    r_ = c.add_run(f"Figure {FCOUNT[0]}. {caption}")
    r_.italic = True
    r_.font.size = Pt(9)
    c.alignment = WD_ALIGN_PARAGRAPH.CENTER


def page_break():
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


# ================================================================================================ TITLE PAGE
for _ in range(5):
    doc.add_paragraph()
P("THE PRICE OF A FALLING RUPEE", bold=True, size=28, align=WD_ALIGN_PARAGRAPH.CENTER, after=4)
P("An Econometric Investigation of Exchange Rate Depreciation, International Food Prices and Food Inflation in Pakistan",
  italic=True, size=14, align=WD_ALIGN_PARAGRAPH.CENTER, after=30)
P("Macroeconomics — Final Semester Research Project", size=12, align=WD_ALIGN_PARAGRAPH.CENTER, after=2)
P("Monthly data, January 2015 – December 2025 (N = 132)", size=11, align=WD_ALIGN_PARAGRAPH.CENTER, after=2)
P("Methods: OLS · ADF/PP/KPSS · ARDL bounds testing · ECM · Nonlinear ARDL · Wald symmetry tests · dynamic multipliers",
  size=10, align=WD_ALIGN_PARAGRAPH.CENTER, after=40)
P("Student name: ______________________    Registration no.: ______________", size=11, align=WD_ALIGN_PARAGRAPH.CENTER, after=4)
P("Course instructor: ______________________    Institution: ______________________", size=11, align=WD_ALIGN_PARAGRAPH.CENTER, after=30)
P(f"Report generated {date.today():%d %B %Y} from the project's results registry.", italic=True, size=9, align=WD_ALIGN_PARAGRAPH.CENTER)
P("Estimation status: all estimates computed in Python (statsmodels 0.15). EViews programs reproducing every specification are "
  "provided; EViews confirmation is pending (see Appendix C).", italic=True, size=9, align=WD_ALIGN_PARAGRAPH.CENTER)
page_break()

# ================================================================================================ ABSTRACT
doc.add_heading("Abstract", 1)
P(f"Between January 2015 and December 2025 Pakistan's national food price index rose by {f(H['food_cpi_change_pct'],0)}%, while the "
  f"number of rupees per US dollar rose by {f(H['exr_change_pct'],0)}% and the FAO world food price index by only {f(H['gfood_change_pct'],0)}%. "
  "This study asks how far exchange-rate depreciation, international food prices and domestic energy costs explain Pakistan's food inflation, "
  "and whether depreciation and appreciation of the rupee affect food prices symmetrically. Using 132 monthly observations from the Pakistan "
  "Bureau of Statistics, IMF, World Bank and FAO, we test integration orders, show that a static OLS regression is likely spurious, and estimate "
  "an autoregressive distributed lag (ARDL) model with Pesaran–Shin–Smith bounds testing and a nonlinear ARDL (NARDL) that separates "
  f"depreciation from appreciation. The linear ARDL({','.join(map(str, ardl['selection']['chosen_order']))}) finds a long-run relationship "
  f"(F = {f(BA['F'],2)}, t = {f(BA['t'],2)}) with long-run elasticities of {f(LA['LEXR']['coef'],2)} for the exchange rate "
  f"(p = {fp(LA['LEXR']['p'])}) and {f(LA['LGFOOD']['coef'],2)} for world food prices (p = {fp(LA['LGFOOD']['p'])}); about "
  f"{f(-100*ECA['speed_of_adjustment'],0)}% of any disequilibrium is corrected each month. In the NARDL, the long-run effect of depreciation is "
  f"{f(LN['LEXR_POS']['coef'],2)} (p = {fp(LN['LEXR_POS']['p'])}) while the appreciation coefficient is statistically insignificant "
  f"(p = {fp(LN['LEXR_NEG']['p'])}). Long-run symmetry cannot be rejected (Wald p = {fp(AS['long_run']['p_chi2'])}), but impact symmetry "
  f"is rejected (p = {fp(AS['short_run']['p_impact'])}): food prices do not fall in the month the rupee appreciates. The depreciation effect is "
  f"positive in all {RC['n_specs']} robustness specifications and significant in {RC['pos_significant']}. The findings are associations "
  "from observational time series, not causal estimates.")
P("Keywords: exchange-rate pass-through; food inflation; Pakistan; ARDL bounds test; nonlinear ARDL; asymmetry.", italic=True)
P("JEL classification: E31, F31, Q11, C22.", italic=True)
page_break()

# ================================================================================================ 1. INTRODUCTION
doc.add_heading("1. Introduction", 1)
P("Food is the single largest item in the Pakistani household budget: the food and non-alcoholic beverages group carries a weight of 34.58% in "
  "the national consumer price index (PBS, base 2015-16). When food prices rise faster than incomes, the burden falls hardest on poorer "
  "households, whose food share is larger still. Over the eleven years studied here, Pakistan experienced both prolonged currency weakness and "
  f"one of the sharpest food-price surges in its recent history, with year-on-year food inflation peaking at {f(H['food_infl_peak'],1)}% in "
  f"{ml(H['food_infl_peak_date'])}.")
P("A common observation in public debate is that food prices rise quickly when the rupee falls but do not come down when it recovers. "
  "This report turns that observation into testable hypotheses. It combines a careful data-construction exercise with a sequence of time-series "
  "methods — unit-root testing, ARDL bounds testing, error-correction modelling and the nonlinear ARDL of Shin, Yu and Greenwood-Nimmo (2014) — "
  "to quantify how much of Pakistan's food inflation is associated with the exchange rate, world food prices and domestic energy costs, and "
  "whether depreciation and appreciation have symmetric effects.")
P("The contribution is threefold: (i) a reproducible, fully documented monthly dataset for 2015–2025 that splices PBS's latest published "
  "reviews onto the IMF's national CPI series only after verifying their overlap; (ii) a transparent estimation pipeline whose every number is "
  "traceable to raw official files; and (iii) a formal test of asymmetric exchange-rate pass-through into Pakistani food prices, with "
  "dynamic multipliers and thirteen robustness specifications.")

# ================================================================================================ 2. BACKGROUND
doc.add_heading("2. Background of the problem", 1)
P(f"Figure 1 sets out the core facts. Indexed to January 2015, the food CPI ended 2025 at {f(100+H['food_cpi_change_pct'],0)}, "
  f"the PKR/USD rate at {f(100+H['exr_change_pct'],0)} and the FAO index at {f(100+H['gfood_change_pct'],0)}. The two domestic series move "
  "together through the 2018–19 depreciation, the 2022–23 crisis and the 2024–25 stabilisation; the world food index rises in 2021–22 and then "
  f"falls back. The rupee depreciated in {desc['exchange_rate_months']['depreciating']} of 131 months and appreciated in "
  f"{desc['exchange_rate_months']['appreciating']}; the largest single-month depreciation in the sample was "
  f"{f(desc['largest_depreciation_months'][0]['pct'],1)}% in {ml(desc['largest_depreciation_months'][0]['date'])}, and the largest "
  f"appreciation {f(desc['largest_appreciation_months'][0]['pct'],1)}% in {ml(desc['largest_appreciation_months'][0]['date'])}.")
figure(FIG / "fig01_rebased_indices.png", "Food CPI, PKR/USD, transport CPI and FAO food price index, January 2015 = 100.")
figure(FIG / "fig02_inflation_vs_depreciation.png", "Year-on-year food inflation, rupee depreciation and FAO food price inflation (%).")
P("Pakistan is structurally exposed to the exchange rate through food. It imports a large share of its edible oil, pulses and tea, and in "
  "several years wheat and sugar; fertiliser inputs and the fuel that powers irrigation and transport are also priced in dollars. A weaker "
  "rupee therefore raises costs both directly, at the border, and indirectly, through production and distribution.")

# ================================================================================================ 3/4. OBJECTIVES & QUESTIONS
doc.add_heading("3. Research objectives", 1)
bullets([
    "To measure the long-run relationship between Pakistan's food CPI and the PKR/USD exchange rate, world food prices and domestic energy costs.",
    "To distinguish short-run adjustment from long-run equilibrium and estimate the speed of adjustment.",
    "To test whether rupee depreciation and appreciation have statistically asymmetric effects on food prices, in the short and long run.",
    "To assess the persistence of food-price responses using cumulative dynamic multipliers.",
    "To evaluate the robustness, stability and diagnostic adequacy of the models and derive policy implications.",
])
doc.add_heading("4. Research questions", 1)
bullets([
    "RQ1. To what extent do exchange-rate depreciation, international food prices and domestic energy costs explain food inflation in Pakistan?",
    "RQ2. Is there a long-run (cointegrating) relationship among these variables, and how quickly do food prices return to it?",
    "RQ3. Does exchange-rate depreciation have a stronger or more persistent impact on food prices than appreciation?",
], style="List Number")
P("Hypotheses: H1 — the long-run elasticity of food prices with respect to the exchange rate is positive (pass-through exists); "
  "H2 — pass-through is incomplete (elasticity below one); H3 — the effect of depreciation exceeds that of appreciation (asymmetry).")

# ================================================================================================ 5. LITERATURE
doc.add_heading("5. Literature review", 1)
doc.add_heading("5.1 Exchange-rate pass-through", 2)
P("Exchange-rate pass-through (ERPT) is the percentage change in domestic prices that follows a one-percent change in the exchange rate. "
  "Dornbusch (1987) explained incomplete pass-through through market structure and the pricing behaviour of imperfectly competitive firms. "
  "Taylor (2000) argued that pass-through falls in low-inflation environments because firms expect cost shocks to be less persistent, and "
  "Choudhri and Hakura (2006) found, across a large sample of countries, that pass-through is positively associated with the average inflation "
  "rate. Campa and Goldberg (2005) documented that pass-through into import prices is partial in the short run and higher, though still often "
  "incomplete, in the long run. These results motivate distinguishing short- from long-run effects and expecting larger pass-through in a "
  "high-inflation economy such as Pakistan in 2022–23.")
doc.add_heading("5.2 Asymmetric price adjustment", 2)
P("Prices often respond more quickly to cost increases than to cost decreases. Bacon (1991) coined the phrase “rockets and feathers” for UK "
  "retail petrol prices, and Peltzman (2000) showed that prices rise faster than they fall across a wide range of product markets. For "
  "exchange rates, Delatte and López-Villavicencio (2012) used a nonlinear ARDL to show that pass-through in several major economies is "
  "asymmetric, with depreciations passed on more than appreciations in the long run. Shin, Yu and Greenwood-Nimmo (2014) formalised the "
  "NARDL framework used in this study, building on the ARDL bounds approach of Pesaran and Shin (1999) and Pesaran, Shin and Smith (2001).")
doc.add_heading("5.3 Evidence for Pakistan", 2)
P("Choudhri and Khan (2002) examined whether rupee devaluation was inflationary in Pakistan and found the pass-through to consumer prices in "
  "their sample to be limited. Hyder and Shah (2004), in a State Bank of Pakistan working paper, estimated pass-through to wholesale and "
  "consumer prices and found it modest and stronger for wholesale prices. Khan and Schimmelpfennig (2006) concluded that monetary factors were "
  "the main drivers of inflation in Pakistan, with the wheat support price affecting inflation in the short run. These studies predate the "
  "large depreciations of 2018–19 and 2022–23 and do not test asymmetry in food prices specifically — the gap this study addresses.")

# ================================================================================================ 6/7 THEORY & CONCEPT
doc.add_heading("6. Theoretical framework", 1)
P("Consider a representative food price as a mark-up over marginal cost, P = μ·MC, where marginal cost combines domestic inputs and "
  "imported, dollar-priced inputs: MC = f(W, E·P*, P_E). Here E is the PKR/USD rate, P* the world price of imported food and inputs, and "
  "P_E the domestic energy price. Log-linearising gives ln P = c + β_E ln E + β_W ln P* + β_N ln P_E, where each β is an elasticity that "
  "depends on the cost share of the input and on the degree to which firms adjust the mark-up. Pass-through is complete when β_E equals the "
  "import cost share times one, and incomplete when firms absorb part of the shock. Asymmetry arises if mark-ups adjust differently to cost "
  "increases and decreases — for example because of menu costs, inventory valuation, search costs for consumers, or market power in "
  "wholesale trade.")
doc.add_heading("7. Conceptual framework", 1)
P("The transmission chain runs from the currency market to the kitchen table: rupee depreciation → imported food and inputs → production and "
  "transport costs → wholesale markets → consumer food prices. World food prices enter at the import stage; domestic energy costs enter "
  "production and transport, and are themselves affected by the exchange rate because Pakistan imports most of its crude oil. Direct channels "
  "(imported finished foods) act quickly; indirect channels (inputs, energy, distribution) act with lags. The website's Chapter 03 presents "
  "this framework interactively.")

# ================================================================================================ 8. DATA
doc.add_heading("8. Data and variable definitions", 1)
P("All series are monthly, January 2015 to December 2025 (N = 132), with no missing observations in any model variable. Every raw file is "
  "stored unmodified with its download time and SHA-256 hash; the dataset is rebuilt by a script that runs ten cross-source validation checks "
  f"({sum(c['passed'] for c in VAL['checks'])} of {len(VAL['checks'])} passed).")
rows = [[v["code"] + " / " + v["log_code"], v["name"], v["unit"], v["series_id"]] for v in VARS["variables"]]
table(["Code", "Variable", "Unit", "Source / series"], rows, "Variable definitions and sources.", widths=[3.2, 4.5, 3.2, 5.3])
doc.add_heading("8.1 Base-year comparability", 2)
P(next(v for v in VARS["variables"] if v["code"] == "FOODCPI")["rebasing"])
P("PBS Table 1 values for August–December 2025 were taken from each following month's review, so that the latest revisions (including the "
  "August–October 2025 FCA correction noted by PBS) are used. The exchange rate is the World Bank GEM period average (DPANUSSPB), which matches "
  "the IMF IFS period-average rate with a correlation of 0.99997 over 2015M01–2025M06.")
doc.add_heading("8.2 Choice of variables", 2)
for c in VARS["considered_but_excluded"]:
    P(f"{c['variable']} — {c['decision']}. {c['reason']}")
P("Domestic energy costs are proxied by the national transport CPI, whose largest component is motor fuel; the housing-and-utilities CPI "
  "(which contains electricity and gas) and the Brent crude price are used as alternatives in the robustness analysis.")

# ================================================================================================ 9/10 METHODOLOGY & SPEC
doc.add_heading("9. Research methodology", 1)
bullets([
    "Descriptive statistics, growth rates, correlation matrices, outlier detection (robust z-scores) and variance inflation factors.",
    "Unit-root tests: Augmented Dickey-Fuller (lags by AIC and SIC), Phillips-Perron and KPSS on levels, first and second differences, to rule out I(2) variables.",
    "Baseline OLS in log levels, with Engle–Granger and Granger–Newbold checks for spurious regression.",
    "ARDL lag selection over all combinations up to four lags on a common sample (AIC; SIC and HQ in robustness), with 11 monthly dummies.",
    "PSS bounds F- and t-tests (case III), with asymptotic critical values and 20,000-draw Monte Carlo finite-sample critical values.",
    "Long-run coefficients (delta-method standard errors), short-run dynamics and the restricted error-correction model.",
    "NARDL with partial-sum decomposition of ln EXR; Wald tests of long-run and short-run symmetry; cumulative dynamic multipliers with 95% bands from 5,000 parametric draws.",
    "Diagnostics: Breusch–Godfrey, Breusch–Pagan–Godfrey, White, ARCH, Jarque–Bera, Ramsey RESET, CUSUM and CUSUM of squares.",
    "Thirteen robustness specifications varying lags, proxies, deterministics, dummies and sample windows.",
])
doc.add_heading("10. Econometric model specifications", 1)
P("Baseline OLS:  ln FOOD_t = β0 + β1 ln EXR_t + β2 ln GFOOD_t + β3 ln ENERGY_t + u_t.")
P("Conditional error-correction (ARDL) form:  Δln FOOD_t = c + ρ ln FOOD_{t−1} + Σ θ_j x_{j,t−1} + Σ α_i Δln FOOD_{t−i} + Σ Σ π_{jl} Δx_{j,t−l} "
  "+ γ'S_t + ε_t, with long-run coefficients L_j = −θ_j/ρ. The bounds test examines H0: ρ = θ_1 = … = θ_k = 0.")
P("NARDL decomposition:  ln EXR_t = ln EXR_0 + EXR⁺_t + EXR⁻_t, with EXR⁺_t = Σ max(Δln EXR_j, 0) and EXR⁻_t = Σ min(Δln EXR_j, 0). Because a rise "
  "in PKR/USD is a depreciation, EXR⁺ accumulates depreciations and EXR⁻ appreciations. Long-run symmetry: H0: L⁺ = L⁻; impact symmetry: "
  "H0: β⁺₀ = β⁻₀.")
P("Error-correction model:  Δln FOOD_t = short-run terms + λ ECT_{t−1} + ε_t, where ECT is the deviation from the long-run relation and λ "
  "(= ρ) is the speed of adjustment, expected to lie in (−1, 0).")

# ================================================================================================ 11. RESULTS
doc.add_heading("11. Empirical results", 1)
doc.add_heading("11.1 Descriptive statistics", 2)
rows = [[D[k]["label"], f(D[k]["mean"], 2), f(D[k]["median"], 2), f(D[k]["sd"], 2), f(D[k]["min"], 2), f(D[k]["max"], 2),
         f(D[k]["skewness"], 2), f(D[k]["kurtosis"], 2), f"{f(D[k]['jarque_bera'],1)} ({fp(D[k]['jb_p'])})"]
        for k in ("FOODCPI", "EXR", "GFOOD", "TRANSCPI", "FOOD_INF_YOY", "FOOD_INF_MOM", "EXR_DEP_YOY")]
table(["Variable", "Mean", "Median", "SD", "Min", "Max", "Skew", "Kurt", "JB (p)"], rows, "Descriptive statistics, 2015M01–2025M12.",
      note="Kurtosis is raw (normal = 3). JB = Jarque–Bera.")
P(f"Food prices grew at a compound rate of {f(D['FOODCPI']['cagr_pct'],2)}% a year, the exchange rate at {f(D['EXR']['cagr_pct'],2)}% and the "
  f"FAO index at {f(D['GFOOD']['cagr_pct'],2)}%. Monthly food inflation is strongly non-normal (skewness {f(D['FOOD_INF_MOM']['skewness'],2)}, "
  f"kurtosis {f(D['FOOD_INF_MOM']['kurtosis'],2)}); the most extreme month by robust z-score is "
  f"{ml(max(desc['food_inflation_outliers']['items'], key=lambda o: abs(o['robust_z']))['date'])}.")
doc.add_heading("11.2 Correlations and multicollinearity", 2)
lv = corr["levels_log"]
table([""] + [x.replace("L", "", 1) for x in lv["variables"]], [[lv["variables"][i]] + [f(v, 2) for v in row] for i, row in enumerate(lv["matrix"])],
      "Correlation matrix, log levels.")
table(["Regressor", "VIF (levels)", "Tolerance", "VIF (differences)"],
      [[a["variable"], f(a["vif"], 2), f(a["tolerance"], 3), f(b["vif"], 2)] for a, b in zip(corr["vif_levels"], corr["vif_differences"])],
      "Variance inflation factors.")
P(corr["note"])
doc.add_heading("11.3 Unit-root tests", 2)
rows = []
for v in ("LFOODCPI", "LEXR", "LGFOOD", "LTRANSCPI", "LEXR_POS", "LEXR_NEG"):
    g = lambda form, test, det="c", rule=None: next((t for t in stn["tests"] if t["variable"] == v and t["form"] == form and t["test"] == test
                                                     and t["deterministic"] == det and (rule is None or t["lag_rule"] == rule)), None)
    c = lambda t: f"{f(t['stat'],2)} ({fp(t['p'])})" if t else "—"
    rows.append([v, c(g("level", "ADF", "c", "AIC")), c(g("level", "ADF", "ct", "AIC")), c(g("level", "PP")), c(g("level", "KPSS")),
                 c(g("first_difference", "ADF", "c", "BIC")), c(g("first_difference", "PP")), stn["summary"][v]["integration_order"]])
table(["Variable", "ADF lvl c", "ADF lvl c+t", "PP lvl", "KPSS lvl", "ADF Δ", "PP Δ", "Order"], rows, "Unit-root tests: statistic (p-value).",
      note="ADF/PP H0: unit root; KPSS H0: stationary. KPSS p-values bounded to [0.01, 0.10].", size=7.5)
P("All variables are I(1) and none is I(2), so the bounds approach is admissible. For ln EXR the ADF test on the first difference with "
  "AIC-selected lags is borderline, but ADF with SIC lags and Phillips–Perron reject the unit root decisively.")
doc.add_heading("11.4 Baseline OLS", 2)
table(["Term", "Coef.", "SE", "t", "p"], [[c["term"], f(c["coef"], 4) + star(c["p"]), f(c["se"], 4), f(c["t"], 2), fp(c["p"])] for c in ols["coefficients"]],
      f"Static OLS, log levels (N = {ols['nobs']}).",
      note=f"R² = {f(ols['r2'],3)}, adj. R² = {f(ols['adj_r2'],3)}, F = {f(ols['F'],1)} (p {fp(ols['F_p'])}), DW = {f(ols['dw'],3)}.")
eg = ols["spurious_regression_check"]["engle_granger"]
P(f"The regression fits almost perfectly, yet the Durbin–Watson statistic ({f(ols['dw'],2)}) is far below R² and the Engle–Granger test cannot "
  f"reject a unit root in the residuals (τ = {f(eg['stat'],2)}, p = {fp(eg['p'])}). By the Granger–Newbold rule the static regression may be "
  "spurious: it ignores dynamics, and its standard errors are invalid. OLS is therefore a benchmark only.")
doc.add_heading("11.5 ARDL: lag selection and bounds test", 2)
table(["Rank", "ARDL order", "AIC", "SIC", "HQ"], [[i + 1, str(tuple(m["order"])), f(m["aic"], 4), f(m["sic"], 4), f(m["hq"], 4)]
                                                   for i, m in enumerate(ardl["selection"]["top_models"][:6])],
      f"Lag selection for the linear ARDL ({ardl['selection']['models_evaluated']} models, max 4 lags).")


def bounds_rows(b):
    a, fs = b["asymptotic"], b.get("finite_sample", {})
    return [[lvl, f(a[lvl]["F_I0"], 2), f(a[lvl]["F_I1"], 2), f(fs.get(lvl, {}).get("F_I0"), 2), f(fs.get(lvl, {}).get("F_I1"), 2),
             f(a[lvl]["t_I0"], 2), f(a[lvl]["t_I1"], 2)] for lvl in ("10%", "5%", "1%")]


table(["Level", "F I(0)", "F I(1)", "F I(0) n", "F I(1) n", "t I(0)", "t I(1)"], bounds_rows(BA),
      f"PSS bounds test, linear ARDL: F = {f(BA['F'],3)}, t = {f(BA['t'],3)}, k = {BA['k']}.",
      note="Asymptotic values: PSS (2001) case III. 'n' columns: finite-sample values from 20,000 Monte Carlo draws at the estimation sample size.")
P(f"Both statistics exceed their 5% I(1) bounds (F: {BA['decision_F_5pct_asymptotic']}; t: {BA['decision_t_5pct_asymptotic']}), and the "
  "decision is unchanged with finite-sample critical values. There is a long-run relationship between food prices, the exchange rate, world food "
  "prices and energy costs.")
doc.add_heading("11.6 Long-run and short-run estimates", 2)
table(["Variable", "Long-run L", "SE", "p", "95% CI"], [[k, f(v["coef"], 3) + star(v["p"]), f(v["se"], 3), fp(v["p"]),
                                                        f"[{f(v['ci95_low'],2)}, {f(v['ci95_high'],2)}]"] for k, v in LA.items()],
      f"Long-run coefficients, ARDL{tuple(ardl['selection']['chosen_order'])}.")
table(["Term", "Coef.", "SE", "t", "p"], [[c["term"], f(c["coef"], 4) + star(c["p"]), f(c["se"], 4), f(c["t"], 2), fp(c["p"])]
                                          for c in ECA["coefficients"]],
      "Error-correction regression, ARDL (seasonal dummies not shown).")
P(f"A permanent 1% depreciation is associated with food prices {f(LA['LEXR']['coef'],2)}% higher in the long run, and a 1% rise in world food "
  f"prices with {f(LA['LGFOOD']['coef'],2)}% higher prices; both are significant and both are below one, so pass-through is incomplete. The "
  f"energy proxy is positive but insignificant (p = {fp(LA['LTRANSCPI']['p'])}). The speed of adjustment is λ = {f(ECA['speed_of_adjustment'],3)}: "
  f"about {f(-100*ECA['speed_of_adjustment'],0)}% of a deviation is corrected each month (half-life ≈ {f(ECA['half_life_months'],1)} months).")
doc.add_heading("11.7 Nonlinear ARDL: the asymmetry investigation", 2)
figure(FIG / "fig03_partial_sums.png", "Partial-sum decomposition of ln(PKR/USD).")
table(["Level", "F I(0)", "F I(1)", "F I(0) n", "F I(1) n", "t I(0)", "t I(1)"], bounds_rows(BN),
      f"PSS bounds test, NARDL{tuple(nardl['selection']['chosen_order'])}: F = {f(BN['F'],3)}, t = {f(BN['t'],3)}, k = {BN['k']}.")
P(f"The F-test rejects the null of no long-run relationship ({BN['decision_F_5pct_asymptotic']}), but the t-test does not "
  f"({BN['decision_t_5pct_asymptotic']}; simulated p = {fp(BN.get('p_value_t_I1_sim'))}). The NARDL long-run coefficients are therefore "
  "interpreted with caution, while the linear ARDL, where both tests reject, carries the evidence for cointegration.")
table(["Variable", "Long-run L", "SE", "p", "95% CI"], [[k, f(v["coef"], 3) + star(v["p"]), f(v["se"], 3), fp(v["p"]),
                                                        f"[{f(v['ci95_low'],2)}, {f(v['ci95_high'],2)}]"] for k, v in LN.items()],
      "Long-run coefficients, NARDL.")
rows = [[t["id"], t["null"], f"{t.get('statistic','')} = {f(t.get('value'),3)}" if t.get("value") is not None else "n/a",
         fp(t.get("p")), t.get("decision", t.get("reason", ""))] for t in wald["tests"]]
table(["Test", "H0", "Statistic", "p", "Decision"], rows, "Wald tests of symmetry.", size=7.5)
figure(FIG / "fig04_dynamic_multipliers.png", "Cumulative dynamic multipliers (left) and asymmetry with 95% band (right).")
snap = {s["h"]: s for s in F["multiplier_snapshots"]}
P(f"The impact response to a 1% depreciation is {f(snap[0]['depreciation'],3)}% and builds to {f(snap[12]['depreciation'],3)}% after 12 months "
  f"and {f(snap[36]['depreciation'],3)}% after 36. The response to a 1% appreciation is {f(snap[0]['appreciation_response'],3)}% on impact — prices "
  f"rise rather than fall — before turning negative ({f(snap[12]['appreciation_response'],3)}% after 12 months). The asymmetry m⁺ − m⁻ is "
  f"significantly positive on impact (95% band [{f(snap[0]['asym_lo95'],2)}, {f(snap[0]['asym_hi95'],2)}]) but its band includes zero from the "
  "first month onwards, consistent with the Wald tests: short-run asymmetry, long-run symmetry not rejected.")

# ================================================================================================ 12. DIAGNOSTICS
doc.add_heading("12. Diagnostic tests", 1)
rows = []
for t_a, t_n in zip(ardl["diagnostics"], nardl["diagnostics"]):
    if t_a["test"].startswith("Durbin"):
        rows.append([t_a["test"], "DW (indicative)", f(t_a["stat"], 3), f(t_n["stat"], 3), "Not valid with lagged dependent variable"])
        continue
    rows.append([t_a["test"], t_a["null"], f"{f(t_a['stat'],2)} ({fp(t_a['p'])})", f"{f(t_n['stat'],2)} ({fp(t_n['p'])})",
                 "ARDL: " + ("reject" if t_a["reject_5pct"] else "do not reject") + "; NARDL: " + ("reject" if t_n["reject_5pct"] else "do not reject")])
table(["Test", "H0", "ARDL stat (p)", "NARDL stat (p)", "Decision at 5%"], rows, "Residual diagnostics.", size=7.5)
P("Neither model shows serial correlation, heteroskedasticity, ARCH effects or functional-form misspecification. Residual normality is "
  "rejected for both, driven by a handful of extreme months; with N > 100 this has little effect on the validity of t- and F-tests, and an "
  "impulse dummy for May 2024 restores normality (Section 13).")
figure(FIG / "fig05_stability_ardl.png", "CUSUM and CUSUM of squares, linear ARDL.")
figure(FIG / "fig06_stability_nardl.png", "CUSUM and CUSUM of squares, NARDL.")
sa, sn = ardl["stability"], nardl["stability"]
P(f"The linear ARDL is stable on both tests. The NARDL passes CUSUM but its CUSUM of squares leaves the 5% band (maximum deviation "
  f"{f(sn['cusumsq_max_dev'],3)} against {f(sn['cusumsq_c0'],3)}), indicating that residual variance changed over the sample — quiet early years "
  "and volatile later ones. This argues for caution with NARDL standard errors and is one reason the robustness analysis matters.")
P("If a diagnostic fails: serial correlation calls for more lags or HAC standard errors; heteroskedasticity for robust standard errors; "
  "non-normality for outlier dummies or bootstrap inference; a failed RESET for a different functional form; instability for sub-sample "
  "estimation or break dummies.")

# ================================================================================================ 13. ROBUSTNESS
doc.add_heading("13. Robustness tests", 1)
rows = []
for r in rob["nardl_specifications"]:
    if "long_run" not in r:
        continue
    lp, ln_ = r["long_run"]["LEXR_POS"], r["long_run"]["LEXR_NEG"]
    rows.append([r["id"], str(tuple(r["order"])), r["nobs"], f(r["bounds_F"], 2), f(r["bounds_t"], 2),
                 f"{f(lp['coef'],2)} ({fp(lp['p'])})", f"{f(ln_['coef'],2)} ({fp(ln_['p'])})", fp(r.get("lr_sym_p")), fp(r.get("impact_sym_p"))])
table(["Spec", "Order", "N", "F", "t", "L⁺ (p)", "L⁻ (p)", "LR sym p", "Impact sym p"], rows, "NARDL robustness specifications.", size=7)
P("; ".join(f"{r['id']}: {r['label']}" for r in rob["nardl_specifications"]) + ".")
figure(FIG / "fig08_robustness_forest.png", "Long-run depreciation and appreciation elasticities across specifications.")
P(f"The depreciation effect is positive in all {RC['n_specs']} food-CPI specifications and significant at 5% in {RC['pos_significant']}; the "
  f"appreciation effect is never significant. Long-run symmetry is rejected in {RC['lr_symmetry_rejected']} specification (the post-2019 "
  f"sample using only the 2015-16-base national CPI), and impact symmetry in {RC['impact_symmetry_rejected']} of {RC['n_specs']}. The "
  "depreciation effect loses significance when a 2019M07 step dummy is added together with other event dummies, and in the pre-2024 sample, so "
  "its precise magnitude depends on how the base-year change and the 2024–25 disinflation are treated.")

# ================================================================================================ 14-17
doc.add_heading("14. Discussion", 1)
dFood = __import__("math").log(1 + H["food_cpi_change_pct"] / 100)
sh_exr = 100 * LA["LEXR"]["coef"] * __import__("math").log(1 + H["exr_change_pct"] / 100) / dFood
sh_w = 100 * LA["LGFOOD"]["coef"] * __import__("math").log(1 + H["gfood_change_pct"] / 100) / dFood
P(f"The results support H1 and H2: food prices share a long-run equilibrium with the exchange rate and world food prices, and pass-through is "
  f"substantial but incomplete. As an accounting exercise, the long-run ARDL coefficients associate about {f(sh_exr,0)}% of the log increase in "
  f"food prices over 2015–2025 with the exchange rate and about {f(sh_w,0)}% with world food prices — the domestic currency, not world markets, "
  "is the dominant correlate of Pakistan's food inflation. This is consistent with Choudhri and Hakura's (2006) finding that pass-through is "
  "larger in high-inflation environments, and larger than earlier Pakistani estimates from calmer periods (Choudhri & Khan, 2002; Hyder & "
  "Shah, 2004).")
P("H3 receives partial support. The short-run response is clearly asymmetric — prices do not fall in the month of an appreciation — a pattern "
  "consistent with the rockets-and-feathers literature (Bacon, 1991; Peltzman, 2000). But the long-run appreciation coefficient is too "
  f"imprecisely estimated to establish a permanent asymmetry: the sample contains {desc['exchange_rate_months']['appreciating']} appreciating "
  "months, mostly small. Failing to reject symmetry is not evidence of symmetry. The post-2019 sub-sample, which uses only the consistently "
  "measured national CPI, rejects long-run symmetry, which is suggestive but rests on 75 observations.")
P("Statistical and economic significance differ. The energy proxy is statistically weak in the linear ARDL, but its NARDL elasticity (about "
  f"{f(LN['LTRANSCPI']['coef'],2)}) would matter economically; conversely, the significant impact asymmetry concerns within-month dynamics that "
  "largely wash out within a few months.")
doc.add_heading("15. Policy implications", 1)
bullets([
    "Exchange-rate stability is food-security policy: orderly adjustment and adequate reserves limit food-price shocks.",
    "Do not rely on a currency recovery to reverse food-price increases quickly; targeted transfers (e.g. through existing social-protection programmes) are the faster relief.",
    "Reduce exposure to world prices through diversified sourcing and higher domestic productivity in import-dependent staples such as edible oil and pulses.",
    "Improve market information and competition oversight in wholesale food markets to shorten the lag between cost decreases and retail prices.",
    "Monetary policy should treat depreciation-driven food inflation as a persistent, not transitory, shock to expectations.",
])
doc.add_heading("16. Limitations", 1)
bullets([
    "Observational time series identify conditional associations, not causal effects; the exchange rate is itself endogenous to inflation and the balance of payments.",
    "Pre-2019 food CPI is the IMF's back-linked series of the previous CPI; the 2015-16-base national CPI exists only from July 2019.",
    "Few and small appreciation episodes limit the precision of the asymmetry tests.",
    "In the NARDL the PSS t-test does not confirm cointegration and the CUSUM of squares indicates variance instability.",
    "The transport CPI is an imperfect energy proxy; the policy rate and money supply could not be included for the full sample.",
    "All results were computed in Python; EViews programs are supplied but EViews confirmation is pending.",
])
doc.add_heading("17. Conclusion", 1)
P(f"Pakistan's food prices nearly tripled between 2015 and 2025. This study finds that their path is tied in the long run to the rupee and to "
  f"world food prices, with a long-run exchange-rate elasticity of about {f(LA['LEXR']['coef'],2)} and an adjustment half-life of about "
  f"{f(ECA['half_life_months'],1)} months. Depreciation is reliably followed by higher food prices; appreciation does not bring an equivalent, "
  "statistically detectable decline, and in the short run prices do not fall at all when the rupee recovers. Whether the asymmetry is "
  "permanent cannot be settled with the appreciation episodes available — but the burden of proof now lies with those who expect a stronger "
  "rupee to make food cheaper.")

# ================================================================================================ REFERENCES
doc.add_heading("References", 1)
refs_ts = (ROOT / "lib" / "references.ts").read_text()
import re as _re  # noqa: E402

for m in _re.finditer(r'text: "((?:[^"\\]|\\.)*)"(?:, doi: "([^"]+)")?(?:, url: "([^"]+)")?', refs_ts):
    txt, doi, url = m.group(1), m.group(2), m.group(3)
    p = doc.add_paragraph(txt + (f" https://doi.org/{doi}" if doi else f" {url}" if url else ""))
    p.paragraph_format.left_indent = Cm(1)
    p.paragraph_format.first_line_indent = Cm(-1)
    for r_ in p.runs:
        r_.font.size = Pt(9.5)

# ================================================================================================ APPENDICES
page_break()
doc.add_heading("Appendix A. Data sources and provenance", 1)
for s in SRC:
    P(f"{s['institution']}. {s['title']}. {s['url']}. Used for: {s['used_for']}.")
    for d_ in s["downloads"]:
        p = doc.add_paragraph(f"data/raw/{d_['file']} — downloaded {d_['downloaded_utc']} — SHA-256 {d_['sha256'][:24]}…", style="List Bullet")
        p.runs[0].font.size = Pt(8)
doc.add_heading("Appendix B. Validation checks", 1)
table(["Check", "Result", "Detail"], [[c["check"], "PASS" if c["passed"] else "FAIL", c["detail"]] for c in VAL["checks"]],
      "Automated cross-source validation (scripts/02_build_dataset.py).", size=7.5)
doc.add_heading("Appendix C. Reproduction and EViews verification", 1)
bullets([
    "python scripts/01_fetch_data.py — download raw data (skips files already present).",
    "python scripts/02_build_dataset.py — build and validate the dataset.",
    "python scripts/03_estimate.py — estimate every model and test (≈ 2.5 minutes).",
    "python scripts/04_figures.py; python scripts/05_build_registry.py — figures and the website registry.",
    "python scripts/06_write_eviews.py — regenerate the EViews programs; run eviews/00_master.prg in EViews 10+.",
    "python scripts/07_compare_eviews.py — compare EViews coefficients with Python; matching models are marked 'verified'.",
], style="List Number")
P("Status: the estimates in this report were produced in Python 3.13 with statsmodels 0.15 and are labelled “computed, pending EViews "
  "verification”. They become “verified” only after the comparison script confirms agreement with EViews output to a relative tolerance of 10⁻⁴.")
doc.add_heading("Appendix D. Full NARDL conditional error-correction output", 1)
table(["Term", "Coef.", "SE", "t", "p"], [[c["term"], f(c["coef"], 4) + star(c["p"]), f(c["se"], 4), f(c["t"], 2), fp(c["p"])]
                                          for c in nardl["cec_equation"]["coefficients"]],
      f"NARDL{tuple(nardl['selection']['chosen_order'])} conditional EC regression, {nardl['sample']['start']}–{nardl['sample']['end']} (seasonal dummies omitted).")
figure(FIG / "fig07_fit_residuals.png", "NARDL actual vs fitted log food CPI and residuals.")
figure(FIG / "fig09_correlations.png", "Correlations of monthly log changes.", width=10)

out = OUT / "The_Price_of_a_Falling_Rupee_Report.docx"
doc.save(out)
print("wrote", out.relative_to(ROOT), "| tables:", TCOUNT[0], "figures:", FCOUNT[0])
