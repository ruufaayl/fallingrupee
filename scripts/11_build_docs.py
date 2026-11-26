"""
11_build_docs.py — team material in plain language: team plan, word-for-word presentation script (taken from the slide
notes so the two always match), and a viva guide per member. Writes Markdown to docs/ and a combined DOCX to deliverables/.
Run after scripts/10_build_deck.py:  python scripts/11_build_docs.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from docx import Document
from docx.shared import Pt
from pptx import Presentation

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DEL = ROOT / "deliverables"
DOCS.mkdir(exist_ok=True)
DEL.mkdir(exist_ok=True)
S = json.loads((ROOT / "data" / "research" / "simple.json").read_text())
O = ROOT / "research" / "outputs"
desc = {v["variable"]: v for v in json.loads((O / "descriptive_statistics.json").read_text())["variables"]}
C = {c["code"]: c for c in S["coefficients"]}
A, H = S["asymmetry"], {h["id"]: h for h in S["hypotheses"]}
SITE = "https://the-price-of-a-falling-rupee.vercel.app"

# ------------------------------------------------------------------------------------------ slides + notes from the deck
prs = Presentation(str(ROOT / "presentation" / "The_Price_of_a_Falling_Rupee_Deck.pptx"))
slides = []
for i, sl in enumerate(prs.slides, 1):
    note = sl.notes_slide.notes_text_frame.text if sl.has_notes_slide else ""
    m = re.match(r"\[(?:Handover to )?(MEMBER \d)[^\]]*\]\s*(.*)", note, re.S)
    texts = [sh.text_frame.text for sh in sl.shapes if sh.has_text_frame and sh.text_frame.text.strip()]
    head = next((t for t in texts if not t.isupper() and len(t) > 3 and "vercel" not in t), texts[0] if texts else "")
    slides.append({"n": i, "member": m.group(1) if m else "", "title": head.split("\n")[0], "script": (m.group(2) if m else note).strip()})
by = {k: [s for s in slides if s["member"] == k] for k in ("MEMBER 1", "MEMBER 2", "MEMBER 3")}


def rng(k):
    ns = [s["n"] for s in by[k]]
    return f"slides {min(ns)}–{max(ns)}"


# ------------------------------------------------------------------------------------------ TEAM PLAN
plan = f"""# Team Plan — The Price of a Falling Rupee

Total talk: about 12–15 minutes (≈ 4–5 minutes each), then questions.

| Member | Part | Slides | Covers |
|---|---|---|---|
| **Member 1** | Opening & set-up | {rng('MEMBER 1')} | Title, problem statement, research question, dependent & independent variables, data, the equation, hypotheses H1–H6 |
| **Member 2** | Data & tests | {rng('MEMBER 2')} | Trend graph, descriptive statistics, correlation, stationarity (ADF), multicollinearity (VIF) |
| **Member 3** | Results & conclusion | {rng('MEMBER 3')} | Regression output, hypothesis decisions, autocorrelation, heteroskedasticity, normality, RESET, asymmetry, conclusion, Q&A |

**Hand-overs** — Member 1 ends with: “Now my teammate will show the data and the tests.” Member 2 ends with: “Now my teammate will present the regression results.”

**Files to bring** — the slides (`presentation/The_Price_of_a_Falling_Rupee_Deck.pptx`), the dataset (`deliverables/Falling_Rupee_Dataset.xlsx`), the website ({SITE}).

**Rehearsal tip** — each member reads the script once aloud, then presents from the slide only. Know your numbers (see the viva guide).
"""
(DOCS / "TEAM_PLAN.md").write_text(plan)

# ------------------------------------------------------------------------------------------ SCRIPT
script = ["# Presentation Script — word for word", "", "Read naturally; the bold title is what is on the slide.", ""]
for k in ("MEMBER 1", "MEMBER 2", "MEMBER 3"):
    script += [f"## {k.title()}", ""]
    for s in slides:
        if s["member"] == k:
            script += [f"**Slide {s['n']} — {s['title']}**", "", s["script"], ""]
(DOCS / "PRESENTATION_SCRIPT.md").write_text("\n".join(script))

# ------------------------------------------------------------------------------------------ VIVA
p = lambda x: "< 0.001" if x < 0.001 else f"{x:.3f}"
REG = json.loads((O / "simple_regression.json").read_text())
DG, FIT = REG["diagnostics"], S["fit"]
rd, wf, fu, fl = C["RupeeDep_lag1"], C["WorldFoodInf_lag1"], C["FuelInf_lag1"], C["FoodInf_lag1"]
vmax = max(v["vif"] for v in S["vif"])
viva = {
    "MEMBER 1": {
        "know": [
            f"Problem: food prices +{desc['FOODCPI']['total_change_pct']:.0f}%, dollar rate +{desc['EXR']['total_change_pct']:.0f}%, world food prices +{desc['GFOOD']['total_change_pct']:.0f}% (Jan 2015 → Dec 2025).",
            "Dependent variable (Y): Food Inflation — monthly % change in the PBS national food price index.",
            "Independent variables (previous month): X₁ Rupee Depreciation (World Bank) · X₂ World Food Inflation (FAO) · X₃ Fuel & Transport Inflation (PBS) · X₄ Last Month's Food Inflation (autoregressive term).",
            "Data: monthly, Jan 2015 – Dec 2025, 132 observations, no missing values.",
            f"Equation: {S['equation_general']}",
            "Six hypotheses: H1–H4 t-tests on each β, H5 F-test on the whole model, H6 Wald F-test for asymmetry. Reject H₀ when p < 0.05.",
        ],
        "qa": [
            ("Why these variables?", "They are the main channels: a weaker rupee makes imports dearer, world prices set the cost of imported food, fuel moves food to market, and last month's inflation captures momentum."),
            ("What is the dependent variable?", "Food inflation — the thing we explain. The independent variables are the possible causes."),
            ("Why monthly % changes instead of price levels?", "Price levels keep trending upward (non-stationary). Regressing trending series can show fake relationships, so we use monthly % changes, which are stationary."),
            ("Why use last month's values for the X variables?", "Prices take time to react — shops and wholesalers re-price after costs change. Using last month also means today's food prices cannot affect the X's (no reverse causation within the month)."),
            ("What is the autoregressive term?", "Last month's food inflation (X₄). It is 'auto' because it is the dependent variable's own past value. It captures momentum — price rises tend to continue."),
            ("What does β mean?", "How many percentage points food inflation changes when that X changes by one percentage point, holding the others constant."),
            ("What are H₀ and H₁?", "H₀ (null) says no effect; H₁ (alternative) says there is an effect. We reject H₀ if the p-value is below 0.05."),
            ("Where is the data from?", "Pakistan Bureau of Statistics, World Bank and FAO — all combined month by month in our Excel file."),
        ],
    },
    "MEMBER 2": {
        "know": [
            f"Food prices grew {desc['FOODCPI']['cagr_pct']:.1f}% a year, dollar rate {desc['EXR']['cagr_pct']:.1f}%, world food {desc['GFOOD']['cagr_pct']:.1f}%; food inflation averaged {desc['FOOD_INF_MOM']['mean']:.2f}% per month.",
            f"Correlation in levels: food vs dollar r = {REG['correlation_levels']['matrix'][0][1]:.2f}. In monthly changes: food inflation vs last month's depreciation r = {REG['correlation_changes']['matrix'][0][1]:.2f}.",
            "Correlation is not causation — trending series always look correlated, which is why we test stationarity.",
            "ADF test, H₀ = non-stationary: levels p > 0.05 (non-stationary); monthly % changes p < 0.001 (stationary).",
            f"Multicollinearity: highest VIF = {vmax:.2f} (problem only if > 10) → none.",
        ],
        "qa": [
            ("What is stationarity?", "A stationary series moves around a fixed average with a stable spread. Prices keep rising, so they are non-stationary; their monthly % changes are stationary."),
            ("Why does non-stationarity matter?", "Two trending series can look strongly related even when they are not — a 'spurious regression'. That is why we tested first and then used % changes."),
            ("What is the ADF test?", "The Augmented Dickey-Fuller test. H₀: the series has a unit root (non-stationary). If p < 0.05 we reject H₀ and call it stationary."),
            ("Why is correlation in levels 0.98 but only 0.23 in changes?", "Levels share a common upward trend, which inflates correlation. Monthly changes remove the trend, so the 0.23 is the honest month-to-month link."),
            ("What is multicollinearity?", "When the X variables are so similar that the regression cannot separate their effects. It makes coefficients unstable."),
            ("What is VIF?", "Variance Inflation Factor = 1 ÷ (1 − R²) from regressing one X on the others. Above 10 is a problem; ours are all about 1–1.5."),
            ("Why is VIF low even though the rupee and fuel prices move together in levels?", "In monthly changes they move much less together (r ≈ 0.5), so each variable keeps its own information."),
        ],
    },
    "MEMBER 3": {
        "know": [
            f"Estimated equation: {S['equation_estimated']}",
            f"Rupee depreciation β₁ = {rd['coef']:.3f}, t = {rd['t']:.2f}, p = {p(rd['p'])} → significant (1% weaker rupee → food prices +{rd['coef']:.2f}% next month).",
            f"Last month's food inflation β₄ = {fl['coef']:.3f}, p = {p(fl['p'])} → significant (momentum). World food (p = {p(wf['p'])}) and fuel (p = {p(fu['p'])}) not significant.",
            f"F = {FIT['F']:.2f}, p = {p(FIT['F_p'])} → model significant. R² = {FIT['r2']:.3f}.",
            f"Diagnostics: DW = {DG['durbin_watson']:.2f}, BG p = {p(DG['bg12']['p'])} (no autocorrelation); BP p = {p(DG['bp']['p'])}, White p = {p(DG['white']['p'])} (no heteroskedasticity); JB p = {p(DG['jb']['p'])} (normal); RESET p = {p(DG['reset']['p'])} (correct form).",
            f"Asymmetry: rupee falls {A['dep_coef']:.2f} (p = {p(A['dep_p'])}); rupee rises {A['app_coef']:.2f} (p = {p(A['app_p'])}); Wald F p = {p(A['p'])} → difference not proven.",
        ],
        "qa": [
            ("What is your main finding?", f"A weaker rupee raises food inflation the next month: a 1% depreciation adds about {rd['coef']:.2f}% to food prices (p = {p(rd['p'])})."),
            ("Your R² is only 0.10 — is the model bad?", "No. Monthly food prices also jump with weather, harvests, Ramadan and policy, which no macro model fully captures. The F-test shows the model is significant, and the coefficients we care about are significant. Monthly inflation regressions typically have low R²."),
            ("What is autocorrelation and how did you test it?", f"Errors that repeat from month to month. Durbin-Watson is {DG['durbin_watson']:.2f} (close to 2 = none), and Breusch-Godfrey with 12 lags gives p = {p(DG['bg12']['p'])} — no autocorrelation. We rely on Breusch-Godfrey because DW is less reliable when the model has a lagged dependent variable."),
            ("What is heteroskedasticity?", f"When the size of the errors changes with the X's. Breusch-Pagan (p = {p(DG['bp']['p'])}) and White (p = {p(DG['white']['p'])}) both fail to reject constant variance — no heteroskedasticity."),
            ("Why are world food prices not significant?", "Their p-value is above 0.05, so we cannot separate their monthly effect from zero. Possible reasons: world price changes reach Pakistani shops slowly and unevenly, and over the whole decade world food prices rose only 23% — far less than Pakistan's food prices — so they explain little of Pakistan's food inflation."),
            ("What does 'fail to reject H₀' mean?", "We do not have enough evidence of an effect. It does not prove the effect is exactly zero."),
            ("Explain the asymmetry result.", f"When the rupee fell, food prices rose (β = {A['dep_coef']:.2f}, significant). When the rupee rose, food prices did not fall (β ≈ 0). But the test that they differ gives p = {p(A['p'])}, so we cannot prove it statistically — the rupee rose in only {A['app_months']} months."),
            ("Is this cause and effect?", "We show a tested link with a time order (the rupee moves first, food prices follow), but not a laboratory proof. We say 'associated with'."),
            ("What should policymakers do?", "Keep the rupee stable, treat a falling rupee as an early warning for food inflation, and support poor families directly rather than waiting for the rupee to recover."),
        ],
    },
}
common = [
    ("What is OLS?", "Ordinary Least Squares — it draws the line (or plane) that makes the squared errors as small as possible."),
    ("What is a p-value?", "The probability of seeing a result this strong if H₀ were true. Below 0.05 → that is unlikely, so we reject H₀."),
    ("What is the t-test vs the F-test?", "The t-test checks one coefficient at a time; the F-test checks whether all the slopes together are zero."),
    ("What software did you use?", "Answer with the software you actually used. The regression can be re-run in Excel (Data Analysis ▸ Regression) or EViews from the 'Regression Data' sheet and gives the same numbers."),
    ("One sentence summary?", S["one_line"]),
]
lines = ["# Viva Guide — simple and complete", "", "Each member: learn your **Must know** list by heart, then practise the questions aloud.", ""]
for k in ("MEMBER 1", "MEMBER 2", "MEMBER 3"):
    lines += [f"## {k.title()}", "", "**Must know**", ""] + [f"- {x}" for x in viva[k]["know"]] + ["", "**Likely questions**", ""]
    for q, a in viva[k]["qa"]:
        lines += [f"**Q: {q}**", "", f"A: {a}", ""]
lines += ["## Any member may be asked", ""]
for q, a in common:
    lines += [f"**Q: {q}**", "", f"A: {a}", ""]
lines += ["## The 30-second answer to the research question", "", *[f"{i + 1}. {a}" for i, a in enumerate(S["answer"])], ""]
(DOCS / "VIVA_GUIDE.md").write_text("\n".join(lines))

# ------------------------------------------------------------------------------------------ combined DOCX
doc = Document()
doc.styles["Normal"].font.name = "Calibri"
doc.styles["Normal"].font.size = Pt(11)
for md in ("TEAM_PLAN.md", "PRESENTATION_SCRIPT.md", "VIVA_GUIDE.md"):
    for raw in (DOCS / md).read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("|---"):
            continue
        if line.startswith("# "):
            doc.add_heading(line[2:], 1)
        elif line.startswith("## "):
            doc.add_heading(line[3:], 2)
        elif line.startswith("- "):
            doc.add_paragraph(line[2:].replace("**", ""), style="List Bullet")
        elif line.startswith("|"):
            doc.add_paragraph("  ·  ".join(c.strip().replace("**", "") for c in line.strip("|").split("|")))
        elif line.startswith("**") and line.endswith("**"):
            doc.add_paragraph().add_run(line.strip("*")).bold = True
        else:
            para = doc.add_paragraph()
            for i, part in enumerate(line.split("**")):
                para.add_run(part).bold = i % 2 == 1
    doc.add_page_break()
doc.save(DEL / "Team_Script_and_Viva_Guide.docx")
print("wrote docs/TEAM_PLAN.md, docs/PRESENTATION_SCRIPT.md, docs/VIVA_GUIDE.md, deliverables/Team_Script_and_Viva_Guide.docx")
