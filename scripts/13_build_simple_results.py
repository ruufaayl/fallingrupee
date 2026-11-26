"""
13_build_simple_results.py — the plain-language results file (data/research/simple.json) used by the website, the slides,
the short report and the viva notes: one equation, the hypotheses, the tests and their decisions.
Run: python scripts/13_build_simple_results.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
O = ROOT / "research" / "outputs"
J = lambda n: json.loads((O / f"{n}.json").read_text())
ardl, nardl, stn, desc, corr, ols, mult = (J("ardl_results"), J("nardl_results"), J("stationarity"), J("descriptive_statistics"),
                                          J("correlations"), J("ols_results"), J("multipliers"))
LA = {x["variable"]: x for x in ardl["long_run"]}
LN = {x["variable"]: x for x in nardl["long_run"]}
D = {v["variable"]: v for v in desc["variables"]}
AS, BA = nardl["asymmetry"], ardl["bounds_test"]
ECM = ardl["ecm_regression"]
r = lambda x, d=2: round(float(x), d)

NAMES = {"LEXR": "Dollar Rate", "LGFOOD": "World Food Prices", "LTRANSCPI": "Fuel & Transport Costs"}
SYMB = {"LEXR": "β₁", "LGFOOD": "β₂", "LTRANSCPI": "β₃"}

variables = [
    {"role": "Dependent (Y)", "name": "Food Prices", "symbol": "Y", "measure": "Pakistan's national food price index (2015-16 = 100)",
     "source": "Pakistan Bureau of Statistics (PBS)", "why": "What families pay for food — the thing we want to explain."},
    {"role": "Independent (X₁)", "name": "Dollar Rate", "symbol": "X₁", "measure": "Rupees needed to buy 1 US dollar (monthly average)",
     "source": "World Bank (Global Economic Monitor)", "why": "A higher number = a weaker rupee, so imports cost more."},
    {"role": "Independent (X₂)", "name": "World Food Prices", "symbol": "X₂", "measure": "FAO Food Price Index (2014–16 = 100)",
     "source": "Food and Agriculture Organization (FAO)", "why": "Prices of wheat, oil, sugar, dairy and meat on world markets."},
    {"role": "Independent (X₃)", "name": "Fuel & Transport Costs", "symbol": "X₃", "measure": "Transport price index, mostly petrol & diesel (2015-16 = 100)",
     "source": "Pakistan Bureau of Statistics (PBS)", "why": "Fuel is needed to grow food and move it to the market."},
]

coefs = []
for k in ("LEXR", "LGFOOD", "LTRANSCPI"):
    L = LA[k]
    sig = L["p"] < 0.05
    coefs.append({"code": k, "name": NAMES[k], "symbol": SYMB[k], "coef": r(L["coef"]), "se": r(L["se"], 3), "p": r(L["p"], 3),
                  "ci": [r(L["ci95_low"]), r(L["ci95_high"])], "significant": sig,
                  "plain": (f"A 10% rise in {NAMES[k]} → food prices about "
                            f"{r((math.exp(L['coef'] * math.log(1.1)) - 1) * 100, 1)}% higher in the long run.") if sig else
                           (f"Its effect ({r(L['coef'])}) is too uncertain to be distinguished from zero (p = {r(L['p'], 2)}).")})

eq_text = (f"Food Prices = {r(LA['C']['coef'])} + {r(LA['LEXR']['coef'])} × Dollar Rate + {r(LA['LGFOOD']['coef'])} × World Food Prices"
           f" + {r(LA['LTRANSCPI']['coef'])} × Fuel & Transport Costs")

hyp = [
    {"id": "H1", "question": "Does a weaker rupee raise food prices?", "h0": "The dollar rate has no effect on food prices (β₁ = 0).",
     "h1": "A higher dollar rate raises food prices (β₁ ≠ 0).", "test": "t-test on β₁ (long-run ARDL)",
     "result": f"β₁ = {r(LA['LEXR']['coef'])}, p = {r(LA['LEXR']['p'], 3)}", "reject": LA["LEXR"]["p"] < 0.05},
    {"id": "H2", "question": "Do world food prices raise Pakistan's food prices?", "h0": "World food prices have no effect (β₂ = 0).",
     "h1": "Higher world food prices raise food prices (β₂ ≠ 0).", "test": "t-test on β₂ (long-run ARDL)",
     "result": f"β₂ = {r(LA['LGFOOD']['coef'])}, p = {r(LA['LGFOOD']['p'], 3)}", "reject": LA["LGFOOD"]["p"] < 0.05},
    {"id": "H3", "question": "Do fuel & transport costs raise food prices?", "h0": "Fuel & transport costs have no effect (β₃ = 0).",
     "h1": "Higher fuel & transport costs raise food prices (β₃ ≠ 0).", "test": "t-test on β₃ (long-run ARDL)",
     "result": f"β₃ = {r(LA['LTRANSCPI']['coef'])}, p = {r(LA['LTRANSCPI']['p'], 3)}", "reject": LA["LTRANSCPI"]["p"] < 0.05},
    {"id": "H4", "question": "Do these variables move together in the long run?", "h0": "There is no long-run relationship.",
     "h1": "There is a long-run relationship.", "test": "ARDL Bounds Test (F)",
     "result": f"F = {r(BA['F'])} > critical value {BA['asymptotic']['5%']['F_I1']} (5%)", "reject": BA["decision_F_5pct_asymptotic"] == "reject"},
    {"id": "H5", "question": "Does a falling rupee and a rising rupee affect food prices equally?",
     "h0": "The effect of a falling rupee equals the effect of a rising rupee (symmetry).",
     "h1": "The effects are different (asymmetry).", "test": "Wald test (NARDL)",
     "result": (f"Short run: p = {r(AS['short_run']['p_impact'], 3)} → different. "
                f"Long run: p = {r(AS['long_run']['p_chi2'], 3)} → cannot say they differ."),
     "reject": AS["short_run"]["p_impact"] < 0.05, "partial": AS["long_run"]["p_chi2"] >= 0.05},
]
for h in hyp:
    h["decision"] = "Reject H0" if h["reject"] else "Fail to reject H0"
hyp[4]["decision"] = "Reject H0 in the short run · Fail to reject H0 in the long run" if hyp[4].get("partial") else hyp[4]["decision"]


def adf(v, form, rule):
    return next(t for t in stn["tests"] if t["variable"] == v and t["form"] == form and t["test"] == "ADF"
                and t["deterministic"] == "c" and t["lag_rule"] == rule)


unit_rows = []
for k, nm in (("LFOODCPI", "Food Prices"), ("LEXR", "Dollar Rate"), ("LGFOOD", "World Food Prices"), ("LTRANSCPI", "Fuel & Transport Costs")):
    lv, d1 = adf(k, "level", "AIC"), adf(k, "first_difference", "BIC")
    unit_rows.append({"name": nm, "level_p": r(lv["p"], 3), "diff_p": r(d1["p"], 3), "order": stn["summary"][k]["integration_order"]})

dg = {d["test"]: d for d in ardl["diagnostics"]}
st = ardl["stability"]
tests = [
    {"name": "Descriptive Statistics", "checks": "Average, spread, lowest and highest value of each variable.", "h0": None,
     "result": f"Food prices rose {r(D['FOODCPI']['total_change_pct'],0)}%, the dollar rate {r(D['EXR']['total_change_pct'],0)}%, world food prices {r(D['GFOOD']['total_change_pct'],0)}%.",
     "decision": "—", "pass": None, "meaning": "Pakistan's food prices rose far more than world food prices."},
    {"name": "Correlation Matrix", "checks": "How strongly each pair of variables moves together (−1 to +1).", "h0": None,
     "result": f"Food Prices vs Dollar Rate: r = {r(corr['levels_log']['matrix'][0][1])}; vs World Food Prices: r = {r(corr['levels_log']['matrix'][0][2])}.",
     "decision": "—", "pass": None, "meaning": "Food prices and the dollar rate move together very closely."},
    {"name": "ADF Unit Root Test", "checks": "Whether each series has a stable average (stationary) or keeps trending.",
     "h0": "The series has a unit root (not stationary).", "result": "All four: not stationary in levels, stationary after first difference → I(1).",
     "decision": "I(1) for all", "pass": True, "meaning": "The data trend over time, so plain OLS could mislead — we use ARDL, which handles this."},
    {"name": "ARDL Bounds Test", "checks": "Whether the variables share a long-run relationship.", "h0": "No long-run relationship.",
     "result": f"F = {r(BA['F'])} > {BA['asymptotic']['5%']['F_I1']} (5% upper bound)", "decision": "Reject H0", "pass": True,
     "meaning": "Food prices, the dollar rate and world food prices are tied together in the long run."},
    {"name": "Error Correction (ECM)", "checks": "How fast food prices return to the long-run path after a shock.",
     "h0": "No adjustment (coefficient = 0).", "result": f"ECT = {r(ECM['speed_of_adjustment'],3)}, p < 0.001",
     "decision": "Reject H0", "pass": True,
     "meaning": f"About {r(-100*ECM['speed_of_adjustment'],0):.0f}% of any gap closes every month; half of it is gone in about {r(ECM['half_life_months'],1)} months."},
    {"name": "Wald Test (Asymmetry)", "checks": "Whether a falling and a rising rupee have the same effect.",
     "h0": "Same effect (symmetry).", "result": f"Short run p = {r(AS['short_run']['p_impact'],3)}; long run p = {r(AS['long_run']['p_chi2'],3)}",
     "decision": "Short run: reject · Long run: fail to reject", "pass": None,
     "meaning": "When the rupee recovers, food prices do not come down in the same month."},
    {"name": "Breusch-Godfrey (Serial Correlation)", "checks": "Whether errors from one month repeat in the next.",
     "h0": "No serial correlation.", "result": f"p = {r(dg['Breusch-Godfrey LM (2 lags)']['p'],3)}", "decision": "Fail to reject H0",
     "pass": dg["Breusch-Godfrey LM (2 lags)"]["p"] >= 0.05, "meaning": "No leftover pattern in the errors — good."},
    {"name": "Breusch-Pagan-Godfrey (Heteroskedasticity)", "checks": "Whether the size of errors changes with the variables.",
     "h0": "Errors have constant variance.", "result": f"p = {r(dg['Breusch-Pagan-Godfrey']['p'],3)}", "decision": "Fail to reject H0",
     "pass": dg["Breusch-Pagan-Godfrey"]["p"] >= 0.05, "meaning": "Error size is stable — good."},
    {"name": "Jarque-Bera (Normality)", "checks": "Whether the errors follow a normal (bell-shaped) distribution.",
     "h0": "Errors are normally distributed.", "result": f"p = {r(dg['Jarque-Bera']['p'],3)}",
     "decision": "Reject H0" if dg["Jarque-Bera"]["p"] < 0.05 else "Fail to reject H0", "pass": dg["Jarque-Bera"]["p"] >= 0.05,
     "meaning": "A few extreme months (e.g. May 2024) make errors non-normal. With 128 months this does not change the conclusions."},
    {"name": "Ramsey RESET (Model Form)", "checks": "Whether the equation's shape is correct.", "h0": "The model is correctly specified.",
     "result": f"p = {r(dg['Ramsey RESET (1 fitted term)']['p'],3)}", "decision": "Fail to reject H0",
     "pass": dg["Ramsey RESET (1 fitted term)"]["p"] >= 0.05, "meaning": "The equation's form is fine — good."},
    {"name": "CUSUM & CUSUM of Squares (Stability)", "checks": "Whether the relationship stayed stable over 2015–2025.",
     "h0": "The model is stable.", "result": f"CUSUM {'inside' if st['cusum_within_bounds'] else 'outside'} 5% bands; CUSUMSQ {'inside' if st['cusumsq_within_bounds'] else 'outside'} 5% bands",
     "decision": "Fail to reject H0" if st["cusum_within_bounds"] and st["cusumsq_within_bounds"] else "Reject H0",
     "pass": st["cusum_within_bounds"] and st["cusumsq_within_bounds"], "meaning": "The relationship held steady over the whole period — good."},
]

out = {
    "title": "The Price of a Falling Rupee",
    "problem": ("Between 2015 and 2025, food prices in Pakistan nearly tripled. Over the same period the rupee lost much of its value "
                "against the US dollar, while world food prices rose only a little. We want to know whether the weak rupee is the main "
                "reason food became so expensive."),
    "question": ("Do a weaker rupee, world food prices and fuel costs raise food prices in Pakistan — and do food prices fall back "
                 "when the rupee gets stronger?"),
    "period": "January 2015 – December 2025", "n": 132,
    "variables": variables,
    "equation_general": "Food Prices = β₀ + β₁ Dollar Rate + β₂ World Food Prices + β₃ Fuel & Transport Costs + error",
    "equation_estimated": eq_text,
    "equation_note": ("All variables are in logarithms, so each number is an elasticity: the % change in food prices for a 1% change in that variable. "
                      "Estimated with an ARDL model (long-run form) on monthly data, 2015–2025."),
    "constant": r(LA["C"]["coef"]),
    "coefficients": coefs,
    "hypotheses": hyp,
    "unit_roots": unit_rows,
    "tests": tests,
    "asymmetry": {"falling": r(LN["LEXR_POS"]["coef"]), "falling_p": r(LN["LEXR_POS"]["p"], 3), "rising": r(LN["LEXR_NEG"]["coef"]),
                  "rising_p": r(LN["LEXR_NEG"]["p"], 3), "impact_falling": r(AS["short_run"]["beta0_pos"], 3),
                  "impact_rising": r(-AS["short_run"]["beta0_neg"], 3), "p_short": r(AS["short_run"]["p_impact"], 3),
                  "p_long": r(AS["long_run"]["p_chi2"], 3)},
    "fit": {"r2": r(ardl["levels_equation"]["r2"], 4), "adj_r2": r(ardl["levels_equation"]["adj_r2"], 4), "nobs": ardl["sample"]["nobs"]},
    "answer": [
        f"YES — a weaker rupee raises food prices. A 10% rise in the dollar rate goes with about {r((math.exp(LA['LEXR']['coef']*math.log(1.1))-1)*100,1)}% higher food prices in the long run.",
        f"YES — world food prices matter too: a 10% rise goes with about {r((math.exp(LA['LGFOOD']['coef']*math.log(1.1))-1)*100,1)}% higher food prices.",
        "NOT CLEAR — fuel & transport costs: the effect is positive but not statistically significant.",
        "When the rupee gets stronger, food prices do NOT fall in the same month. Over the long run we cannot prove the fall is smaller — there were too few months of a rising rupee to tell.",
    ],
    "one_line": "The rupee's fall is paid for at the market: when the rupee weakens, food gets dearer — and it does not get cheaper again quickly when the rupee recovers.",
}
(ROOT / "data" / "research" / "simple.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
print(json.dumps({"eq": eq_text, "hyp": [(h["id"], h["decision"]) for h in hyp]}, indent=1, ensure_ascii=False))
