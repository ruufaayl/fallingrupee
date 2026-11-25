# Viva Preparation — Likely Questions and Defensible Answers

> **Status:** every estimate here was computed in Python (statsmodels 0.15) by `scripts/03_estimate.py`. EViews programs that reproduce each specification are in `/eviews`; results are labelled *pending EViews verification* until `scripts/07_compare_eviews.py` confirms them.

## 60-second summary

Food prices in Pakistan rose 194% over 2015–2025 while rupees per dollar rose 178% and world food prices only 23%. Using 132 monthly observations, an ARDL bounds test finds a long-run relationship with an exchange-rate elasticity of 0.64 and a world-food elasticity of 0.61. A nonlinear ARDL shows depreciation raises food prices (L⁺ = 0.53, p = 0.043), while appreciation has no detectable equivalent effect; impact symmetry is rejected but long-run symmetry is not. Results are associations, robust in sign across 12 food-CPI specifications.

## Questions

**1. Why not just run OLS on the levels?**

Because all four series are I(1). A levels regression of trending series can show a high R² with no true relationship (Granger & Newbold, 1974). Our OLS has R² = 0.982 but DW = 0.25, and the Engle–Granger test cannot reject a unit root in the residuals (p = 0.159). OLS is kept only as a benchmark.

**2. Why ARDL rather than Johansen cointegration?**

ARDL bounds testing is valid whether regressors are I(0) or I(1) (the exchange-rate difference was borderline on one ADF variant), it is a single-equation method suited to our question about food prices, it performs well in samples of ~130 observations, and it extends naturally to the NARDL needed for asymmetry. Johansen would require all variables to be I(1) and many more parameters.

**3. How did you make sure no variable is I(2)?**

Every variable was tested in second differences with ADF and PP; all reject the unit root decisively. The bounds critical values assume regressors are I(0) or I(1), so this check is essential.

**4. Your NARDL F-test rejects but the t-test does not. Is there cointegration or not?**

PSS recommend both tests. In the linear ARDL both reject (F = 7.54, t = −3.83), so we are confident an equilibrium exists. In the NARDL the F rejects (F = 5.36) but t = −2.39 does not; this can happen when lagged regressors matter but the dependent variable adjusts weakly. We therefore treat the NARDL long-run coefficients as suggestive and say so explicitly.

**5. Why is k = 4 in the NARDL bounds test?**

EXR⁺ and EXR⁻ enter as separate level regressors alongside world food prices and energy, so there are four regressors. Counting them separately is the conservative convention of Shin, Yu & Greenwood-Nimmo (2014) and raises the critical values.

**6. Different coefficients for depreciation and appreciation — isn't that asymmetry?**

Not by itself. L⁺ = 0.53 and L⁻ = 1.18 look different, but the Wald test of L⁺ = L⁻ gives p = 0.495. The difference is not statistically significant, mainly because L⁻ is imprecise. Asymmetry is established only in the impact effect (p = 0.023).

**7. Why is the appreciation coefficient so imprecise?**

The rupee appreciated in 48 months, mostly by small amounts (cumulative −0.37 log points against 1.39 for depreciation). Little variation means wide confidence intervals.

**8. What does the negative impact coefficient on appreciation mean?**

β⁻₀ = −0.464 on EXR⁻: since EXR⁻ falls when the rupee appreciates, food prices tend to rise in the month of an appreciation, before reversing the next month. Economically: shelf prices do not fall immediately. It may also reflect timing — some appreciation episodes coincided with domestic supply shocks — which is why we do not over-interpret it.

**9. Why include seasonal dummies?**

Food prices have a seasonal pattern (harvests, perishables). The 11 monthly dummies are jointly significant (p = < 0.001). Results without them are reported as a robustness check (NOSEAS).

**10. How did you handle the CPI base-year change?**

PBS's 2015-16-base national CPI starts in July 2019; earlier months are the IMF's back-linked series of the previous CPI. We did not splice anything ourselves; we verified the IMF and PBS series match to ±0.003 points on overlapping months, and we test a 2019M07 step dummy and a post-2019 sub-sample.

**11. Why the transport CPI as the energy variable?**

It is the national CPI group dominated by motor fuel — the cost of moving food. No consistent monthly domestic fuel price series was obtainable for the whole sample. We test the housing-and-utilities CPI (electricity, gas) and Brent crude as alternatives.

**12. Why did you leave out the policy rate and money supply?**

The SBP portal refused automated access and the IMF policy-rate series was unavailable; broad money ends in April 2025. Adding them would shorten the sample and add parameters to an already rich NARDL. This is listed as a limitation.

**13. Your residuals fail Jarque–Bera. Does that invalidate the results?**

Non-normality comes from a few extreme months, especially May 2024. With N > 100, t- and F-tests remain approximately valid by the central limit theorem; an impulse dummy for May 2024 restores normality and leaves the conclusions unchanged (IMPULSE specification).

**14. The NARDL fails CUSUM of squares. What does that mean?**

Residual variance is not constant: quiet early years and volatile 2022–25. Coefficients (CUSUM) look stable, but standard errors should be read with caution. The linear ARDL passes both tests.

**15. Is this causal? Does depreciation cause food inflation?**

No causal identification is claimed. These are conditional associations in observational data; the exchange rate itself responds to inflation and the balance of payments. Causal work would need identified shocks (structural VAR, local projections with instruments).

**16. Interpret the error-correction coefficient.**

λ = −0.120: about 12% of any gap between actual and equilibrium food prices closes each month, so half of a deviation disappears in about 5.4 months. It is negative and inside (−1, 0), confirming a stable equilibrium.

**17. Statistical versus economic significance?**

An elasticity of 0.64 is economically large: a 10% depreciation is associated with roughly 6.3% higher food prices in the long run. Conversely, the impact asymmetry is statistically significant but short-lived.

**18. Were these results produced in EViews?**

Not yet. EViews was not available in the build environment, so all estimates were computed in Python with statsmodels and are labelled as pending verification. The EViews programs replicate each equation term by term, and a comparison script marks results verified once EViews output matches to a relative tolerance of 10⁻⁴.

**19. Why monthly data from 2015?**

The 2015–2025 window covers two large depreciation episodes and a stabilisation, gives 132 observations, and avoids earlier CPI vintages. All series are available monthly for the whole window.

**20. What would you do next?**

Item-level pass-through for wheat flour, edible oil and sugar; threshold models for high- versus low-inflation regimes; urban/rural food CPI; and identified exchange-rate shocks for causal inference.

## Numbers to know by heart

- Sample: 2015M01–2025M12, N = 132 (estimation N = 128 after lags)
- ARDL(2, 1, 3, 2): F = 7.54, t = −3.83; L_EXR = 0.64; L_GFOOD = 0.61; λ = −0.120
- NARDL(1, 0, 1, 0, 2): F = 5.36, t = −2.39; L⁺ = 0.53; L⁻ = 1.18
- Symmetry: long run p = 0.495; impact p = 0.023
- 5% PSS case III bounds: k=3 F 3.23/4.35, t −2.86/−3.78; k=4 F 2.86/4.01, t −2.86/−3.99
