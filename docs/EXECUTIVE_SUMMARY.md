# The Price of a Falling Rupee — Executive Summary

> **Status:** every estimate here was computed in Python (statsmodels 0.15) by `scripts/03_estimate.py`. EViews programs that reproduce each specification are in `/eviews`; results are labelled *pending EViews verification* until `scripts/07_compare_eviews.py` confirms them.

**Question.** How far do rupee depreciation, world food prices and domestic energy costs explain Pakistan's food inflation — and does
depreciation affect food prices more strongly or more persistently than appreciation?

**Why it matters.** Food is 34.58% of Pakistan's national CPI basket. Between January 2015 and December 2025 the food price index rose
**194%** (10.4% a year), rupees per US dollar rose **178%**, and
world food prices (FAO) rose only **23%**. Food inflation peaked at **48.7%** in 2023-05.

**Data.** 132 monthly observations (2015M01–2025M12) from PBS, the IMF CPI and IFS datasets, the World Bank GEM and Pink Sheet, and the FAO.
Raw files are archived with SHA-256 hashes; ten automated cross-source checks pass.

**Method.** Unit-root tests → static OLS (shown to be possibly spurious) → ARDL bounds test and error-correction model → nonlinear ARDL
(NARDL) separating depreciation from appreciation → Wald symmetry tests and dynamic multipliers → diagnostics → 13 robustness specifications.

## Findings

| | Result |
|---|---|
| Long-run relationship (ARDL(2, 1, 3, 2)) | Yes — F = 7.54, t = −3.83, both beyond the 5% I(1) bounds |
| Long-run exchange-rate elasticity | **0.64** (p = 0.004); incomplete pass-through |
| Long-run world-food-price elasticity | **0.61** (p = 0.002) |
| Energy (transport CPI) | 0.21, not significant in ARDL (p = 0.359); 0.50 (p = 0.031) in NARDL |
| Speed of adjustment | −0.120 per month; half-life ≈ 5.4 months |
| Depreciation, long run (NARDL(1, 0, 1, 0, 2)) | **0.53** (p = 0.043); positive in 12/12 robustness specs, significant in 9 |
| Appreciation, long run | 1.18 (p = 0.291) — not significant |
| Long-run symmetry | Not rejected (χ² = 0.47, p = 0.495) |
| Short-run (impact) symmetry | **Rejected** (F = 5.35, p = 0.023): prices do not fall in the month the rupee appreciates |

**Bottom line.** Pakistan's food prices are tied in the long run to the rupee far more than to world markets: as an accounting
decomposition, the rupee is associated with about 61% of the log rise in food prices over 2015–2025. Depreciation reliably raises
food prices; appreciation does not bring an equivalent, statistically detectable fall, and prices do not fall at all in the month the rupee
recovers. Whether the asymmetry is permanent cannot be settled with the few, small appreciation episodes available.

**Policy.** Treat exchange-rate stability as food policy; deliver relief through targeted transfers rather than waiting for a currency
recovery; diversify edible-oil and pulse imports; strengthen competition and price information in wholesale food markets.

**Caveats.** Observational time series (associations, not causal effects); CPI base change in July 2019; NARDL cointegration supported by
the F- but not the t-test; EViews confirmation pending.

Live documentary: https://the-price-of-a-falling-rupee.vercel.app
