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
ardl = json.loads((O / "ardl_results.json").read_text())
desc = {v["variable"]: v for v in json.loads((O / "descriptive_statistics.json").read_text())["variables"]}
C = {c["code"]: c for c in S["coefficients"]}
A, H = S["asymmetry"], {h["id"]: h for h in S["hypotheses"]}
B, ECM = ardl["bounds_test"], ardl["ecm_regression"]
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
| **Member 1** | Opening & set-up | {rng('MEMBER 1')} | Title, problem statement, research question, dependent & independent variables, data sources, the equation, the hypotheses H1–H5 |
| **Member 2** | Data & tests | {rng('MEMBER 2')} | Trend graph, descriptive statistics, correlation matrix, ADF unit root test, ARDL bounds test & error correction |
| **Member 3** | Results & conclusion | {rng('MEMBER 3')} | Estimated equation, hypothesis decisions, asymmetry (Wald test), diagnostic tests, conclusion, Q&A |

**Hand-overs** — Member 1 ends with: “Now my teammate will show the data and the tests.” Member 2 ends with: “Now my teammate will present the results.”

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
viva = {
    "MEMBER 1": {
        "know": [
            f"Problem: food prices +{desc['FOODCPI']['total_change_pct']:.0f}%, dollar rate +{desc['EXR']['total_change_pct']:.0f}%, world food prices +{desc['GFOOD']['total_change_pct']:.0f}% (Jan 2015 → Dec 2025).",
            "Dependent variable (Y): Food Prices — PBS national food price index.",
            "Independent variables: X₁ Dollar Rate (World Bank) · X₂ World Food Prices (FAO) · X₃ Fuel & Transport Costs (PBS transport index).",
            "Data: monthly, Jan 2015 – Dec 2025, 132 months, no missing values.",
            f"Equation: {S['equation_general']}",
            "H₀ always says “no effect”; H₁ says “there is an effect”. Reject H₀ when p < 0.05.",
        ],
        "qa": [
            ("Why did you choose these variables?", "Because they are the three main ways a weak rupee and the outside world can push food prices: imported food and inputs (dollar rate), world market prices (FAO), and the cost of fuel to grow and move food (transport index)."),
            ("What is a dependent variable?", "The thing we want to explain — here, food prices. The independent variables are the possible causes."),
            ("Why monthly data?", "Prices change every month, and monthly data gives us 132 observations — enough to see how effects build up over time."),
            ("Why 2015 to 2025?", "It covers the recent big falls of the rupee (2019 and 2022–23) and the recovery after, with all data available from official sources."),
            ("Where did the data come from?", "Pakistan Bureau of Statistics, World Bank and FAO. All four are combined month by month in the Excel sheet we submitted."),
            ("What does β mean?", "How much food prices change, in percent, when that variable changes by 1 percent. It is called an elasticity because we use logarithms."),
            ("What is H₀ and H₁?", "H₀ is the null hypothesis — no effect. H₁ is the alternative — there is an effect. The test tells us if we have enough evidence to reject H₀."),
            ("Why logarithms?", "So the coefficients read as percentages, and so big numbers like 280 rupees and small ones like 100 index points are comparable."),
        ],
    },
    "MEMBER 2": {
        "know": [
            f"Food prices grew {desc['FOODCPI']['cagr_pct']:.1f}% a year, the dollar rate {desc['EXR']['cagr_pct']:.1f}%, world food prices {desc['GFOOD']['cagr_pct']:.1f}%.",
            f"Food inflation averaged {desc['FOOD_INF_YOY']['mean']:.1f}% and peaked at {desc['FOOD_INF_YOY']['max']:.1f}% in May 2023.",
            "Correlation Food Prices vs Dollar Rate ≈ 0.98 — very high, but correlation ≠ cause.",
            "ADF test: H₀ = not stationary. Levels p > 0.05 (trend), first differences p < 0.05 → all variables I(1).",
            f"Bounds test: F = {B['F']:.2f} > 5% critical value {B['asymptotic']['5%']['F_I1']} → reject H₀ → long-run relationship.",
            f"ECT = {ECM['speed_of_adjustment']:.2f} → about {-100*ECM['speed_of_adjustment']:.0f}% of the gap closes each month; half-life ≈ {ECM['half_life_months']:.1f} months.",
        ],
        "qa": [
            ("What is stationarity?", "A stationary series moves around a fixed average. Prices keep climbing, so they are not stationary in levels — but their monthly changes are."),
            ("Why does stationarity matter?", "Running ordinary regression on two trending series can show a relationship even when there is none (a 'spurious regression'). We had to check first."),
            ("What does I(1) mean?", "The series becomes stationary after taking the change once. ARDL works when variables are I(0) or I(1), not I(2) — ours are all I(1)."),
            ("Why ARDL and not simple OLS?", "ARDL handles trending (I(1)) data and lets effects build up over several months. Simple OLS ignores both."),
            ("What does the bounds test tell us?", "Whether the variables are tied together in the long run. Our F statistic is above the upper critical value, so yes."),
            ("What is the error correction term?", "It shows how fast food prices come back to their long-run path. Negative and significant means the relationship is stable."),
            ("High correlation — isn't that enough?", "No. Anything that rises over time looks correlated. That is why we ran the unit root and bounds tests."),
            ("How did you choose the number of lags?", "The software tried every combination up to 4 months and picked the one with the lowest Akaike Information Criterion (AIC)."),
        ],
    },
    "MEMBER 3": {
        "know": [
            f"Estimated equation: {S['equation_estimated']}",
            f"Dollar rate: {C['LEXR']['coef']:.2f}, p = {p(C['LEXR']['p'])} → reject H₀ (10% weaker rupee → ≈ 6.3% dearer food).",
            f"World food prices: {C['LGFOOD']['coef']:.2f}, p = {p(C['LGFOOD']['p'])} → reject H₀.",
            f"Fuel & transport: {C['LTRANSCPI']['coef']:.2f}, p = {p(C['LTRANSCPI']['p'])} → fail to reject H₀ (no clear effect).",
            f"Asymmetry: rupee falls 1% → food +{A['falling']:.2f}% (p = {p(A['falling_p'])}); in the month the rupee rises, food does not fall. Wald short run p = {p(A['p_short'])} (different); long run p = {p(A['p_long'])} (can't tell).",
            "Diagnostics: serial correlation ✓, heteroskedasticity ✓, RESET ✓, CUSUM stability ✓, normality ✗ (a few extreme months).",
        ],
        "qa": [
            ("What is your main finding?", "A weaker rupee clearly raises food prices: a 10% rise in the dollar rate goes with about 6.3% higher food prices in the long run."),
            ("Why is fuel & transport not significant?", "Its p-value is 0.36, above 0.05, so we cannot separate its effect from zero. The most likely reason: fuel prices move almost exactly with the rupee (correlation 0.98), so once the rupee is in the model, fuel adds little extra information."),
            ("What does 'fail to reject H₀' mean?", "We do not have enough evidence of an effect. It does not prove there is zero effect."),
            ("What is the Wald test?", "A test of whether two coefficients are equal. We used it to check if a falling rupee and a rising rupee have the same effect."),
            ("So do prices fall when the rupee recovers?", "Not in the same month — they keep rising a little. Over the long run we cannot tell, because there were only a few months when the rupee got stronger."),
            ("Normality failed — is the model wrong?", "No. A few extreme months (like May 2024) make the errors non-normal. With 128 months the tests are still reliable, and removing that month's effect gives the same conclusions."),
            ("Is this cause and effect?", "We show a strong, tested link — not a laboratory proof. Other things also move prices. We say 'associated with', not 'caused by'."),
            ("What should the government do?", "Keep the rupee stable, help poor families directly instead of waiting for the rupee to recover, and import food and inputs from more sources."),
            ("What is R² of your model?", f"{S['fit']['r2']:.3f} — the model explains almost all the movement in food prices, but in time series that is normal, so we rely on the tests instead."),
        ],
    },
}
common = [
    ("What is a p-value?", "The chance of seeing a result this strong if H₀ were true. Below 0.05 means that chance is very small, so we reject H₀."),
    ("What is the 5% significance level?", "Our cut-off: we accept a 5% risk of saying there is an effect when there is not."),
    ("What software did you use?", "A statistical package for time-series econometrics (ARDL, bounds test, diagnostics). Answer honestly with the software you actually used to run the estimates."),
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
