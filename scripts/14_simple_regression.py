"""
14_simple_regression.py — the main model of the simplified project: an OLS regression on monthly % changes with an
autoregressive term, plus the standard, easy-to-defend tests (correlation, stationarity, multicollinearity, regression
t/F/R², autocorrelation, heteroskedasticity, normality, specification, asymmetry). Writes research/outputs/simple_regression.json
and data/processed/regression_data.csv (exactly the rows used, so the regression can be re-run in Excel or EViews).

Model:  FoodInf_t = b0 + b1·RupeeDep_{t-1} + b2·WorldFoodInf_{t-1} + b3·FuelInf_{t-1} + b4·FoodInf_{t-1} + e_t
        (all variables = % change on the previous month; sample Jan 2015 – Dec 2025, N = 132)
Run: python scripts/14_simple_regression.py
"""
from __future__ import annotations

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.diagnostic import acorr_breusch_godfrey, het_breuschpagan, het_white, linear_reset
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.stattools import durbin_watson, jarque_bera
from statsmodels.tsa.stattools import adfuller

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
full = pd.read_csv(ROOT / "data" / "processed" / "pakistan_food_inflation_monthly.csv")
full.index = pd.period_range("2008-07", periods=len(full), freq="M")
r = lambda x, d=3: None if x is None or not np.isfinite(x) else round(float(x), d)

# ---------------------------------------------------------------- variables: simple monthly % changes
pc = full[["FOODCPI", "EXR", "GFOOD", "TRANSCPI"]].pct_change(fill_method=None) * 100
d = pd.DataFrame({
    "FoodInf": pc["FOODCPI"],
    "RupeeDep_lag1": pc["EXR"].shift(1),
    "WorldFoodInf_lag1": pc["GFOOD"].shift(1),
    "FuelInf_lag1": pc["TRANSCPI"].shift(1),
    "FoodInf_lag1": pc["FOODCPI"].shift(1),
}).loc["2015-01":"2025-12"]
assert d.notna().all().all() and len(d) == 132
X_NAMES = {"RupeeDep_lag1": "Rupee Depreciation (last month)", "WorldFoodInf_lag1": "World Food Inflation (last month)",
           "FuelInf_lag1": "Fuel & Transport Inflation (last month)", "FoodInf_lag1": "Food Inflation (last month)"}
SYM = {"RupeeDep_lag1": "β₁", "WorldFoodInf_lag1": "β₂", "FuelInf_lag1": "β₃", "FoodInf_lag1": "β₄"}

out_csv = d.copy()
out_csv.insert(0, "Month", [str(p) for p in d.index])
out_csv.to_csv(ROOT / "data" / "processed" / "regression_data.csv", index=False, float_format="%.6f")

# ---------------------------------------------------------------- 1. regression
X = sm.add_constant(d[list(X_NAMES)])
m = sm.OLS(d["FoodInf"], X).fit()
coefs = [{"code": "const", "name": "Constant", "symbol": "β₀", "coef": r(m.params["const"]), "se": r(m.bse["const"]),
          "t": r(m.tvalues["const"], 2), "p": r(m.pvalues["const"]), "significant": bool(m.pvalues["const"] < 0.05)}]
for k, nm in X_NAMES.items():
    ci = m.conf_int().loc[k]
    coefs.append({"code": k, "name": nm, "symbol": SYM[k], "coef": r(m.params[k]), "se": r(m.bse[k]), "t": r(m.tvalues[k], 2),
                  "p": r(m.pvalues[k]), "ci": [r(ci[0]), r(ci[1])], "significant": bool(m.pvalues[k] < 0.05)})
persist = m.params["FoodInf_lag1"]
total_exr = m.params["RupeeDep_lag1"] / (1 - persist)

# robustness: Newey-West (HAC) standard errors, and a May-2024 outlier dummy
hac = sm.OLS(d["FoodInf"], X).fit(cov_type="HAC", cov_kwds={"maxlags": 6})
Xd = X.assign(D_2024M05=(d.index == pd.Period("2024-05")).astype(float))
md = sm.OLS(d["FoodInf"], Xd).fit()

# ---------------------------------------------------------------- 2. correlation (monthly % changes and levels)
cm = d[["FoodInf", "RupeeDep_lag1", "WorldFoodInf_lag1", "FuelInf_lag1", "FoodInf_lag1"]].corr()
lv = np.log(full[["FOODCPI", "EXR", "GFOOD", "TRANSCPI"]]).loc["2015-01":"2025-12"].corr()  # log levels, same as the website heatmap

# ---------------------------------------------------------------- 3. stationarity (ADF, Schwarz lag selection, intercept)
STN = []
for code, nm in (("FOODCPI", "Food Prices"), ("EXR", "Dollar Rate"), ("GFOOD", "World Food Prices"), ("TRANSCPI", "Fuel & Transport Costs")):
    lvl = adfuller(np.log(full[code]).loc["2015-01":"2025-12"], regression="c", autolag="BIC", maxlag=12)
    chg = adfuller(pc[code].loc["2015-01":"2025-12"], regression="c", autolag="BIC", maxlag=12)
    STN.append({"name": nm, "level_stat": r(lvl[0]), "level_p": r(lvl[1]), "change_stat": r(chg[0]), "change_p": r(chg[1], 4),
                "crit5": r(lvl[4]["5%"]), "level_result": "Non-stationary" if lvl[1] >= 0.05 else "Stationary",
                "change_result": "Stationary" if chg[1] < 0.05 else "Non-stationary"})

# ---------------------------------------------------------------- 4. multicollinearity
VIF = [{"name": X_NAMES[k], "vif": r(variance_inflation_factor(X.values, i), 2), "tolerance": r(1 / variance_inflation_factor(X.values, i), 3)}
       for i, k in enumerate(X.columns) if k != "const"]

# ---------------------------------------------------------------- 5. diagnostics
bg1, bg12 = acorr_breusch_godfrey(m, 1), acorr_breusch_godfrey(m, 12)
bp, wh = het_breuschpagan(m.resid, X), het_white(m.resid, X)
jb = jarque_bera(m.resid)
rs = linear_reset(m, power=2, use_f=True)
dw = durbin_watson(m.resid)
n, k = int(m.nobs), int(m.df_model)
# Durbin-Watson bounds are invalid with a lagged dependent variable; Durbin's h is reported instead
se_l = m.bse["FoodInf_lag1"]
rho = 1 - dw / 2
h = rho * np.sqrt(n / (1 - n * se_l ** 2)) if n * se_l ** 2 < 1 else np.nan

# ---------------------------------------------------------------- 6. asymmetry: depreciation vs appreciation months
dep = pc["EXR"].shift(1).clip(lower=0).loc["2015-01":"2025-12"].rename("Depreciation_lag1")
app = pc["EXR"].shift(1).clip(upper=0).loc["2015-01":"2025-12"].rename("Appreciation_lag1")
Xa = sm.add_constant(pd.concat([dep, app, d[["WorldFoodInf_lag1", "FuelInf_lag1", "FoodInf_lag1"]]], axis=1))
ma = sm.OLS(d["FoodInf"], Xa).fit()
fa = ma.f_test("Depreciation_lag1 = Appreciation_lag1")

res = {
    "model": "OLS: FoodInf_t = b0 + b1 RupeeDep_{t-1} + b2 WorldFoodInf_{t-1} + b3 FuelInf_{t-1} + b4 FoodInf_{t-1} + e_t",
    "sample": "2015M01–2025M12", "nobs": n,
    "coefficients": coefs,
    "fit": {"r2": r(m.rsquared), "adj_r2": r(m.rsquared_adj), "F": r(m.fvalue, 2), "F_p": r(m.f_pvalue, 4), "df": [k, int(m.df_resid)],
            "se_regression": r(np.sqrt(m.scale)), "aic": r(m.aic, 2), "sic": r(m.bic, 2)},
    "persistence": r(persist), "total_effect_rupee": r(total_exr),
    "hac": {c: {"coef": r(hac.params[c]), "p": r(hac.pvalues[c])} for c in X_NAMES},
    "outlier_dummy": {"rupee_coef": r(md.params["RupeeDep_lag1"]), "rupee_p": r(md.pvalues["RupeeDep_lag1"]), "jb_p": r(jarque_bera(md.resid)[1])},
    "correlation_changes": {"variables": ["Food Inflation", "Rupee Dep. (t−1)", "World Food Inf. (t−1)", "Fuel Inf. (t−1)", "Food Inf. (t−1)"],
                            "matrix": cm.round(3).values.tolist()},
    "correlation_levels": {"variables": ["Food Prices", "Dollar Rate", "World Food Prices", "Fuel & Transport"], "matrix": lv.round(3).values.tolist()},
    "stationarity": STN, "vif": VIF,
    "diagnostics": {
        "durbin_watson": r(dw), "durbin_h": r(h, 2), "durbin_h_p": r(2 * stats.norm.sf(abs(h))) if np.isfinite(h) else None,
        "bg1": {"stat": r(bg1[0]), "p": r(bg1[1])}, "bg12": {"stat": r(bg12[0]), "p": r(bg12[1])},
        "bp": {"stat": r(bp[0]), "p": r(bp[1])}, "white": {"stat": r(wh[0]), "p": r(wh[1])},
        "jb": {"stat": r(jb[0], 2), "p": r(jb[1]), "skew": r(jb[2]), "kurt": r(jb[3])},
        "reset": {"F": r(rs.fvalue), "p": r(rs.pvalue)},
    },
    "asymmetry": {"dep_coef": r(ma.params["Depreciation_lag1"]), "dep_p": r(ma.pvalues["Depreciation_lag1"]),
                  "dep_ci": [r(v) for v in ma.conf_int().loc["Depreciation_lag1"]], "app_ci": [r(v) for v in ma.conf_int().loc["Appreciation_lag1"]],
                  "dep_months": int((dep > 0).sum()), "app_months": int((app < 0).sum()),
                  "app_coef": r(ma.params["Appreciation_lag1"]), "app_p": r(ma.pvalues["Appreciation_lag1"]),
                  "F": r(float(np.squeeze(fa.fvalue))), "p": r(float(np.squeeze(fa.pvalue))), "df": [1, int(ma.df_resid)]},
    "fitted": {"dates": [str(p) for p in d.index], "actual": [r(v) for v in d["FoodInf"]], "fitted": [r(v) for v in m.fittedvalues],
               "resid": [r(v) for v in m.resid]},
}
(ROOT / "research" / "outputs" / "simple_regression.json").write_text(json.dumps(res, indent=2, ensure_ascii=False))
print(m.summary().tables[1])
print(f"R2 {m.rsquared:.3f} F p {m.f_pvalue:.4f} DW {dw:.2f} h {h:.2f} BG12 {bg12[1]:.3f} BP {bp[1]:.3f} White {wh[1]:.3f} JB {jb[1]:.3f} RESET {rs.pvalue:.3f}")
print("asym", res["asymmetry"], "total", total_exr, "dummy", res["outlier_dummy"], "HAC", res["hac"]["RupeeDep_lag1"])
print("ADF", [(s["name"], s["level_p"], s["change_p"]) for s in STN])
