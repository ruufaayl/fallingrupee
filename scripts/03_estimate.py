"""
03_estimate.py — the complete econometric analysis, end to end, from data/processed/estimation_sample.csv.

Every number written here is computed in Python (pandas / statsmodels / arch / scipy). These are
SUPPLEMENTARY estimates: the designated estimation environment is EViews, and the EViews programs in
/eviews reproduce the same specifications. Each result carries status "computed_python_pending_eviews"
until it is confirmed in EViews (see scripts/05_compare_eviews.py).

Outputs: research/outputs/*.json (machine-readable results) and research/outputs/figures/*.png
Run:     python scripts/03_estimate.py
"""
from __future__ import annotations

import json
import sys
import warnings
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
from arch.unitroot import PhillipsPerron
from scipy import stats
from statsmodels.stats.diagnostic import (acorr_breusch_godfrey, het_arch, het_breuschpagan, het_white,
                                          linear_reset, recursive_olsresiduals)
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.stattools import durbin_watson, jarque_bera
from statsmodels.tsa.stattools import adfuller, coint, kpss

sys.path.insert(0, str(Path(__file__).parent))
import ardl_engine as E  # noqa: E402

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research" / "outputs"
OUT.mkdir(parents=True, exist_ok=True)
STATUS = "computed_python_pending_eviews"
ENGINE = {"software": "Python " + sys.version.split()[0], "packages": {
    "statsmodels": sm.__version__, "pandas": pd.__version__, "numpy": np.__version__}}
NOW = datetime.now(timezone.utc).isoformat(timespec="seconds")

df = pd.read_csv(ROOT / "data" / "processed" / "estimation_sample.csv")
df.index = pd.period_range("2015-01", periods=len(df), freq="M")
SEAS = [c for c in df if c.startswith("SEAS")]
Y = "LFOODCPI"
X_ARDL = ["LEXR", "LGFOOD", "LTRANSCPI"]
X_NARDL = ["LEXR_POS", "LEXR_NEG", "LGFOOD", "LTRANSCPI"]
MAXLAG = 4
SAMPLE = f"{df.index[0]}–{df.index[-1]}"


def f(x, nd=6):
    """JSON-safe float."""
    if x is None:
        return None
    x = float(x)
    return None if not np.isfinite(x) else round(x, nd)


def save(name: str, obj: dict) -> None:
    obj = {"_meta": {"generated_utc": NOW, "engine": ENGINE, "status": STATUS,
                     "estimation_sample": SAMPLE, "script": "scripts/03_estimate.py"}, **obj}
    (OUT / f"{name}.json").write_text(json.dumps(obj, indent=2, ensure_ascii=False))
    print(f"  wrote research/outputs/{name}.json")


def coef_table(res, names=None) -> list[dict]:
    names = names or list(res.params.index)
    return [{"term": n, "coef": f(res.params[n]), "se": f(res.bse[n]), "t": f(res.tvalues[n]),
             "p": f(res.pvalues[n])} for n in names]


# =============================================================================== 1. descriptives
print("1. Descriptive statistics")
LABEL = {"FOODCPI": "Food CPI (2015-16=100)", "EXR": "PKR per USD", "GFOOD": "FAO Food Price Index (2014-16=100)",
         "TRANSCPI": "Transport CPI (2015-16=100)", "CPI": "Headline CPI (2015-16=100)",
         "FOOD_INF_YOY": "Food inflation, YoY %", "FOOD_INF_MOM": "Food inflation, MoM %",
         "EXR_DEP_YOY": "PKR depreciation vs USD, YoY %", "GFOOD_YOY": "FAO FFPI, YoY %", "TRANS_YOY": "Transport CPI, YoY %"}
desc = []
for v, lab in LABEL.items():
    x = df[v].dropna()
    jb, jbp, sk, ku = jarque_bera(x)
    row = {"variable": v, "label": lab, "n": int(x.size), "mean": f(x.mean()), "median": f(x.median()),
           "sd": f(x.std()), "min": f(x.min()), "min_date": str(x.idxmin()), "max": f(x.max()),
           "max_date": str(x.idxmax()), "skewness": f(sk), "kurtosis": f(ku), "jarque_bera": f(jb), "jb_p": f(jbp)}
    if v in ("FOODCPI", "EXR", "GFOOD", "TRANSCPI", "CPI"):
        yrs = (len(x) - 1) / 12
        row["total_change_pct"] = f((x.iloc[-1] / x.iloc[0] - 1) * 100)
        row["cagr_pct"] = f(((x.iloc[-1] / x.iloc[0]) ** (1 / yrs) - 1) * 100)
        row["index_2015m01_100_end"] = f(x.iloc[-1] / x.iloc[0] * 100)
    desc.append(row)

# year-by-year averages, for the narrative
annual = (df[["FOODCPI", "EXR", "GFOOD", "TRANSCPI", "CPI"]].groupby(df.index.year).mean())
annual_infl = annual.pct_change() * 100
# outliers in monthly food inflation: |z| > 2.5 using median/MAD (robust)
mom = df["FOOD_INF_MOM"]
mad = stats.median_abs_deviation(mom, scale="normal")
z = (mom - mom.median()) / mad
outliers = [{"date": str(d), "food_inf_mom": f(mom[d], 3), "robust_z": f(z[d], 2)} for d in z[abs(z) > 2.5].index]
# regime episodes of the exchange rate (largest depreciation / appreciation months)
dl = df["LEXR"].diff() * 100
top_dep = [{"date": str(d), "pct": f(dl[d], 2)} for d in dl.nlargest(6).index]
top_app = [{"date": str(d), "pct": f(dl[d], 2)} for d in dl.nsmallest(6).index]
save("descriptive_statistics", {
    "variables": desc,
    "annual_means": {str(y): {k: f(v, 3) for k, v in row.items()} for y, row in annual.iterrows()},
    "annual_growth_pct": {str(y): {k: f(v, 3) for k, v in row.items()} for y, row in annual_infl.dropna().iterrows()},
    "food_inflation_outliers": {"method": "robust z = (x − median)/MAD·1.4826, |z| > 2.5, monthly food inflation",
                                "items": outliers},
    "largest_depreciation_months": top_dep, "largest_appreciation_months": top_app,
    "exchange_rate_months": {"depreciating": int((dl > 0).sum()), "appreciating": int((dl < 0).sum()),
                             "cumulative_depreciation_log": f(df["LEXR_POS"].iloc[-1]),
                             "cumulative_appreciation_log": f(df["LEXR_NEG"].iloc[-1])},
})

# =============================================================================== 2. correlations / VIF
print("2. Correlations and multicollinearity")
lv = ["LFOODCPI", "LEXR", "LGFOOD", "LTRANSCPI"]
corr_lv = df[lv].corr()
corr_d = df[lv].diff().dropna().corr()
corr_yoy = df[["FOOD_INF_YOY", "EXR_DEP_YOY", "GFOOD_YOY", "TRANS_YOY"]].dropna().corr()


def vif_table(cols, data):
    X = sm.add_constant(data[cols].dropna())
    return [{"variable": c, "vif": f(variance_inflation_factor(X.values, i + 1), 3),
             "tolerance": f(1 / variance_inflation_factor(X.values, i + 1), 4)} for i, c in enumerate(cols)]


save("correlations", {
    "levels_log": {"variables": lv, "matrix": corr_lv.round(4).values.tolist()},
    "first_differences_log": {"variables": lv, "matrix": corr_d.round(4).values.tolist()},
    "yoy_rates": {"variables": list(corr_yoy.columns), "matrix": corr_yoy.round(4).values.tolist()},
    "vif_levels": vif_table(["LEXR", "LGFOOD", "LTRANSCPI"], df),
    "vif_differences": vif_table(["LEXR", "LGFOOD", "LTRANSCPI"], df[["LEXR", "LGFOOD", "LTRANSCPI"]].diff()),
    "vif_nardl_levels": vif_table(["LEXR_POS", "LEXR_NEG", "LGFOOD", "LTRANSCPI"], df),
    "note": ("VIF > 10 signals that trending levels share a common trend; this inflates standard errors in a static "
             "levels regression but does not bias coefficients. Variables are retained on theoretical grounds; the "
             "ARDL error-correction form, whose short-run regressors are differences, is far less collinear."),
})

# =============================================================================== 3. stationarity
print("3. Unit-root tests")
CV_ = lambda d: {k: f(v, 4) for k, v in d.items()}


def unit_root_battery(x: pd.Series, name: str, form: str) -> list[dict]:
    rows = []
    for spec in (["c", "ct"] if form == "level" else ["c"]):
        for ic in ("AIC", "BIC"):
            a = adfuller(x, regression=spec, autolag=ic, maxlag=12)
            rows.append({"variable": name, "form": form, "test": "ADF", "deterministic": spec, "lag_rule": ic,
                         "lags": int(a[2]), "stat": f(a[0], 4), "p": f(a[1], 4), "crit": CV_(a[4]),
                         "null": "Unit root (non-stationary)", "reject_5pct": bool(a[1] < 0.05)})
        pp = PhillipsPerron(x, trend=spec, test_type="tau")
        rows.append({"variable": name, "form": form, "test": "PP", "deterministic": spec,
                     "lag_rule": "Newey-West bandwidth", "lags": int(pp.lags), "stat": f(pp.stat, 4),
                     "p": f(pp.pvalue, 4), "crit": CV_(pp.critical_values), "null": "Unit root (non-stationary)",
                     "reject_5pct": bool(pp.pvalue < 0.05)})
        k = kpss(x, regression=spec, nlags="auto")
        rows.append({"variable": name, "form": form, "test": "KPSS", "deterministic": spec,
                     "lag_rule": "Hobijn et al. auto", "lags": int(k[2]), "stat": f(k[0], 4),
                     "p": f(k[1], 4), "p_note": "KPSS p-values are interpolated and bounded to [0.01, 0.10]",
                     "crit": CV_({kk: v for kk, v in k[3].items() if kk != "2.5%"}),
                     "null": "Stationary", "reject_5pct": bool(k[0] > k[3]["5%"])})
    return rows


ur_vars = {"LFOODCPI": "ln Food CPI", "LEXR": "ln PKR/USD", "LGFOOD": "ln FAO FFPI", "LTRANSCPI": "ln Transport CPI",
           "LEXR_POS": "ln EXR⁺ (depreciation sum)", "LEXR_NEG": "ln EXR⁻ (appreciation sum)",
           "LHOUSCPI": "ln Housing & utilities CPI", "LBRENT": "ln Brent (USD)", "LGFOOD_WB": "ln WB food index"}
ur_rows, verdict = [], {}
for v, lab in ur_vars.items():
    lvl = unit_root_battery(df[v], v, "level")
    d1 = unit_root_battery(df[v].diff().dropna(), v, "first_difference")
    d2 = unit_root_battery(df[v].diff().diff().dropna(), v, "second_difference")
    ur_rows += lvl + d1 + d2

    def stationary(rows):  # majority of ADF(AIC), ADF(BIC), PP with intercept, plus KPSS not rejecting
        r = [x for x in rows if x["deterministic"] == "c"]
        unit = [x["reject_5pct"] for x in r if x["test"] in ("ADF", "PP")]
        kp = [not x["reject_5pct"] for x in r if x["test"] == "KPSS"]
        return sum(unit) >= 2, (sum(unit) >= 2) and all(kp), unit, kp
    lv_ok = stationary(lvl)
    lv_ct = [x["reject_5pct"] for x in lvl if x["deterministic"] == "ct" and x["test"] in ("ADF", "PP")]
    d1_ok = stationary(d1)
    d2_ok = stationary(d2)
    if lv_ok[0] or sum(lv_ct) >= 2:
        order = "I(0)/trend-stationary (mixed evidence)" if not lv_ok[1] else "I(0)"
    elif d1_ok[0]:
        order = "I(1)"
    elif d2_ok[0]:
        order = "I(1)/I(2) borderline — stationary in second differences"
    else:
        order = "undetermined"
    verdict[v] = {"label": lab, "integration_order": order, "not_I2": bool(d2_ok[0]),
                  "level_reject_unitroot_votes_c": lv_ok[2], "level_reject_unitroot_votes_ct": lv_ct,
                  "diff_reject_unitroot_votes": d1_ok[2], "diff_kpss_stationary": d1_ok[3]}
save("stationarity", {
    "rule": ("Integration order by majority of ADF(AIC), ADF(SIC) and PP at 5%; KPSS reported as a confirmatory test "
             "with the reverse null. ARDL bounds testing requires that no variable is I(2): every variable is checked "
             "in second differences."),
    "summary": verdict, "tests": ur_rows,
    "bounds_admissible": all(v["not_I2"] for v in verdict.values()),
})

# =============================================================================== 4. OLS baseline
print("4. Baseline OLS")
Xo = sm.add_constant(df[X_ARDL])
ols = sm.OLS(df[Y], Xo).fit()
ols_hac = sm.OLS(df[Y], Xo).fit(cov_type="HAC", cov_kwds={"maxlags": 12})
eg = coint(df[Y], df[X_ARDL], trend="c", autolag="aic")
ols_d = sm.OLS(df[Y].diff().dropna(), sm.add_constant(df[X_ARDL].diff().dropna())).fit(cov_type="HAC",
                                                                                    cov_kwds={"maxlags": 12})


def diag_block(res, bg_lags=(2, 12), white=True) -> list[dict]:
    e = res.resid
    out = []
    for L in bg_lags:
        lm, lmp, fv, fp = acorr_breusch_godfrey(res, nlags=L)
        out.append({"group": "Serial correlation", "test": f"Breusch-Godfrey LM ({L} lags)",
                    "null": f"No serial correlation up to order {L}", "stat_name": "Obs·R²", "stat": f(lm, 4),
                    "df": L, "p": f(lmp, 4), "F": f(fv, 4), "p_F": f(fp, 4), "reject_5pct": bool(lmp < 0.05)})
    bp = het_breuschpagan(e, res.model.exog)
    out.append({"group": "Heteroskedasticity", "test": "Breusch-Pagan-Godfrey", "null": "Homoskedastic errors",
                "stat_name": "Obs·R²", "stat": f(bp[0], 4), "df": int(res.model.exog.shape[1] - 1),
                "p": f(bp[1], 4), "F": f(bp[2], 4), "p_F": f(bp[3], 4), "reject_5pct": bool(bp[1] < 0.05)})
    if white:
        # White test without cross terms (EViews option), regressing e² on regressors and their squares.
        Xw = pd.DataFrame(res.model.exog, columns=res.model.exog_names)
        nonconst = [c for c in Xw if Xw[c].nunique() > 2]
        Z = pd.concat([Xw, Xw[nonconst].pow(2).add_suffix("^2")], axis=1)
        aux = sm.OLS(e.values ** 2, Z.values).fit()
        lm = aux.nobs * aux.rsquared
        dfw = Z.shape[1] - 1
        out.append({"group": "Heteroskedasticity", "test": "White (no cross terms)", "null": "Homoskedastic errors",
                    "stat_name": "Obs·R²", "stat": f(lm, 4), "df": int(dfw), "p": f(stats.chi2.sf(lm, dfw), 4),
                    "reject_5pct": bool(stats.chi2.sf(lm, dfw) < 0.05)})
    for L in (1, 12):
        a = het_arch(e, nlags=L)
        out.append({"group": "Heteroskedasticity", "test": f"ARCH LM ({L} lag{'s' if L > 1 else ''})",
                    "null": "No ARCH effects", "stat_name": "Obs·R²", "stat": f(a[0], 4), "df": L, "p": f(a[1], 4),
                    "reject_5pct": bool(a[1] < 0.05)})
    jb, jbp, sk, ku = jarque_bera(e)
    out.append({"group": "Normality", "test": "Jarque-Bera", "null": "Residuals are normally distributed",
                "stat_name": "JB", "stat": f(jb, 4), "df": 2, "p": f(jbp, 4), "skewness": f(sk, 4),
                "kurtosis": f(ku, 4), "reject_5pct": bool(jbp < 0.05)})
    rr = linear_reset(res, power=2, test_type="fitted", use_f=True)
    out.append({"group": "Functional form", "test": "Ramsey RESET (1 fitted term)",
                "null": "Correct functional form (no omitted non-linearity)", "stat_name": "F",
                "stat": f(rr.fvalue, 4), "df": [int(rr.df_num), int(rr.df_denom)], "p": f(rr.pvalue, 4),
                "reject_5pct": bool(rr.pvalue < 0.05)})
    out.append({"group": "Serial correlation", "test": "Durbin-Watson", "null": "No first-order autocorrelation",
                "stat_name": "DW", "stat": f(durbin_watson(e), 4), "p": None,
                "note": ("Indicative only: DW is invalid with a lagged dependent variable among the regressors; "
                         "rely on Breusch-Godfrey.")})
    return out


ols_out = {
    "model_id": "OLS_LEVELS", "equation": "LFOODCPI = c + b1·LEXR + b2·LGFOOD + b3·LTRANSCPI + u",
    "nobs": int(ols.nobs), "coefficients": coef_table(ols), "coefficients_hac": coef_table(ols_hac),
    "r2": f(ols.rsquared), "adj_r2": f(ols.rsquared_adj), "F": f(ols.fvalue, 3), "F_p": f(ols.f_pvalue, 8),
    "se_regression": f(np.sqrt(ols.scale)), "dw": f(durbin_watson(ols.resid), 4), "aic": f(ols.aic, 3),
    "bic": f(ols.bic, 3),
    "spurious_regression_check": {
        "granger_newbold_rule": "R² > DW suggests a possibly spurious levels regression",
        "r2_exceeds_dw": bool(ols.rsquared > durbin_watson(ols.resid)),
        "engle_granger": {"null": "No cointegration (residuals have a unit root)", "stat": f(eg[0], 4),
                          "p": f(eg[1], 4), "crit": {"1%": f(eg[2][0], 4), "5%": f(eg[2][1], 4), "10%": f(eg[2][2], 4)}}},
    "diagnostics": diag_block(ols, white=True),
    "first_difference_ols": {"equation": "ΔLFOODCPI = c + b1·ΔLEXR + b2·ΔLGFOOD + b3·ΔLTRANSCPI + u (HAC s.e.)",
                             "nobs": int(ols_d.nobs), "coefficients": coef_table(ols_d), "r2": f(ols_d.rsquared),
                             "dw": f(durbin_watson(ols_d.resid), 4)},
}
save("ols_results", ols_out)

# =============================================================================== 5. ARDL & NARDL
print("5. Lag selection, ARDL and NARDL")


def cusum_block(res) -> dict:
    rr = recursive_olsresiduals(res, alpha=0.95)
    rresid, cusum, ci = rr[0], rr[5], rr[6]
    k = res.model.exog.shape[1]
    n = len(res.resid)
    w = np.asarray(rresid)[k:]
    w = w[np.isfinite(w)]
    s2 = np.cumsum(w ** 2) / np.sum(w ** 2)
    m = len(w)
    expected = np.arange(1, m + 1) / m
    # CUSUMSQ 5% bound by Monte Carlo (iid normal recursive residuals under H0)
    rng = np.random.default_rng(11)
    sim = rng.standard_normal((20000, m)) ** 2
    simS = np.cumsum(sim, 1) / sim.sum(1, keepdims=True)
    c0 = float(np.quantile(np.abs(simS - expected).max(1), 0.95))
    dates = [str(d) for d in res.resid.index[-m:]]
    cus = np.asarray(cusum)[-m:]
    lo, hi = np.asarray(ci[0])[-m:], np.asarray(ci[1])[-m:]
    return {"dates": dates, "cusum": [f(v, 4) for v in cus], "cusum_lo": [f(v, 4) for v in lo],
            "cusum_hi": [f(v, 4) for v in hi],
            "cusum_within_bounds": bool(np.all((cus >= lo - 1e-9) & (cus <= hi + 1e-9))),
            "cusumsq": [f(v, 4) for v in s2], "cusumsq_expected": [f(v, 4) for v in expected],
            "cusumsq_c0": f(c0, 4), "cusumsq_within_bounds": bool(np.all(np.abs(s2 - expected) <= c0)),
            "cusumsq_max_dev": f(np.abs(s2 - expected).max(), 4),
            "cusumsq_max_dev_date": dates[int(np.argmax(np.abs(s2 - expected)))],
            "method": ("CUSUM: Brown-Durbin-Evans with 5% lines ±0.948·√(n−k)·(1+2(t−k)/(n−k)) as in statsmodels/EViews. "
                       "CUSUMSQ: 5% two-sided bound c0 obtained by 20,000 Monte Carlo draws of iid normal recursive "
                       f"residuals (m = {m}); EViews uses tabulated Durbin (1969) values, which are close.")}


def full_ardl(xs, label, model_id, fixed=SEAS, maxlag=MAXLAG, data=df, crit="aic", sim_k=True):
    sel = E.select_order(data, Y, xs, fixed, maxlag, maxlag, crit)
    r = E.fit(data, Y, xs, sel.order, fixed, start=maxlag)
    sim = E.simulate_bounds(len(xs), nobs=r.nobs, nsim=20000) if sim_k else None
    b = E.bounds_test(r, sim)
    ecm = E.restricted_ecm(data, r)
    return sel, r, b, ecm


def ardl_json(sel, r, b, ecm, model_id, label):
    lr = r.longrun
    return {
        "model_id": model_id, "label": label, "dependent": Y, "regressors": r.xs,
        "deterministics": "Unrestricted intercept, no trend (PSS case III); 11 monthly seasonal dummies (fixed regressors)",
        "selection": {"criterion": sel.criterion.upper(), "max_lags": MAXLAG, "models_evaluated": sel.n_models,
                      "chosen_order": list(sel.order),
                      "top_models": [{"order": list(o), "aic": f(a, 5), "sic": f(s, 5), "hq": f(h, 5),
                                      "adj_r2": f(ar, 5)} for o, a, s, h, ar in
                                     sel.table[["order", "aic", "sic", "hq", "adj_r2"]].head(12).itertuples(index=False)]},
        "sample": {"start": r.sample[0], "end": r.sample[1], "nobs": r.nobs},
        "levels_equation": {"coefficients": coef_table(r.levels, [n for n in r.levels.params.index if n not in SEAS]),
                            "seasonal_dummies_joint_F": f(r.levels.f_test(", ".join(f"{c}=0" for c in SEAS)).fvalue, 4)
                            if SEAS[0] in r.levels.params.index else None,
                            "seasonal_dummies_joint_p": f(r.levels.f_test(", ".join(f"{c}=0" for c in SEAS)).pvalue, 6)
                            if SEAS[0] in r.levels.params.index else None,
                            "r2": f(r.levels.rsquared), "adj_r2": f(r.levels.rsquared_adj),
                            "se_regression": f(np.sqrt(r.levels.scale)), "loglik": f(r.levels.llf, 4),
                            "F": f(r.levels.fvalue, 3), "F_p": f(r.levels.f_pvalue, 8),
                            "dw": f(durbin_watson(r.levels.resid), 4)},
        "cec_equation": {"description": "Conditional error correction (EViews: ARDL Long Run Form and Bounds Test)",
                         "coefficients": coef_table(r.cec, [n for n in r.cec.params.index if n not in SEAS]),
                         "r2": f(r.cec.rsquared)},
        "bounds_test": b,
        "long_run": [{"variable": v, **{k: f(x) for k, x in row.items()}} for v, row in lr.iterrows()],
        "ecm_regression": {"description": "Restricted ECM (EViews: ECM Regression) — short-run terms and CointEq(-1)",
                           "coefficients": coef_table(ecm, [n for n in ecm.params.index if n not in SEAS]),
                           "r2": f(ecm.rsquared), "adj_r2": f(ecm.rsquared_adj), "dw": f(durbin_watson(ecm.resid), 4),
                           "speed_of_adjustment": f(ecm.params["CointEq(-1)"]),
                           "speed_p": f(ecm.pvalues["CointEq(-1)"], 6),
                           "half_life_months": f(np.log(0.5) / np.log(1 + ecm.params["CointEq(-1)"]), 3)},
        "diagnostics": diag_block(r.levels),
        "stability": cusum_block(r.levels),
        "fitted": {"dates": [str(d) for d in r.levels.fittedvalues.index],
                   "actual": [f(v, 5) for v in df.loc[r.levels.fittedvalues.index, Y]],
                   "fitted": [f(v, 5) for v in r.levels.fittedvalues], "resid": [f(v, 5) for v in r.levels.resid]},
    }


sel_a, ra, ba, ecm_a = full_ardl(X_ARDL, "Linear ARDL", "ARDL_MAIN")
ardl_j = ardl_json(sel_a, ra, ba, ecm_a, "ARDL_MAIN", "Linear (symmetric) ARDL")
save("ardl_results", ardl_j)

sel_n, rn, bn, ecm_n = full_ardl(X_NARDL, "Nonlinear ARDL", "NARDL_MAIN")
nardl_j = ardl_json(sel_n, rn, bn, ecm_n, "NARDL_MAIN", "Nonlinear ARDL (Shin, Yu & Greenwood-Nimmo 2014)")
lrs = E.wald_longrun_symmetry(rn, "LEXR_POS", "LEXR_NEG")
srs = E.wald_shortrun_symmetry(rn, "LEXR_POS", "LEXR_NEG")
nardl_j["asymmetry"] = {"long_run": {k: (f(v) if isinstance(v, float) else v) for k, v in lrs.items()},
                        "short_run": {k: (f(v) if isinstance(v, float) else v) for k, v in srs.items()}}
mult = E.dynamic_multipliers(rn, "LEXR_POS", "LEXR_NEG", H=36, ndraw=5000)
save("nardl_results", nardl_j)
save("multipliers", {"model_id": "NARDL_MAIN", "units": "elasticity: % change in food CPI per 1% change in PKR/USD",
                     "definitions": {"pos": "m⁺(h): cumulative response to a permanent 1% depreciation",
                                     "neg": "m⁻(h): cumulative response to a 1-unit rise in LEXR_NEG; the response to a "
                                            "1% APPRECIATION is −m⁻(h), i.e. a fall in food prices when m⁻ > 0",
                                     "asym": "m⁺(h) − m⁻(h): asymmetry; zero line inside the band ⇒ no significant asymmetry"},
                     "band": "95% parametric bootstrap (5,000 draws from N(b̂, V̂) of the levels ARDL)",
                     "long_run_pos": f(lrs["L_pos"]), "long_run_neg": f(lrs["L_neg"]),
                     **{k: ([f(x, 5) for x in v] if isinstance(v, list) and k != "horizon" else v) for k, v in mult.items()}})

wald = {"tests": [
    {"id": "LR_SYM", "model_id": "NARDL_MAIN", "null": lrs["null"], "statistic": "Wald χ²", "value": f(lrs["wald_chi2"], 4),
     "df": 1, "p": f(lrs["p_chi2"], 4), "alt_statistic": "F (θ⁺ = θ⁻)", "alt_value": f(lrs["F_linear"], 4),
     "alt_df": lrs["F_df"], "alt_p": f(lrs["p_F_linear"], 4),
     "decision": "Reject symmetry" if lrs["p_chi2"] < 0.05 else "Do not reject symmetry"},
    {"id": "SR_IMPACT", "model_id": "NARDL_MAIN", "null": srs["null_impact"], "statistic": "F",
     "value": f(srs["F_impact"], 4), "df": srs["F_impact_df"], "p": f(srs["p_impact"], 4),
     "decision": "Reject symmetry" if srs["p_impact"] < 0.05 else "Do not reject symmetry"}]}
if "p_additive" in srs:
    wald["tests"].append({"id": "SR_ADDITIVE", "model_id": "NARDL_MAIN", "null": srs["null_additive"], "statistic": "F",
                          "value": f(srs["F_additive"], 4), "df": srs["F_additive_df"], "p": f(srs["p_additive"], 4),
                          "decision": "Reject symmetry" if srs["p_additive"] < 0.05 else "Do not reject symmetry"})
else:
    wald["tests"].append({"id": "SR_ADDITIVE", "model_id": "NARDL_MAIN", "null": "Additive short-run symmetry: Σπ⁺ = Σπ⁻",
                          "status": "not_applicable",
                          "reason": ("The selected order gives LEXR_POS no lagged Δ-terms (q⁺ = 0), so its short-run "
                                     "effect is the impact coefficient alone; short-run symmetry is tested on impact.")})
save("wald_tests", wald)

# =============================================================================== 6. robustness
print("6. Robustness")
EV = ["D_REBASE", "D_COVID", "D_FLOOD", "D_RAMADAN"]
df["D_2024M05"] = (df.index == pd.Period("2024-05")).astype(int)


def spec_row(spec_id, label, xs, fixed=SEAS, data=df, maxlag=MAXLAG, crit="aic", y=Y, note=""):
    global Y
    old, Y = Y, y
    try:
        sel = E.select_order(data, y, xs, fixed, maxlag, maxlag, crit)
        r = E.fit(data, y, xs, sel.order, fixed, start=maxlag)
        b = E.bounds_test(r)
        lr = r.longrun
        row = {"id": spec_id, "label": label, "note": note, "sample": f"{r.sample[0]}–{r.sample[1]}", "nobs": r.nobs,
               "order": list(sel.order), "criterion": crit.upper(), "bounds_F": f(b["F"], 3),
               "bounds_t": f(b["t"], 3), "F_decision_5pct": b["decision_F_5pct_asymptotic"],
               "t_decision_5pct": b["decision_t_5pct_asymptotic"], "ect": f(r.cec.params[r.level_names[0]], 4),
               "ect_p": f(r.cec.pvalues[r.level_names[0]], 4),
               "long_run": {v: {"coef": f(lr.loc[v, "coef"], 4), "p": f(lr.loc[v, "p"], 4)} for v in xs},
               "bg2_p": f(acorr_breusch_godfrey(r.levels, 2)[1], 4), "jb_p": f(jarque_bera(r.levels.resid)[1], 4)}
        if "LEXR_POS" in xs:
            w = E.wald_longrun_symmetry(r, "LEXR_POS", "LEXR_NEG")
            s_ = E.wald_shortrun_symmetry(r, "LEXR_POS", "LEXR_NEG")
            row.update({"lr_sym_p": f(w["p_chi2"], 4), "impact_sym_p": f(s_["p_impact"], 4),
                        "sr_additive_p": f(s_.get("p_additive"), 4)})
        return row
    finally:
        Y = old


X_N = X_NARDL
specs = [
    ("BASE", "Baseline NARDL (AIC, max lag 4, seasonal dummies)", X_N, {}),
    ("SIC", "Lag order by Schwarz criterion", X_N, {"crit": "sic"}),
    ("HQ", "Lag order by Hannan-Quinn criterion", X_N, {"crit": "hq"}),
    ("LAG6", "Maximum lag 6", X_N, {"maxlag": 6}),
    ("ENERGY_HOUS", "Energy proxy: Housing, water, electricity, gas & fuels CPI", ["LEXR_POS", "LEXR_NEG", "LGFOOD", "LHOUSCPI"], {}),
    ("ENERGY_BRENT", "Energy proxy: Brent crude (USD/bbl)", ["LEXR_POS", "LEXR_NEG", "LGFOOD", "LBRENT"], {}),
    ("GFOOD_WB", "Global food: World Bank Pink Sheet food index", ["LEXR_POS", "LEXR_NEG", "LGFOOD_WB", "LTRANSCPI"], {}),
    ("EVENTS", "Event dummies: CPI rebase 2019M07 (step), COVID, 2022 floods, Ramadan", X_N, {"fixed": SEAS + EV}),
    ("IMPULSE", "Impulse dummy for the May-2024 food-price collapse", X_N, {"fixed": SEAS + ["D_2024M05"]}),
    ("NOSEAS", "No seasonal dummies", X_N, {"fixed": []}),
    ("PRE2024", "Sample 2015M01–2023M12 (before 2024–25 disinflation)", X_N, {"data": df.loc[:"2023-12"]}),
    ("POST_REBASE", "Sample 2019M07–2025M12 (2015-16-base national CPI only)", X_N, {"data": df.loc["2019-07":], "maxlag": 3}),
    ("HEADLINE", "Dependent variable: headline CPI (extension)", X_N, {"y": "LCPI"}),
]
rob = []
for sid, lab, xs, kw in specs:
    try:
        rob.append(spec_row(sid, lab, xs, **kw))
    except Exception as exc:  # report rather than hide
        rob.append({"id": sid, "label": lab, "status": "failed", "error": str(exc)})
# linear ARDL counterparts for the key alternatives
rob_lin = [spec_row("ARDL_BASE", "Linear ARDL baseline", X_ARDL),
           spec_row("ARDL_SIC", "Linear ARDL, SIC", X_ARDL, crit="sic"),
           spec_row("ARDL_EVENTS", "Linear ARDL with event dummies", X_ARDL, fixed=SEAS + EV),
           spec_row("ARDL_PRE2024", "Linear ARDL, 2015M01–2023M12", X_ARDL, data=df.loc[:"2023-12"]),
           spec_row("ARDL_POST_REBASE", "Linear ARDL, 2019M07–2025M12", X_ARDL, data=df.loc["2019-07":], maxlag=3)]
save("robustness", {"nardl_specifications": rob, "ardl_specifications": rob_lin,
                    "critical_values_note": ("Decisions use PSS (2001) asymptotic case III bounds at 5% "
                                             "(k=3: F 3.23/4.35, t −2.86/−3.78; k=4: F 2.86/4.01, t −2.86/−3.99).")})

# =============================================================================== 7. time series for charts
print("7. Time series for the website")
ts = df[["FOODCPI", "CPI", "EXR", "GFOOD", "GFOOD_WB", "TRANSCPI", "HOUSCPI", "BRENT", "FOOD_INF_YOY", "FOOD_INF_MOM",
         "CPI_INF_YOY", "EXR_DEP_YOY", "GFOOD_YOY", "TRANS_YOY", "LEXR_POS", "LEXR_NEG"]]
save("timeseries", {"dates": [str(d) for d in ts.index],
                    "series": {c: [f(v, 4) for v in ts[c]] for c in ts.columns},
                    "rebased_2015m01": {c: [f(v / ts[c].iloc[0] * 100, 3) for v in ts[c]]
                                        for c in ("FOODCPI", "EXR", "GFOOD", "TRANSCPI", "CPI")}})
print("done.")
