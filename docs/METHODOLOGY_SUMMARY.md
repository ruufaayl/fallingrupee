# Methodology Summary

> **Status:** every estimate here was computed in Python (statsmodels 0.15) by `scripts/03_estimate.py`. EViews programs that reproduce each specification are in `/eviews`; results are labelled *pending EViews verification* until `scripts/07_compare_eviews.py` confirms them.

| Step | Technique | Purpose | Key result |
|---|---|---|---|
| 1 | Descriptives, growth rates, robust outlier z-scores | Size and shape of the shock | Food CPI CAGR 10.38%; monthly food inflation non-normal |
| 2 | Correlations, VIF/tolerance | Multicollinearity | VIF > 10 in levels (common trend); < 2 in differences |
| 3 | ADF (AIC, SIC), PP, KPSS on levels, Δ, Δ² | Integration order; rule out I(2) | All variables I(1); bounds test admissible |
| 4 | Static OLS + Engle–Granger + Granger–Newbold rule | Benchmark; spurious-regression check | R² 0.982 vs DW 0.25; EG p = 0.159 |
| 5 | ARDL lag search (max 4, AIC; SIC/HQ in robustness), 11 monthly dummies | Dynamic specification | ARDL(2, 1, 3, 2); NARDL(1, 0, 1, 0, 2) |
| 6 | PSS bounds F & t, case III; asymptotic + Monte Carlo finite-sample CVs | Long-run relationship | ARDL F = 7.54, t = −3.83 (reject); NARDL F = 5.36 (reject), t = −2.39 (do not reject) |
| 7 | Long-run L = −θ/ρ (delta method); ECM | Equilibrium & adjustment speed | L_EXR = 0.64; λ = −0.120 |
| 8 | NARDL partial sums EXR⁺, EXR⁻ (Shin, Yu & Greenwood-Nimmo 2014) | Asymmetric pass-through | L⁺ = 0.53, L⁻ = 1.18 |
| 9 | Wald tests (χ² delta method; linear F) | Statistical test of symmetry | LR p = 0.495; impact p = 0.023 |
| 10 | Cumulative dynamic multipliers, 5,000-draw parametric bands | Persistence and timing | Asymmetry significant on impact only |
| 11 | BG, BPG, White, ARCH, JB, RESET, CUSUM, CUSUMSQ | Model adequacy | Clean except normality; NARDL CUSUMSQ crosses |
| 12 | 13 alternative specifications | Robustness | L⁺ > 0 in 12/12, significant in 9 |

**Key equations**

- Conditional EC form: Δln FOOD_t = c + ρ ln FOOD_t−1 + Σθ_j x_j,t−1 + Σα_i Δln FOOD_t−i + ΣΣπ_jl Δx_j,t−l + γ′S_t + ε_t
- Bounds test H0: ρ = θ_1 = … = θ_k = 0; long run L_j = −θ_j/ρ
- Partial sums: EXR⁺_t = Σ max(Δln EXR_j, 0), EXR⁻_t = Σ min(Δln EXR_j, 0); ln EXR_t = ln EXR_0 + EXR⁺_t + EXR⁻_t
- Symmetry: long run H0: L⁺ = L⁻; impact H0: β⁺₀ = β⁻₀

**Reproduce:** `python scripts/01_fetch_data.py && python scripts/02_build_dataset.py && python scripts/03_estimate.py`, then
`eviews/00_master.prg` in EViews and `python scripts/07_compare_eviews.py`.
