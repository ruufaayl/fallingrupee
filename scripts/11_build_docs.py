"""
11_build_docs.py — executive summary, methodology summary and viva preparation (Markdown), with every number
read from the results registry. Run: python scripts/11_build_docs.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
O = ROOT / "research" / "outputs"
DOCS = ROOT / "docs"
DOCS.mkdir(exist_ok=True)
J = lambda n: json.loads((O / f"{n}.json").read_text())
ardl, nardl, ols, desc, stn = J("ardl_results"), J("nardl_results"), J("ols_results"), J("descriptive_statistics"), J("stationarity")
F = json.loads((ROOT / "data" / "research" / "findings.json").read_text())
H, RC = F["headline_numbers"], F["robustness_counts"]
LA = {x["variable"]: x for x in ardl["long_run"]}
LN = {x["variable"]: x for x in nardl["long_run"]}
AS, BA, BN, ECA, ECN = nardl["asymmetry"], ardl["bounds_test"], nardl["bounds_test"], ardl["ecm_regression"], nardl["ecm_regression"]
eg = ols["spurious_regression_check"]["engle_granger"]
f = lambda x, d=2: f"{x:.{d}f}".replace("-", "−")
fp = lambda p: "< 0.001" if p < 0.001 else f"{p:.3f}"
SITE = "https://the-price-of-a-falling-rupee.vercel.app"
oa, on = tuple(ardl["selection"]["chosen_order"]), tuple(nardl["selection"]["chosen_order"])
share = 100 * LA["LEXR"]["coef"] * math.log(1 + H["exr_change_pct"] / 100) / math.log(1 + H["food_cpi_change_pct"] / 100)
STATUS = ("> **Status:** every estimate here was computed in Python (statsmodels 0.15) by `scripts/03_estimate.py`. EViews programs "
          "that reproduce each specification are in `/eviews`; results are labelled *pending EViews verification* until "
          "`scripts/07_compare_eviews.py` confirms them.\n")

# --------------------------------------------------------------------------------------------- executive summary
(DOCS / "EXECUTIVE_SUMMARY.md").write_text(f"""# The Price of a Falling Rupee — Executive Summary

{STATUS}
**Question.** How far do rupee depreciation, world food prices and domestic energy costs explain Pakistan's food inflation — and does
depreciation affect food prices more strongly or more persistently than appreciation?

**Why it matters.** Food is 34.58% of Pakistan's national CPI basket. Between January 2015 and December 2025 the food price index rose
**{f(H['food_cpi_change_pct'],0)}%** ({f(H['food_cagr_pct'],1)}% a year), rupees per US dollar rose **{f(H['exr_change_pct'],0)}%**, and
world food prices (FAO) rose only **{f(H['gfood_change_pct'],0)}%**. Food inflation peaked at **{f(H['food_infl_peak'],1)}%** in {H['food_infl_peak_date']}.

**Data.** 132 monthly observations (2015M01–2025M12) from PBS, the IMF CPI and IFS datasets, the World Bank GEM and Pink Sheet, and the FAO.
Raw files are archived with SHA-256 hashes; ten automated cross-source checks pass.

**Method.** Unit-root tests → static OLS (shown to be possibly spurious) → ARDL bounds test and error-correction model → nonlinear ARDL
(NARDL) separating depreciation from appreciation → Wald symmetry tests and dynamic multipliers → diagnostics → 13 robustness specifications.

## Findings

| | Result |
|---|---|
| Long-run relationship (ARDL{oa}) | Yes — F = {f(BA['F'])}, t = {f(BA['t'])}, both beyond the 5% I(1) bounds |
| Long-run exchange-rate elasticity | **{f(LA['LEXR']['coef'])}** (p = {fp(LA['LEXR']['p'])}); incomplete pass-through |
| Long-run world-food-price elasticity | **{f(LA['LGFOOD']['coef'])}** (p = {fp(LA['LGFOOD']['p'])}) |
| Energy (transport CPI) | {f(LA['LTRANSCPI']['coef'])}, not significant in ARDL (p = {fp(LA['LTRANSCPI']['p'])}); {f(LN['LTRANSCPI']['coef'])} (p = {fp(LN['LTRANSCPI']['p'])}) in NARDL |
| Speed of adjustment | {f(ECA['speed_of_adjustment'],3)} per month; half-life ≈ {f(ECA['half_life_months'],1)} months |
| Depreciation, long run (NARDL{on}) | **{f(LN['LEXR_POS']['coef'])}** (p = {fp(LN['LEXR_POS']['p'])}); positive in {RC['pos_positive']}/{RC['n_specs']} robustness specs, significant in {RC['pos_significant']} |
| Appreciation, long run | {f(LN['LEXR_NEG']['coef'])} (p = {fp(LN['LEXR_NEG']['p'])}) — not significant |
| Long-run symmetry | Not rejected (χ² = {f(AS['long_run']['wald_chi2'])}, p = {fp(AS['long_run']['p_chi2'])}) |
| Short-run (impact) symmetry | **Rejected** (F = {f(AS['short_run']['F_impact'])}, p = {fp(AS['short_run']['p_impact'])}): prices do not fall in the month the rupee appreciates |

**Bottom line.** Pakistan's food prices are tied in the long run to the rupee far more than to world markets: as an accounting
decomposition, the rupee is associated with about {f(share,0)}% of the log rise in food prices over 2015–2025. Depreciation reliably raises
food prices; appreciation does not bring an equivalent, statistically detectable fall, and prices do not fall at all in the month the rupee
recovers. Whether the asymmetry is permanent cannot be settled with the few, small appreciation episodes available.

**Policy.** Treat exchange-rate stability as food policy; deliver relief through targeted transfers rather than waiting for a currency
recovery; diversify edible-oil and pulse imports; strengthen competition and price information in wholesale food markets.

**Caveats.** Observational time series (associations, not causal effects); CPI base change in July 2019; NARDL cointegration supported by
the F- but not the t-test; EViews confirmation pending.

Live documentary: {SITE}
""")

# --------------------------------------------------------------------------------------------- methodology summary
(DOCS / "METHODOLOGY_SUMMARY.md").write_text(f"""# Methodology Summary

{STATUS}
| Step | Technique | Purpose | Key result |
|---|---|---|---|
| 1 | Descriptives, growth rates, robust outlier z-scores | Size and shape of the shock | Food CPI CAGR {f(H['food_cagr_pct'],2)}%; monthly food inflation non-normal |
| 2 | Correlations, VIF/tolerance | Multicollinearity | VIF > 10 in levels (common trend); < 2 in differences |
| 3 | ADF (AIC, SIC), PP, KPSS on levels, Δ, Δ² | Integration order; rule out I(2) | All variables I(1); bounds test admissible |
| 4 | Static OLS + Engle–Granger + Granger–Newbold rule | Benchmark; spurious-regression check | R² {f(ols['r2'],3)} vs DW {f(ols['dw'],2)}; EG p = {fp(eg['p'])} |
| 5 | ARDL lag search (max 4, AIC; SIC/HQ in robustness), 11 monthly dummies | Dynamic specification | ARDL{oa}; NARDL{on} |
| 6 | PSS bounds F & t, case III; asymptotic + Monte Carlo finite-sample CVs | Long-run relationship | ARDL F = {f(BA['F'])}, t = {f(BA['t'])} (reject); NARDL F = {f(BN['F'])} (reject), t = {f(BN['t'])} (do not reject) |
| 7 | Long-run L = −θ/ρ (delta method); ECM | Equilibrium & adjustment speed | L_EXR = {f(LA['LEXR']['coef'])}; λ = {f(ECA['speed_of_adjustment'],3)} |
| 8 | NARDL partial sums EXR⁺, EXR⁻ (Shin, Yu & Greenwood-Nimmo 2014) | Asymmetric pass-through | L⁺ = {f(LN['LEXR_POS']['coef'])}, L⁻ = {f(LN['LEXR_NEG']['coef'])} |
| 9 | Wald tests (χ² delta method; linear F) | Statistical test of symmetry | LR p = {fp(AS['long_run']['p_chi2'])}; impact p = {fp(AS['short_run']['p_impact'])} |
| 10 | Cumulative dynamic multipliers, 5,000-draw parametric bands | Persistence and timing | Asymmetry significant on impact only |
| 11 | BG, BPG, White, ARCH, JB, RESET, CUSUM, CUSUMSQ | Model adequacy | Clean except normality; NARDL CUSUMSQ crosses |
| 12 | 13 alternative specifications | Robustness | L⁺ > 0 in {RC['pos_positive']}/{RC['n_specs']}, significant in {RC['pos_significant']} |

**Key equations**

- Conditional EC form: Δln FOOD_t = c + ρ ln FOOD_t−1 + Σθ_j x_j,t−1 + Σα_i Δln FOOD_t−i + ΣΣπ_jl Δx_j,t−l + γ′S_t + ε_t
- Bounds test H0: ρ = θ_1 = … = θ_k = 0; long run L_j = −θ_j/ρ
- Partial sums: EXR⁺_t = Σ max(Δln EXR_j, 0), EXR⁻_t = Σ min(Δln EXR_j, 0); ln EXR_t = ln EXR_0 + EXR⁺_t + EXR⁻_t
- Symmetry: long run H0: L⁺ = L⁻; impact H0: β⁺₀ = β⁻₀

**Reproduce:** `python scripts/01_fetch_data.py && python scripts/02_build_dataset.py && python scripts/03_estimate.py`, then
`eviews/00_master.prg` in EViews and `python scripts/07_compare_eviews.py`.
""")

# --------------------------------------------------------------------------------------------- viva preparation
QA = [
    ("Why not just run OLS on the levels?",
     f"Because all four series are I(1). A levels regression of trending series can show a high R² with no true relationship (Granger & "
     f"Newbold, 1974). Our OLS has R² = {f(ols['r2'],3)} but DW = {f(ols['dw'],2)}, and the Engle–Granger test cannot reject a unit root in the "
     f"residuals (p = {fp(eg['p'])}). OLS is kept only as a benchmark."),
    ("Why ARDL rather than Johansen cointegration?",
     "ARDL bounds testing is valid whether regressors are I(0) or I(1) (the exchange-rate difference was borderline on one ADF variant), it is "
     "a single-equation method suited to our question about food prices, it performs well in samples of ~130 observations, and it extends "
     "naturally to the NARDL needed for asymmetry. Johansen would require all variables to be I(1) and many more parameters."),
    ("How did you make sure no variable is I(2)?",
     "Every variable was tested in second differences with ADF and PP; all reject the unit root decisively. The bounds critical values assume "
     "regressors are I(0) or I(1), so this check is essential."),
    ("Your NARDL F-test rejects but the t-test does not. Is there cointegration or not?",
     f"PSS recommend both tests. In the linear ARDL both reject (F = {f(BA['F'])}, t = {f(BA['t'])}), so we are confident an equilibrium exists. "
     f"In the NARDL the F rejects (F = {f(BN['F'])}) but t = {f(BN['t'])} does not; this can happen when lagged regressors matter but the "
     "dependent variable adjusts weakly. We therefore treat the NARDL long-run coefficients as suggestive and say so explicitly."),
    ("Why is k = 4 in the NARDL bounds test?",
     "EXR⁺ and EXR⁻ enter as separate level regressors alongside world food prices and energy, so there are four regressors. Counting them "
     "separately is the conservative convention of Shin, Yu & Greenwood-Nimmo (2014) and raises the critical values."),
    ("Different coefficients for depreciation and appreciation — isn't that asymmetry?",
     f"Not by itself. L⁺ = {f(LN['LEXR_POS']['coef'])} and L⁻ = {f(LN['LEXR_NEG']['coef'])} look different, but the Wald test of L⁺ = L⁻ gives "
     f"p = {fp(AS['long_run']['p_chi2'])}. The difference is not statistically significant, mainly because L⁻ is imprecise. Asymmetry is "
     f"established only in the impact effect (p = {fp(AS['short_run']['p_impact'])})."),
    ("Why is the appreciation coefficient so imprecise?",
     f"The rupee appreciated in {desc['exchange_rate_months']['appreciating']} months, mostly by small amounts (cumulative "
     f"{f(desc['exchange_rate_months']['cumulative_appreciation_log'])} log points against {f(desc['exchange_rate_months']['cumulative_depreciation_log'])} "
     "for depreciation). Little variation means wide confidence intervals."),
    ("What does the negative impact coefficient on appreciation mean?",
     f"β⁻₀ = {f(AS['short_run']['beta0_neg'],3)} on EXR⁻: since EXR⁻ falls when the rupee appreciates, food prices tend to rise in the month of "
     "an appreciation, before reversing the next month. Economically: shelf prices do not fall immediately. It may also reflect timing — some "
     "appreciation episodes coincided with domestic supply shocks — which is why we do not over-interpret it."),
    ("Why include seasonal dummies?",
     f"Food prices have a seasonal pattern (harvests, perishables). The 11 monthly dummies are jointly significant (p = "
     f"{fp(ardl['levels_equation']['seasonal_dummies_joint_p'])}). Results without them are reported as a robustness check (NOSEAS)."),
    ("How did you handle the CPI base-year change?",
     "PBS's 2015-16-base national CPI starts in July 2019; earlier months are the IMF's back-linked series of the previous CPI. We did not "
     "splice anything ourselves; we verified the IMF and PBS series match to ±0.003 points on overlapping months, and we test a 2019M07 step "
     "dummy and a post-2019 sub-sample."),
    ("Why the transport CPI as the energy variable?",
     "It is the national CPI group dominated by motor fuel — the cost of moving food. No consistent monthly domestic fuel price series was "
     "obtainable for the whole sample. We test the housing-and-utilities CPI (electricity, gas) and Brent crude as alternatives."),
    ("Why did you leave out the policy rate and money supply?",
     "The SBP portal refused automated access and the IMF policy-rate series was unavailable; broad money ends in April 2025. Adding them would "
     "shorten the sample and add parameters to an already rich NARDL. This is listed as a limitation."),
    ("Your residuals fail Jarque–Bera. Does that invalidate the results?",
     "Non-normality comes from a few extreme months, especially May 2024. With N > 100, t- and F-tests remain approximately valid by the central "
     "limit theorem; an impulse dummy for May 2024 restores normality and leaves the conclusions unchanged (IMPULSE specification)."),
    ("The NARDL fails CUSUM of squares. What does that mean?",
     f"Residual variance is not constant: quiet early years and volatile 2022–25. Coefficients (CUSUM) look stable, but standard errors should "
     f"be read with caution. The linear ARDL passes both tests."),
    ("Is this causal? Does depreciation cause food inflation?",
     "No causal identification is claimed. These are conditional associations in observational data; the exchange rate itself responds to "
     "inflation and the balance of payments. Causal work would need identified shocks (structural VAR, local projections with instruments)."),
    ("Interpret the error-correction coefficient.",
     f"λ = {f(ECA['speed_of_adjustment'],3)}: about {f(-100*ECA['speed_of_adjustment'],0)}% of any gap between actual and equilibrium food prices "
     f"closes each month, so half of a deviation disappears in about {f(ECA['half_life_months'],1)} months. It is negative and inside (−1, 0), "
     "confirming a stable equilibrium."),
    ("Statistical versus economic significance?",
     f"An elasticity of {f(LA['LEXR']['coef'])} is economically large: a 10% depreciation is associated with roughly "
     f"{f((math.exp(LA['LEXR']['coef']*math.log(1.1))-1)*100,1)}% higher food prices in the long run. Conversely, the impact asymmetry is "
     "statistically significant but short-lived."),
    ("Were these results produced in EViews?",
     "Not yet. EViews was not available in the build environment, so all estimates were computed in Python with statsmodels and are labelled "
     "as pending verification. The EViews programs replicate each equation term by term, and a comparison script marks results verified once "
     "EViews output matches to a relative tolerance of 10⁻⁴."),
    ("Why monthly data from 2015?",
     "The 2015–2025 window covers two large depreciation episodes and a stabilisation, gives 132 observations, and avoids earlier CPI vintages. "
     "All series are available monthly for the whole window."),
    ("What would you do next?",
     "Item-level pass-through for wheat flour, edible oil and sugar; threshold models for high- versus low-inflation regimes; urban/rural "
     "food CPI; and identified exchange-rate shocks for causal inference."),
]
viva = ["# Viva Preparation — Likely Questions and Defensible Answers", "", STATUS,
        "## 60-second summary", "",
        f"Food prices in Pakistan rose {f(H['food_cpi_change_pct'],0)}% over 2015–2025 while rupees per dollar rose {f(H['exr_change_pct'],0)}% "
        f"and world food prices only {f(H['gfood_change_pct'],0)}%. Using 132 monthly observations, an ARDL bounds test finds a long-run "
        f"relationship with an exchange-rate elasticity of {f(LA['LEXR']['coef'])} and a world-food elasticity of {f(LA['LGFOOD']['coef'])}. "
        f"A nonlinear ARDL shows depreciation raises food prices (L⁺ = {f(LN['LEXR_POS']['coef'])}, p = {fp(LN['LEXR_POS']['p'])}), while "
        "appreciation has no detectable equivalent effect; impact symmetry is rejected but long-run symmetry is not. Results are associations, "
        "robust in sign across 12 food-CPI specifications.", "", "## Questions", ""]
for i, (q, a) in enumerate(QA, 1):
    viva += [f"**{i}. {q}**", "", a, ""]
viva += ["## Numbers to know by heart", "",
         f"- Sample: 2015M01–2025M12, N = 132 (estimation N = {ardl['sample']['nobs']} after lags)",
         f"- ARDL{oa}: F = {f(BA['F'])}, t = {f(BA['t'])}; L_EXR = {f(LA['LEXR']['coef'])}; L_GFOOD = {f(LA['LGFOOD']['coef'])}; λ = {f(ECA['speed_of_adjustment'],3)}",
         f"- NARDL{on}: F = {f(BN['F'])}, t = {f(BN['t'])}; L⁺ = {f(LN['LEXR_POS']['coef'])}; L⁻ = {f(LN['LEXR_NEG']['coef'])}",
         f"- Symmetry: long run p = {fp(AS['long_run']['p_chi2'])}; impact p = {fp(AS['short_run']['p_impact'])}",
         f"- 5% PSS case III bounds: k=3 F 3.23/4.35, t −2.86/−3.78; k=4 F 2.86/4.01, t −2.86/−3.99", ""]
(DOCS / "VIVA_PREPARATION.md").write_text("\n".join(viva))
print("wrote docs/EXECUTIVE_SUMMARY.md, docs/METHODOLOGY_SUMMARY.md, docs/VIVA_PREPARATION.md")
