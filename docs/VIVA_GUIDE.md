# Viva Guide — simple and complete

Each member: learn your **Must know** list by heart, then practise the questions aloud.

## Member 1

**Must know**

- Problem: food prices +194%, dollar rate +178%, world food prices +23% (Jan 2015 → Dec 2025).
- Dependent variable (Y): Food Inflation — monthly % change in the PBS national food price index.
- Independent variables (previous month): X₁ Rupee Depreciation (World Bank) · X₂ World Food Inflation (FAO) · X₃ Fuel & Transport Inflation (PBS) · X₄ Last Month's Food Inflation (autoregressive term).
- Data: monthly, Jan 2015 – Dec 2025, 132 observations, no missing values.
- Equation: Food Inflation = β₀ + β₁ Rupee Depreciation + β₂ World Food Inflation + β₃ Fuel & Transport Inflation + β₄ Last Month's Food Inflation + error
- Six hypotheses: H1–H4 t-tests on each β, H5 F-test on the whole model, H6 Wald F-test for asymmetry. Reject H₀ when p < 0.05.

**Likely questions**

**Q: Why these variables?**

A: They are the main channels: a weaker rupee makes imports dearer, world prices set the cost of imported food, fuel moves food to market, and last month's inflation captures momentum.

**Q: What is the dependent variable?**

A: Food inflation — the thing we explain. The independent variables are the possible causes.

**Q: Why monthly % changes instead of price levels?**

A: Price levels keep trending upward (non-stationary). Regressing trending series can show fake relationships, so we use monthly % changes, which are stationary.

**Q: Why use last month's values for the X variables?**

A: Prices take time to react — shops and wholesalers re-price after costs change. Using last month also means today's food prices cannot affect the X's (no reverse causation within the month).

**Q: What is the autoregressive term?**

A: Last month's food inflation (X₄). It is 'auto' because it is the dependent variable's own past value. It captures momentum — price rises tend to continue.

**Q: What does β mean?**

A: How many percentage points food inflation changes when that X changes by one percentage point, holding the others constant.

**Q: What are H₀ and H₁?**

A: H₀ (null) says no effect; H₁ (alternative) says there is an effect. We reject H₀ if the p-value is below 0.05.

**Q: Where is the data from?**

A: Pakistan Bureau of Statistics, World Bank and FAO — all combined month by month in our Excel file.

## Member 2

**Must know**

- Food prices grew 10.4% a year, dollar rate 9.8%, world food 1.9%; food inflation averaged 0.84% per month.
- Correlation in levels: food vs dollar r = 0.98. In monthly changes: food inflation vs last month's depreciation r = 0.23.
- Correlation is not causation — trending series always look correlated, which is why we test stationarity.
- ADF test, H₀ = non-stationary: levels p > 0.05 (non-stationary); monthly % changes p < 0.001 (stationary).
- Multicollinearity: highest VIF = 1.47 (problem only if > 10) → none.

**Likely questions**

**Q: What is stationarity?**

A: A stationary series moves around a fixed average with a stable spread. Prices keep rising, so they are non-stationary; their monthly % changes are stationary.

**Q: Why does non-stationarity matter?**

A: Two trending series can look strongly related even when they are not — a 'spurious regression'. That is why we tested first and then used % changes.

**Q: What is the ADF test?**

A: The Augmented Dickey-Fuller test. H₀: the series has a unit root (non-stationary). If p < 0.05 we reject H₀ and call it stationary.

**Q: Why is correlation in levels 0.98 but only 0.23 in changes?**

A: Levels share a common upward trend, which inflates correlation. Monthly changes remove the trend, so the 0.23 is the honest month-to-month link.

**Q: What is multicollinearity?**

A: When the X variables are so similar that the regression cannot separate their effects. It makes coefficients unstable.

**Q: What is VIF?**

A: Variance Inflation Factor = 1 ÷ (1 − R²) from regressing one X on the others. Above 10 is a problem; ours are all about 1–1.5.

**Q: Why is VIF low even though the rupee and fuel prices move together in levels?**

A: In monthly changes they move much less together (r ≈ 0.5), so each variable keeps its own information.

## Member 3

**Must know**

- Estimated equation: Food Inflation = 0.50 + 0.27 Rupee Depreciation + 0.12 World Food Inflation − 0.05 Fuel & Transport Inflation + 0.18 Last Month's Food Inflation
- Rupee depreciation β₁ = 0.266, t = 2.75, p = 0.007 → significant (1% weaker rupee → food prices +0.27% next month).
- Last month's food inflation β₄ = 0.183, p = 0.040 → significant (momentum). World food (p = 0.122) and fuel (p = 0.428) not significant.
- F = 3.56, p = 0.009 → model significant. R² = 0.101.
- Diagnostics: DW = 2.04, BG p = 0.207 (no autocorrelation); BP p = 0.830, White p = 0.555 (no heteroskedasticity); JB p = 0.085 (normal); RESET p = 0.587 (correct form).
- Asymmetry: rupee falls 0.33 (p = 0.004); rupee rises -0.00 (p = 0.988); Wald F p = 0.247 → difference not proven.

**Likely questions**

**Q: What is your main finding?**

A: A weaker rupee raises food inflation the next month: a 1% depreciation adds about 0.27% to food prices (p = 0.007).

**Q: Your R² is only 0.10 — is the model bad?**

A: No. Monthly food prices also jump with weather, harvests, Ramadan and policy, which no macro model fully captures. The F-test shows the model is significant, and the coefficients we care about are significant. Monthly inflation regressions typically have low R².

**Q: What is autocorrelation and how did you test it?**

A: Errors that repeat from month to month. Durbin-Watson is 2.04 (close to 2 = none), and Breusch-Godfrey with 12 lags gives p = 0.207 — no autocorrelation. We rely on Breusch-Godfrey because DW is less reliable when the model has a lagged dependent variable.

**Q: What is heteroskedasticity?**

A: When the size of the errors changes with the X's. Breusch-Pagan (p = 0.830) and White (p = 0.555) both fail to reject constant variance — no heteroskedasticity.

**Q: Why are world food prices not significant?**

A: Their p-value is above 0.05, so we cannot separate their monthly effect from zero. Possible reasons: world price changes reach Pakistani shops slowly and unevenly, and over the whole decade world food prices rose only 23% — far less than Pakistan's food prices — so they explain little of Pakistan's food inflation.

**Q: What does 'fail to reject H₀' mean?**

A: We do not have enough evidence of an effect. It does not prove the effect is exactly zero.

**Q: Explain the asymmetry result.**

A: When the rupee fell, food prices rose (β = 0.33, significant). When the rupee rose, food prices did not fall (β ≈ 0). But the test that they differ gives p = 0.247, so we cannot prove it statistically — the rupee rose in only 49 months.

**Q: Is this cause and effect?**

A: We show a tested link with a time order (the rupee moves first, food prices follow), but not a laboratory proof. We say 'associated with'.

**Q: What should policymakers do?**

A: Keep the rupee stable, treat a falling rupee as an early warning for food inflation, and support poor families directly rather than waiting for the rupee to recover.

## Any member may be asked

**Q: What is OLS?**

A: Ordinary Least Squares — it draws the line (or plane) that makes the squared errors as small as possible.

**Q: What is a p-value?**

A: The probability of seeing a result this strong if H₀ were true. Below 0.05 → that is unlikely, so we reject H₀.

**Q: What is the t-test vs the F-test?**

A: The t-test checks one coefficient at a time; the F-test checks whether all the slopes together are zero.

**Q: What software did you use?**

A: Answer with the software you actually used. The regression can be re-run in Excel (Data Analysis ▸ Regression) or EViews from the 'Regression Data' sheet and gives the same numbers.

**Q: One sentence summary?**

A: When the rupee falls, food prices follow a month later — and nothing in our data shows them coming back down when the rupee recovers.

## The 30-second answer to the research question

1. YES — a weaker rupee raises food inflation. A 1% fall in the rupee adds about 0.27% to food prices the next month (about 0.33% in total once the carry-over is included). Significant at 1% (p = 0.007).
2. Food inflation has momentum: about 18% of last month's rise carries into this month (p = 0.040).
3. NO clear month-to-month effect of world food prices (p = 0.122) or fuel & transport costs (p = 0.428).
4. A rising rupee showed no effect on food prices (-0.00, p = 0.988), while a falling rupee did (0.33, p = 0.004) — but the difference is not statistically proven (p = 0.247).
5. The model passes all diagnostic tests: no multicollinearity, no autocorrelation, no heteroskedasticity, normal errors, correct form.
