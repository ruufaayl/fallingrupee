"""
ardl_engine.py — a transparent ARDL / NARDL estimator that mirrors EViews conventions.

Why a custom engine?  EViews' "ARDL" equation reports (i) a levels ARDL chosen by an
information-criterion grid search on a common sample, (ii) the conditional error-correction
(CEC) regression and PSS bounds test, (iii) the long-run levels equation with delta-method
standard errors and (iv) the restricted error-correction (ECM) form. Implementing those steps
explicitly with OLS keeps every number traceable and lets the EViews programs in /eviews
reproduce the same specification.

Notation (Pesaran, Shin & Smith 2001; Shin, Yu & Greenwood-Nimmo 2014)
  Levels ARDL(p, q1..qk):  y_t = c + Σ_{i=1..p} φ_i y_{t-i} + Σ_j Σ_{l=0..q_j} β_{jl} x_{j,t-l} + γ'D_t + e_t
  CEC form:  Δy_t = c + ρ y_{t-1} + Σ_j θ_j z_{j} + Σ_{i=1..p-1} α_i Δy_{t-i} + Σ_j Σ_{l=0..q_j-1} π_{jl} Δx_{j,t-l} + γ'D_t + e_t
             where z_j = x_{j,t-1} if q_j > 0 and z_j = x_{j,t} if q_j = 0 (EViews' "Z = Z(-1) + D(Z)" convention),
             so the CEC is an exact reparameterisation of the levels ARDL.
  Long run:  L_j = −θ_j / ρ          Speed of adjustment: ρ (must lie in (−2, 0))
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

# --------------------------------------------------------------------------- data helpers


def lag(s: pd.Series, k: int) -> pd.Series:
    return s.shift(k)


def levels_design(df: pd.DataFrame, y: str, xs: list[str], p: int, q: dict[str, int],
                  fixed: list[str]) -> pd.DataFrame:
    cols = {"C": pd.Series(1.0, index=df.index)}
    for i in range(1, p + 1):
        cols[f"{y}(-{i})"] = lag(df[y], i)
    for x in xs:
        for l in range(0, q[x] + 1):
            cols[x if l == 0 else f"{x}(-{l})"] = lag(df[x], l)
    for f in fixed:
        cols[f] = df[f]
    return pd.DataFrame(cols)


def cec_design(df: pd.DataFrame, y: str, xs: list[str], p: int, q: dict[str, int],
               fixed: list[str]) -> tuple[pd.Series, pd.DataFrame, list[str]]:
    dy = df[y].diff()
    cols = {"C": pd.Series(1.0, index=df.index), f"{y}(-1)": lag(df[y], 1)}
    level_names = [f"{y}(-1)"]
    for x in xs:
        name = f"{x}(-1)" if q[x] > 0 else f"{x}**"
        cols[name] = lag(df[x], 1) if q[x] > 0 else df[x]
        level_names.append(name)
    for i in range(1, p):
        cols[f"D({y}(-{i}))"] = lag(dy, i)
    for x in xs:
        dx = df[x].diff()
        for l in range(0, q[x]):
            cols[f"D({x})" if l == 0 else f"D({x}(-{l}))"] = lag(dx, l)
    for f in fixed:
        cols[f] = df[f]
    return dy.rename(f"D({y})"), pd.DataFrame(cols), level_names


# --------------------------------------------------------------------------- model selection


@dataclass
class Selection:
    order: tuple
    criterion: str
    table: pd.DataFrame           # top models by criterion
    n_models: int


def select_order(df: pd.DataFrame, y: str, xs: list[str], fixed: list[str], max_p: int = 4,
                 max_q: int = 4, criterion: str = "aic", min_p: int = 1) -> Selection:
    """Grid search over ARDL(p, q1..qk) on a common sample that drops max(max_p, max_q) obs,
    exactly as EViews does. Criteria are the EViews (per-observation) definitions."""
    m = max(max_p, max_q)
    est = df.iloc[m:]
    rows = []
    yv = est[y].values
    for p in range(min_p, max_p + 1):
        for qs in itertools.product(range(0, max_q + 1), repeat=len(xs)):
            q = dict(zip(xs, qs))
            X = levels_design(df, y, xs, p, q, fixed).iloc[m:].values
            beta, *_ = np.linalg.lstsq(X, yv, rcond=None)
            e = yv - X @ beta
            n, kpar = X.shape
            ll = -0.5 * n * (1 + np.log(2 * np.pi) + np.log(e @ e / n))
            rows.append({"order": (p, *qs), "k": kpar, "loglik": ll,
                         "aic": -2 * ll / n + 2 * kpar / n,
                         "sic": -2 * ll / n + kpar * np.log(n) / n,
                         "hq": -2 * ll / n + 2 * kpar * np.log(np.log(n)) / n,
                         "adj_r2": 1 - (e @ e / (n - kpar)) / np.var(yv, ddof=1)})
    tab = pd.DataFrame(rows).sort_values(criterion).reset_index(drop=True)
    return Selection(order=tuple(tab.loc[0, "order"]), criterion=criterion,
                     table=tab.head(20), n_models=len(tab))


# --------------------------------------------------------------------------- estimation


@dataclass
class ARDLResult:
    y: str
    xs: list[str]
    fixed: list[str]
    order: tuple
    levels: object                 # statsmodels OLS results (levels ARDL)
    cec: object                    # statsmodels OLS results (conditional EC form)
    level_names: list[str]
    sample: tuple[str, str]
    nobs: int
    longrun: pd.DataFrame = field(default=None)
    bounds: dict = field(default=None)
    ecm: object = field(default=None)  # restricted ECM regression (ECT computed from long run)
    ect_series: pd.Series = field(default=None)


def fit(df: pd.DataFrame, y: str, xs: list[str], order: tuple, fixed: list[str],
        start: int | None = None) -> ARDLResult:
    p, qs = order[0], order[1:]
    q = dict(zip(xs, qs))
    m = start if start is not None else max(order)
    Xl = levels_design(df, y, xs, p, q, fixed).iloc[m:]
    lev = sm.OLS(df[y].iloc[m:], Xl).fit()
    dy, Xc, level_names = cec_design(df, y, xs, p, q, fixed)
    cec = sm.OLS(dy.iloc[m:], Xc.iloc[m:]).fit()
    assert np.allclose(lev.resid.values, cec.resid.values, atol=1e-9), "CEC is not a reparameterisation"
    r = ARDLResult(y, xs, fixed, tuple(order), lev, cec, level_names,
                   (str(df.index[m]), str(df.index[-1])), int(lev.nobs))
    r.longrun = longrun(r)
    r.ect_series = ect(df, r).iloc[m:]
    return r


def longrun(r: ARDLResult) -> pd.DataFrame:
    """Long-run coefficients L = −θ/ρ (and constant −c/ρ) with delta-method SEs (EViews 'Levels Equation')."""
    b, V = r.cec.params, r.cec.cov_params()
    rho_n = r.level_names[0]
    rows = []
    for name in r.level_names[1:] + ["C"]:
        rho, th = b[rho_n], b[name]
        L = -th / rho
        g = pd.Series(0.0, index=b.index)
        g[name] = -1 / rho
        g[rho_n] = th / rho ** 2
        se = float(np.sqrt(g @ V @ g))
        t = L / se
        pv = 2 * stats.t.sf(abs(t), r.cec.df_resid)
        var = name.replace("(-1)", "").replace("**", "")
        rows.append({"variable": var, "coef": L, "se": se, "t": t, "p": pv,
                     "ci95_low": L - stats.t.ppf(0.975, r.cec.df_resid) * se,
                     "ci95_high": L + stats.t.ppf(0.975, r.cec.df_resid) * se})
    return pd.DataFrame(rows).set_index("variable")


def ect(df: pd.DataFrame, r: ARDLResult) -> pd.Series:
    """EC_t = y_t − (Σ L_j x_jt + L_c)."""
    lr = r.longrun["coef"]
    fit_ = sum(lr[x] * df[x] for x in r.xs) + lr["C"]
    return (df[r.y] - fit_).rename("ECT")


def restricted_ecm(df: pd.DataFrame, r: ARDLResult) -> object:
    """EViews 'ECM Regression': short-run terms + CointEq(-1); constant restricted into the long run (case III keeps it)."""
    p, qs = r.order[0], r.order[1:]
    q = dict(zip(r.xs, qs))
    dy, Xc, _ = cec_design(df, r.y, r.xs, p, q, r.fixed)
    Xc = Xc.drop(columns=r.level_names)
    Xc["CointEq(-1)"] = ect(df, r).shift(1)
    m = len(df) - r.nobs
    return sm.OLS(dy.iloc[m:], Xc.iloc[m:]).fit()


# --------------------------------------------------------------------------- bounds testing

PSS_TABLE = {  # Pesaran, Shin & Smith (2001), Table CI(iii) case III (unrestricted intercept, no trend), F-statistic
    3: {"10%": (2.72, 3.77), "5%": (3.23, 4.35), "2.5%": (3.69, 4.89), "1%": (4.29, 5.61)},
    4: {"10%": (2.45, 3.52), "5%": (2.86, 4.01), "2.5%": (3.25, 4.49), "1%": (3.74, 5.06)},
    5: {"10%": (2.26, 3.35), "5%": (2.62, 3.79), "2.5%": (2.96, 4.18), "1%": (3.41, 4.68)},
}
PSS_T_TABLE = {  # Pesaran, Shin & Smith (2001), Table CII(iii) case III, t-statistic on y(-1)
    3: {"10%": (-2.57, -3.46), "5%": (-2.86, -3.78), "2.5%": (-3.13, -4.05), "1%": (-3.43, -4.37)},
    4: {"10%": (-2.57, -3.66), "5%": (-2.86, -3.99), "2.5%": (-3.13, -4.26), "1%": (-3.43, -4.60)},
    5: {"10%": (-2.57, -3.86), "5%": (-2.86, -4.19), "2.5%": (-3.13, -4.46), "1%": (-3.43, -4.79)},
}


def simulate_bounds(k: int, nobs: int, nsim: int = 20000, seed: int = 20251231) -> dict:
    """Finite-sample PSS critical values for case III by Monte Carlo (same design as Narayan 2005):
    y is a driftless random walk; regressors are I(0) (lower bound) or I(1) (upper bound);
    Δy_t is regressed on [1, y_{t-1}, x_{t-1}] and the F (joint zero on levels) and t (on y_{t-1}) are stored."""
    rng = np.random.default_rng(seed)
    out = {"F": {"lower": [], "upper": []}, "t": {"lower": [], "upper": []}}
    for bound in ("lower", "upper"):
        e = rng.standard_normal((nsim, nobs + 1, k + 1))
        y = np.cumsum(e[:, :, 0], axis=1)
        x = np.cumsum(e[:, :, 1:], axis=1) if bound == "upper" else e[:, :, 1:]
        lhs = np.diff(y, axis=1)
        X = np.concatenate([np.ones((nsim, nobs, 1)), y[:, :-1, None], x[:, :-1, :]], axis=2)
        Xt = np.transpose(X, (0, 2, 1))
        XtX_inv = np.linalg.inv(Xt @ X)
        b = (XtX_inv @ (Xt @ lhs[:, :, None]))[:, :, 0]
        u = lhs - (X @ b[:, :, None])[:, :, 0]
        dfree = nobs - X.shape[2]
        s2 = (u ** 2).sum(1) / dfree
        R = np.arange(1, k + 2)
        Vr = XtX_inv[:, R][:, :, R] * s2[:, None, None]
        br = b[:, R]
        F = np.einsum("ni,nij,nj->n", br, np.linalg.inv(Vr), br) / len(R)
        t = b[:, 1] / np.sqrt(XtX_inv[:, 1, 1] * s2)
        out["F"][bound] = F
        out["t"][bound] = t
    cv = {}
    for lvl, q in (("10%", 0.90), ("5%", 0.95), ("2.5%", 0.975), ("1%", 0.99)):
        cv[lvl] = {"F": (float(np.quantile(out["F"]["lower"], q)), float(np.quantile(out["F"]["upper"], q))),
                   "t": (float(np.quantile(out["t"]["lower"], 1 - q)), float(np.quantile(out["t"]["upper"], 1 - q)))}
    return {"critical_values": cv, "draws": out, "nsim": nsim, "nobs": nobs, "seed": seed}


def bounds_test(r: ARDLResult, sim: dict | None = None) -> dict:
    k = len(r.xs)
    names = r.level_names
    R = np.zeros((len(names), len(r.cec.params)))
    for i, n in enumerate(names):
        R[i, list(r.cec.params.index).index(n)] = 1
    ft = r.cec.f_test(R)
    F = float(np.squeeze(ft.fvalue))
    t = float(r.cec.tvalues[names[0]])

    def decide(stat, lo, hi, is_t=False):
        if is_t:
            return "reject" if stat < hi else ("inconclusive" if stat < lo else "do not reject")
        return "reject" if stat > hi else ("inconclusive" if stat > lo else "do not reject")

    res = {"k": k, "F": F, "t": t, "df": [len(names), int(r.cec.df_resid)],
           "asymptotic": {lvl: {"F_I0": v[0], "F_I1": v[1], "t_I0": PSS_T_TABLE[k][lvl][0],
                                "t_I1": PSS_T_TABLE[k][lvl][1]} for lvl, v in PSS_TABLE[k].items()},
           "decision_F_5pct_asymptotic": decide(F, *PSS_TABLE[k]["5%"]),
           "decision_t_5pct_asymptotic": decide(t, *PSS_T_TABLE[k]["5%"], is_t=True)}
    if sim is not None:
        cv = sim["critical_values"]
        res["finite_sample"] = {lvl: {"F_I0": v["F"][0], "F_I1": v["F"][1], "t_I0": v["t"][0], "t_I1": v["t"][1]}
                                for lvl, v in cv.items()}
        res["finite_sample_nobs"] = sim["nobs"]
        res["finite_sample_nsim"] = sim["nsim"]
        res["p_value_F_I1_sim"] = float((sim["draws"]["F"]["upper"] >= F).mean())
        res["p_value_F_I0_sim"] = float((sim["draws"]["F"]["lower"] >= F).mean())
        res["p_value_t_I1_sim"] = float((sim["draws"]["t"]["upper"] <= t).mean())
        res["decision_F_5pct_finite"] = decide(F, *cv["5%"]["F"])
        res["decision_t_5pct_finite"] = decide(t, *cv["5%"]["t"], is_t=True)
    return res


# --------------------------------------------------------------------------- NARDL asymmetry tests


def wald_longrun_symmetry(r: ARDLResult, pos: str, neg: str) -> dict:
    """H0: L+ = L−, i.e. −θ+/ρ = −θ−/ρ. Nonlinear Wald (delta method), χ²(1); plus the
    equivalent linear restriction θ+ = θ− as an F(1, df) test (identical null when ρ ≠ 0)."""
    lr = r.longrun
    b, V = r.cec.params, r.cec.cov_params()
    rho_n = r.level_names[0]
    pn = next(n for n in r.level_names if n.startswith(pos))
    nn = next(n for n in r.level_names if n.startswith(neg))
    rho = b[rho_n]
    diff = -(b[pn] - b[nn]) / rho
    g = pd.Series(0.0, index=b.index)
    g[pn], g[nn], g[rho_n] = -1 / rho, 1 / rho, (b[pn] - b[nn]) / rho ** 2
    var = float(g @ V @ g)
    chi2 = diff ** 2 / var
    R = np.zeros((1, len(b)))
    R[0, list(b.index).index(pn)], R[0, list(b.index).index(nn)] = 1, -1
    ft = r.cec.f_test(R)
    return {"null": "Long-run symmetry: L⁺ = L⁻ (−θ⁺/ρ = −θ⁻/ρ)",
            "L_pos": float(lr.loc[pos, "coef"]), "L_neg": float(lr.loc[neg, "coef"]),
            "difference": float(diff), "se_difference": float(np.sqrt(var)),
            "wald_chi2": float(chi2), "df": 1, "p_chi2": float(stats.chi2.sf(chi2, 1)),
            "F_linear": float(np.squeeze(ft.fvalue)), "F_df": [1, int(r.cec.df_resid)],
            "p_F_linear": float(np.squeeze(ft.pvalue))}


def wald_shortrun_symmetry(r: ARDLResult, pos: str, neg: str) -> dict:
    """Additive short-run symmetry (SYG 2014): H0: Σ_l π⁺_l = Σ_l π⁻_l, using the CEC Δ-terms.
    If a partial sum enters with q = 0 its short-run impact is carried by the level term (z = x_t), so the
    test uses the impact coefficient implied by the levels ARDL instead (β_{j0})."""
    lv = r.levels
    b, V = lv.params, lv.cov_params()
    # impact (contemporaneous) multipliers from the levels ARDL: β⁺_0 vs β⁻_0
    R = np.zeros((1, len(b)))
    R[0, list(b.index).index(pos)], R[0, list(b.index).index(neg)] = 1, -1
    ft_imp = lv.f_test(R)
    # cumulative short-run sum on Δ terms in the CEC (only if both have q ≥ 1)
    cb = r.cec.params
    pos_terms = [n for n in cb.index if n.startswith(f"D({pos}")]
    neg_terms = [n for n in cb.index if n.startswith(f"D({neg}")]
    res = {"null_impact": "Impact symmetry: β⁺₀ = β⁻₀ (same within-month effect)",
           "beta0_pos": float(b[pos]), "beta0_neg": float(b[neg]),
           "F_impact": float(np.squeeze(ft_imp.fvalue)), "F_impact_df": [1, int(lv.df_resid)],
           "p_impact": float(np.squeeze(ft_imp.pvalue))}
    if pos_terms and neg_terms:
        R2 = np.zeros((1, len(cb)))
        for n in pos_terms:
            R2[0, list(cb.index).index(n)] = 1
        for n in neg_terms:
            R2[0, list(cb.index).index(n)] = -1
        ft = r.cec.f_test(R2)
        res.update({"null_additive": "Additive short-run symmetry: Σπ⁺ = Σπ⁻",
                    "sum_pi_pos": float(cb[pos_terms].sum()), "sum_pi_neg": float(cb[neg_terms].sum()),
                    "F_additive": float(np.squeeze(ft.fvalue)), "F_additive_df": [1, int(r.cec.df_resid)],
                    "p_additive": float(np.squeeze(ft.pvalue)), "pos_terms": pos_terms, "neg_terms": neg_terms})
    return res


# --------------------------------------------------------------------------- dynamic multipliers


def _step_response(params: pd.Series, y: str, x: str, p: int, qx: int, H: int) -> np.ndarray:
    """Cumulative dynamic multiplier m_h = ∂y_{t+h}/∂x (permanent unit step in x at t) from levels ARDL."""
    phi = np.array([params.get(f"{y}(-{i})", 0.0) for i in range(1, p + 1)])
    beta = np.array([params.get(x if l == 0 else f"{x}(-{l})", 0.0) for l in range(qx + 1)])
    m = np.zeros(H + 1)
    for h in range(H + 1):
        ar = sum(phi[i - 1] * (m[h - i] if h - i >= 0 else 0.0) for i in range(1, p + 1))
        xin = beta[: min(h, qx) + 1].sum()
        m[h] = ar + xin
    return m


def dynamic_multipliers(r: ARDLResult, pos: str, neg: str, H: int = 36, ndraw: int = 5000,
                        seed: int = 7) -> dict:
    """m⁺_h (response to a 1-unit rise in LEXR_POS: depreciation) and m⁻_h (response to a 1-unit rise in
    LEXR_NEG). Because LEXR_NEG falls when the rupee appreciates, the response of food prices to a 1-unit
    APPRECIATION is −m⁻_h. Bands: parametric bootstrap, coefficient draws from N(b̂, V̂)."""
    p = r.order[0]
    q = dict(zip(r.xs, r.order[1:]))
    b = r.levels.params
    mp = _step_response(b, r.y, pos, p, q[pos], H)
    mn = _step_response(b, r.y, neg, p, q[neg], H)
    rng = np.random.default_rng(seed)
    draws = rng.multivariate_normal(b.values, r.levels.cov_params().values, size=ndraw)
    P, N = np.empty((ndraw, H + 1)), np.empty((ndraw, H + 1))
    for i, d in enumerate(draws):
        bd = pd.Series(d, index=b.index)
        P[i] = _step_response(bd, r.y, pos, p, q[pos], H)
        N[i] = _step_response(bd, r.y, neg, p, q[neg], H)
    A = P - N
    pct = lambda M, a: np.percentile(M, a, axis=0)
    return {"horizon": list(range(H + 1)),
            "pos": mp.tolist(), "neg": mn.tolist(), "asym": (mp - mn).tolist(),
            "pos_lo95": pct(P, 2.5).tolist(), "pos_hi95": pct(P, 97.5).tolist(),
            "neg_lo95": pct(N, 2.5).tolist(), "neg_hi95": pct(N, 97.5).tolist(),
            "asym_lo95": pct(A, 2.5).tolist(), "asym_hi95": pct(A, 97.5).tolist(),
            "asym_lo90": pct(A, 5).tolist(), "asym_hi90": pct(A, 95).tolist(),
            "ndraw": ndraw, "seed": seed}
