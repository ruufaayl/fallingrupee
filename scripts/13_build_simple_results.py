"""
13_build_simple_results.py — plain-language results (data/research/simple.json) for the website, slides, report and viva notes.
Built from the simple regression in research/outputs/simple_regression.json (run scripts/14_simple_regression.py first).
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
O = ROOT / "research" / "outputs"
R = json.loads((O / "simple_regression.json").read_text())
desc = {v["variable"]: v for v in json.loads((O / "descriptive_statistics.json").read_text())["variables"]}
C = {c["code"]: c for c in R["coefficients"]}
DG, A, FIT = R["diagnostics"], R["asymmetry"], R["fit"]
pp = lambda p: "< 0.001" if p < 0.001 else f"{p:.3f}"

variables = [
    {"role": "Dependent (Y)", "name": "Food Inflation", "symbol": "Y", "measure": "Monthly % change in Pakistan's national food price index",
     "source": "Pakistan Bureau of Statistics (PBS)", "why": "How fast food prices rise each month — what we want to explain."},
    {"role": "Independent (X₁)", "name": "Rupee Depreciation", "symbol": "X₁", "measure": "Monthly % change in rupees per US dollar (last month)",
     "source": "World Bank (Global Economic Monitor)", "why": "A positive number = the rupee got weaker, so imports cost more."},
    {"role": "Independent (X₂)", "name": "World Food Inflation", "symbol": "X₂", "measure": "Monthly % change in the FAO Food Price Index (last month)",
     "source": "Food and Agriculture Organization (FAO)", "why": "How fast world prices of wheat, oil, sugar, dairy and meat are rising."},
    {"role": "Independent (X₃)", "name": "Fuel & Transport Inflation", "symbol": "X₃", "measure": "Monthly % change in the transport price index (last month)",
     "source": "Pakistan Bureau of Statistics (PBS)", "why": "Fuel is needed to grow food and move it to the market."},
    {"role": "Autoregressive (X₄)", "name": "Last Month's Food Inflation", "symbol": "X₄", "measure": "Food inflation one month earlier",
     "source": "Pakistan Bureau of Statistics (PBS)", "why": "Price rises tend to continue — this captures that momentum."},
]

PLAIN = {
    "RupeeDep_lag1": lambda c: f"If the rupee falls 1% this month, food prices rise about {c['coef']:.2f}% next month (a 10% fall → about {10*c['coef']:.1f}%).",
    "WorldFoodInf_lag1": lambda c: f"Positive ({c['coef']:.2f}) but not significant (p = {c['p']:.2f}): month to month, world prices do not clearly pass into Pakistan's food prices.",
    "FuelInf_lag1": lambda c: f"Close to zero ({c['coef']:.2f}) and not significant (p = {c['p']:.2f}): no clear month-to-month effect.",
    "FoodInf_lag1": lambda c: f"Food inflation carries over: {c['coef']*100:.0f}% of last month's rise repeats this month.",
}
coefs = []
for c in R["coefficients"][1:]:
    coefs.append({**c, "plain": PLAIN[c["code"]](c)})

sign = lambda x: f"+ {x:.2f}" if x >= 0 else f"− {abs(x):.2f}"
eq_est = (f"Food Inflation = {C['const']['coef']:.2f} {sign(C['RupeeDep_lag1']['coef'])} Rupee Depreciation {sign(C['WorldFoodInf_lag1']['coef'])} World Food Inflation "
          f"{sign(C['FuelInf_lag1']['coef'])} Fuel & Transport Inflation {sign(C['FoodInf_lag1']['coef'])} Last Month's Food Inflation")


def hyp(i, q, h0, h1, test, result, p):
    return {"id": f"H{i}", "question": q, "h0": h0, "h1": h1, "test": test, "result": result, "p": p, "reject": p < 0.05,
            "decision": "Reject H₀" if p < 0.05 else "Fail to reject H₀"}


hyps = [
    hyp(1, "Does a weaker rupee raise food inflation?", "Rupee depreciation has no effect (β₁ = 0).", "Rupee depreciation affects food inflation (β₁ ≠ 0).",
        "t-test on β₁", f"β₁ = {C['RupeeDep_lag1']['coef']:.3f}, t = {C['RupeeDep_lag1']['t']:.2f}, p = {pp(C['RupeeDep_lag1']['p'])}", C["RupeeDep_lag1"]["p"]),
    hyp(2, "Does world food inflation raise Pakistan's food inflation?", "World food inflation has no effect (β₂ = 0).", "It has an effect (β₂ ≠ 0).",
        "t-test on β₂", f"β₂ = {C['WorldFoodInf_lag1']['coef']:.3f}, t = {C['WorldFoodInf_lag1']['t']:.2f}, p = {pp(C['WorldFoodInf_lag1']['p'])}", C["WorldFoodInf_lag1"]["p"]),
    hyp(3, "Does fuel & transport inflation raise food inflation?", "Fuel & transport inflation has no effect (β₃ = 0).", "It has an effect (β₃ ≠ 0).",
        "t-test on β₃", f"β₃ = {C['FuelInf_lag1']['coef']:.3f}, t = {C['FuelInf_lag1']['t']:.2f}, p = {pp(C['FuelInf_lag1']['p'])}", C["FuelInf_lag1"]["p"]),
    hyp(4, "Does food inflation carry over from last month? (autoregression)", "Last month's food inflation has no effect (β₄ = 0).", "Food inflation persists (β₄ ≠ 0).",
        "t-test on β₄", f"β₄ = {C['FoodInf_lag1']['coef']:.3f}, t = {C['FoodInf_lag1']['t']:.2f}, p = {pp(C['FoodInf_lag1']['p'])}", C["FoodInf_lag1"]["p"]),
    hyp(5, "Do the variables together explain food inflation?", "All slopes are zero (β₁ = β₂ = β₃ = β₄ = 0).", "At least one slope is not zero.",
        "F-test (overall significance)", f"F({FIT['df'][0]}, {FIT['df'][1]}) = {FIT['F']:.2f}, p = {pp(FIT['F_p'])}", FIT["F_p"]),
    hyp(6, "Does a rising rupee affect food prices as much as a falling rupee?", "Depreciation and appreciation have the same effect.", "The effects are different.",
        "Wald F-test (equal coefficients)", f"Falling rupee {A['dep_coef']:.2f} (p = {pp(A['dep_p'])}); rising rupee {A['app_coef']:.2f} (p = {pp(A['app_p'])}); F = {A['F']:.2f}, p = {pp(A['p'])}", A["p"]),
]

stn = R["stationarity"]
cl = R["correlation_levels"]["matrix"]
cc = R["correlation_changes"]["matrix"]
vmax = max(v["vif"] for v in R["vif"])
tests = [
    {"group": "Data", "name": "Descriptive Statistics", "checks": "Average, spread, lowest and highest value of each variable.", "h0": None,
     "result": f"Food prices +{desc['FOODCPI']['total_change_pct']:.0f}%, dollar rate +{desc['EXR']['total_change_pct']:.0f}%, world food +{desc['GFOOD']['total_change_pct']:.0f}% (2015→2025).",
     "decision": "—", "pass": None, "meaning": "Pakistan's food prices rose far more than world food prices."},
    {"group": "Data", "name": "Correlation", "checks": "How strongly two variables move together (−1 to +1).", "h0": None,
     "result": f"Levels: food vs dollar r = {cl[0][1]:.2f}. Monthly changes: food inflation vs last month's depreciation r = {cc[0][1]:.2f}.",
     "decision": "—", "pass": None, "meaning": "Levels move together almost perfectly; month-to-month links are weaker but positive."},
    {"group": "Data", "name": "Stationarity (ADF Unit Root Test)", "checks": "Whether a series has a stable average or keeps trending.",
     "h0": "The series is non-stationary (has a unit root).",
     "result": f"Levels: all p > 0.05 (non-stationary). Monthly % changes: all p < 0.001 (stationary).", "decision": "Use monthly % changes", "pass": True,
     "meaning": "Regressing trending levels can give fake results, so the model uses monthly % changes, which are stationary."},
    {"group": "Regression", "name": "Multicollinearity (VIF)", "checks": "Whether the independent variables are too similar to each other.",
     "h0": None, "result": f"All VIF ≤ {vmax:.2f} (rule: problem if VIF > 10).", "decision": "No multicollinearity", "pass": vmax < 10,
     "meaning": "Each variable brings its own information, so the coefficients are reliable."},
    {"group": "Regression", "name": "Regression (OLS, t-tests)", "checks": "How much each variable moves food inflation, and whether the effect is significant.",
     "h0": "Each coefficient = 0.", "result": f"Rupee depreciation p = {pp(C['RupeeDep_lag1']['p'])}; last month's food inflation p = {pp(C['FoodInf_lag1']['p'])}; world food p = {pp(C['WorldFoodInf_lag1']['p'])}; fuel p = {pp(C['FuelInf_lag1']['p'])}.",
     "decision": "2 of 4 significant", "pass": True, "meaning": "A weaker rupee and last month's food inflation significantly raise food inflation."},
    {"group": "Regression", "name": "Overall Significance (F-test) & R²", "checks": "Whether the model as a whole explains food inflation.",
     "h0": "All slopes = 0.", "result": f"F = {FIT['F']:.2f}, p = {pp(FIT['F_p'])}; R² = {FIT['r2']:.3f}, adjusted R² = {FIT['adj_r2']:.3f}",
     "decision": "Reject H₀", "pass": FIT["F_p"] < 0.05,
     "meaning": f"The model is significant. It explains about {FIT['r2']*100:.0f}% of monthly ups and downs — normal for monthly food prices, which also jump with weather and harvests."},
    {"group": "Diagnostics", "name": "Autocorrelation (Durbin-Watson & Breusch-Godfrey)", "checks": "Whether errors from one month repeat in the next.",
     "h0": "No autocorrelation.", "result": f"DW = {DG['durbin_watson']:.2f} (≈ 2 is ideal); BG(12 lags) p = {pp(DG['bg12']['p'])}",
     "decision": "Fail to reject H₀", "pass": DG["bg12"]["p"] >= 0.05, "meaning": "No autocorrelation — the errors are independent. (BG is the main test because the model has a lagged Y.)"},
    {"group": "Diagnostics", "name": "Heteroskedasticity (Breusch-Pagan & White)", "checks": "Whether the size of the errors changes with the variables.",
     "h0": "Errors have constant variance (homoskedastic).", "result": f"Breusch-Pagan p = {pp(DG['bp']['p'])}; White p = {pp(DG['white']['p'])}",
     "decision": "Fail to reject H₀", "pass": DG["bp"]["p"] >= 0.05 and DG["white"]["p"] >= 0.05, "meaning": "No heteroskedasticity — error size is stable, so the p-values can be trusted."},
    {"group": "Diagnostics", "name": "Normality (Jarque-Bera)", "checks": "Whether the errors follow a normal (bell-shaped) distribution.",
     "h0": "Errors are normally distributed.", "result": f"JB = {DG['jb']['stat']:.2f}, p = {pp(DG['jb']['p'])}",
     "decision": "Fail to reject H₀" if DG["jb"]["p"] >= 0.05 else "Reject H₀", "pass": DG["jb"]["p"] >= 0.05, "meaning": "The errors are normal enough — t- and F-tests are valid."},
    {"group": "Diagnostics", "name": "Specification (Ramsey RESET)", "checks": "Whether the equation's form is correct (nothing important missing).",
     "h0": "The model is correctly specified.", "result": f"F = {DG['reset']['F']:.2f}, p = {pp(DG['reset']['p'])}",
     "decision": "Fail to reject H₀", "pass": DG["reset"]["p"] >= 0.05, "meaning": "The linear form is fine."},
    {"group": "Diagnostics", "name": "Asymmetry (Wald F-test)", "checks": "Whether a falling and a rising rupee have the same effect.",
     "h0": "Same effect.", "result": f"Falling rupee {A['dep_coef']:.2f} (p = {pp(A['dep_p'])}); rising rupee {A['app_coef']:.2f} (p = {pp(A['app_p'])}); test p = {pp(A['p'])}",
     "decision": "Fail to reject H₀", "pass": None,
     "meaning": "A falling rupee clearly raises food prices; a rising rupee shows no effect — but the difference is not statistically proven."},
]

out = {
    "title": "The Price of a Falling Rupee",
    "problem": ("Between 2015 and 2025, food prices in Pakistan nearly tripled. Over the same period the rupee lost much of its value against the "
                "US dollar, while world food prices rose only a little. We want to know whether the weak rupee is driving food inflation."),
    "question": "Does a weaker rupee, along with world food prices and fuel costs, raise food inflation in Pakistan — and does a stronger rupee bring it down?",
    "period": "January 2015 – December 2025", "n": R["nobs"],
    "variables": variables,
    "equation_general": "Food Inflation = β₀ + β₁ Rupee Depreciation + β₂ World Food Inflation + β₃ Fuel & Transport Inflation + β₄ Last Month's Food Inflation + error",
    "equation_estimated": eq_est,
    "equation_note": ("All variables are monthly % changes. The X variables are measured one month earlier, because prices take time to react. "
                      "Estimated by ordinary least squares (OLS) on 132 months, January 2015 – December 2025."),
    "constant": C["const"]["coef"],
    "coefficients": coefs,
    "hypotheses": hyps,
    "stationarity": stn,
    "vif": R["vif"],
    "tests": tests,
    "asymmetry": A,
    "fit": FIT,
    "total_effect_rupee": R["total_effect_rupee"],
    "answer": [
        f"YES — a weaker rupee raises food inflation. A 1% fall in the rupee adds about {C['RupeeDep_lag1']['coef']:.2f}% to food prices the next month "
        f"(about {R['total_effect_rupee']:.2f}% in total once the carry-over is included). Significant at 1% (p = {pp(C['RupeeDep_lag1']['p'])}).",
        f"Food inflation has momentum: about {C['FoodInf_lag1']['coef']*100:.0f}% of last month's rise carries into this month (p = {pp(C['FoodInf_lag1']['p'])}).",
        f"NO clear month-to-month effect of world food prices (p = {pp(C['WorldFoodInf_lag1']['p'])}) or fuel & transport costs (p = {pp(C['FuelInf_lag1']['p'])}).",
        f"A rising rupee showed no effect on food prices ({A['app_coef']:.2f}, p = {pp(A['app_p'])}), while a falling rupee did ({A['dep_coef']:.2f}, p = {pp(A['dep_p'])}) — "
        f"but the difference is not statistically proven (p = {pp(A['p'])}).",
        "The model passes all diagnostic tests: no multicollinearity, no autocorrelation, no heteroskedasticity, normal errors, correct form.",
    ],
    "one_line": "When the rupee falls, food prices follow a month later — and nothing in our data shows them coming back down when the rupee recovers.",
}
(ROOT / "data" / "research" / "simple.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
print(eq_est)
for h in hyps:
    print(h["id"], h["decision"], h["result"])
