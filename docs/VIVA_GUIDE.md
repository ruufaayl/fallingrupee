# Viva Guide — simple and complete

Each member: learn your **Must know** list by heart, then practise the questions aloud.

## Member 1

**Must know**

- Problem: food prices +194%, dollar rate +178%, world food prices +23% (Jan 2015 → Dec 2025).
- Dependent variable (Y): Food Prices — PBS national food price index.
- Independent variables: X₁ Dollar Rate (World Bank) · X₂ World Food Prices (FAO) · X₃ Fuel & Transport Costs (PBS transport index).
- Data: monthly, Jan 2015 – Dec 2025, 132 months, no missing values.
- Equation: Food Prices = β₀ + β₁ Dollar Rate + β₂ World Food Prices + β₃ Fuel & Transport Costs + error
- H₀ always says “no effect”; H₁ says “there is an effect”. Reject H₀ when p < 0.05.

**Likely questions**

**Q: Why did you choose these variables?**

A: Because they are the three main ways a weak rupee and the outside world can push food prices: imported food and inputs (dollar rate), world market prices (FAO), and the cost of fuel to grow and move food (transport index).

**Q: What is a dependent variable?**

A: The thing we want to explain — here, food prices. The independent variables are the possible causes.

**Q: Why monthly data?**

A: Prices change every month, and monthly data gives us 132 observations — enough to see how effects build up over time.

**Q: Why 2015 to 2025?**

A: It covers the recent big falls of the rupee (2019 and 2022–23) and the recovery after, with all data available from official sources.

**Q: Where did the data come from?**

A: Pakistan Bureau of Statistics, World Bank and FAO. All four are combined month by month in the Excel sheet we submitted.

**Q: What does β mean?**

A: How much food prices change, in percent, when that variable changes by 1 percent. It is called an elasticity because we use logarithms.

**Q: What is H₀ and H₁?**

A: H₀ is the null hypothesis — no effect. H₁ is the alternative — there is an effect. The test tells us if we have enough evidence to reject H₀.

**Q: Why logarithms?**

A: So the coefficients read as percentages, and so big numbers like 280 rupees and small ones like 100 index points are comparable.

## Member 2

**Must know**

- Food prices grew 10.4% a year, the dollar rate 9.8%, world food prices 1.9%.
- Food inflation averaged 10.5% and peaked at 48.7% in May 2023.
- Correlation Food Prices vs Dollar Rate ≈ 0.98 — very high, but correlation ≠ cause.
- ADF test: H₀ = not stationary. Levels p > 0.05 (trend), first differences p < 0.05 → all variables I(1).
- Bounds test: F = 7.54 > 5% critical value 4.35 → reject H₀ → long-run relationship.
- ECT = -0.12 → about 12% of the gap closes each month; half-life ≈ 5.4 months.

**Likely questions**

**Q: What is stationarity?**

A: A stationary series moves around a fixed average. Prices keep climbing, so they are not stationary in levels — but their monthly changes are.

**Q: Why does stationarity matter?**

A: Running ordinary regression on two trending series can show a relationship even when there is none (a 'spurious regression'). We had to check first.

**Q: What does I(1) mean?**

A: The series becomes stationary after taking the change once. ARDL works when variables are I(0) or I(1), not I(2) — ours are all I(1).

**Q: Why ARDL and not simple OLS?**

A: ARDL handles trending (I(1)) data and lets effects build up over several months. Simple OLS ignores both.

**Q: What does the bounds test tell us?**

A: Whether the variables are tied together in the long run. Our F statistic is above the upper critical value, so yes.

**Q: What is the error correction term?**

A: It shows how fast food prices come back to their long-run path. Negative and significant means the relationship is stable.

**Q: High correlation — isn't that enough?**

A: No. Anything that rises over time looks correlated. That is why we ran the unit root and bounds tests.

**Q: How did you choose the number of lags?**

A: The software tried every combination up to 4 months and picked the one with the lowest Akaike Information Criterion (AIC).

## Member 3

**Must know**

- Estimated equation: Food Prices = -2.22 + 0.64 × Dollar Rate + 0.61 × World Food Prices + 0.21 × Fuel & Transport Costs
- Dollar rate: 0.64, p = 0.004 → reject H₀ (10% weaker rupee → ≈ 6.3% dearer food).
- World food prices: 0.61, p = 0.002 → reject H₀.
- Fuel & transport: 0.21, p = 0.359 → fail to reject H₀ (no clear effect).
- Asymmetry: rupee falls 1% → food +0.53% (p = 0.043); in the month the rupee rises, food does not fall. Wald short run p = 0.023 (different); long run p = 0.495 (can't tell).
- Diagnostics: serial correlation ✓, heteroskedasticity ✓, RESET ✓, CUSUM stability ✓, normality ✗ (a few extreme months).

**Likely questions**

**Q: What is your main finding?**

A: A weaker rupee clearly raises food prices: a 10% rise in the dollar rate goes with about 6.3% higher food prices in the long run.

**Q: Why is fuel & transport not significant?**

A: Its p-value is 0.36, above 0.05, so we cannot separate its effect from zero. The most likely reason: fuel prices move almost exactly with the rupee (correlation 0.98), so once the rupee is in the model, fuel adds little extra information.

**Q: What does 'fail to reject H₀' mean?**

A: We do not have enough evidence of an effect. It does not prove there is zero effect.

**Q: What is the Wald test?**

A: A test of whether two coefficients are equal. We used it to check if a falling rupee and a rising rupee have the same effect.

**Q: So do prices fall when the rupee recovers?**

A: Not in the same month — they keep rising a little. Over the long run we cannot tell, because there were only a few months when the rupee got stronger.

**Q: Normality failed — is the model wrong?**

A: No. A few extreme months (like May 2024) make the errors non-normal. With 128 months the tests are still reliable, and removing that month's effect gives the same conclusions.

**Q: Is this cause and effect?**

A: We show a strong, tested link — not a laboratory proof. Other things also move prices. We say 'associated with', not 'caused by'.

**Q: What should the government do?**

A: Keep the rupee stable, help poor families directly instead of waiting for the rupee to recover, and import food and inputs from more sources.

**Q: What is R² of your model?**

A: 0.999 — the model explains almost all the movement in food prices, but in time series that is normal, so we rely on the tests instead.

## Any member may be asked

**Q: What is a p-value?**

A: The chance of seeing a result this strong if H₀ were true. Below 0.05 means that chance is very small, so we reject H₀.

**Q: What is the 5% significance level?**

A: Our cut-off: we accept a 5% risk of saying there is an effect when there is not.

**Q: What software did you use?**

A: A statistical package for time-series econometrics (ARDL, bounds test, diagnostics). Answer honestly with the software you actually used to run the estimates.

**Q: One sentence summary?**

A: The rupee's fall is paid for at the market: when the rupee weakens, food gets dearer — and it does not get cheaper again quickly when the rupee recovers.

## The 30-second answer to the research question

1. YES — a weaker rupee raises food prices. A 10% rise in the dollar rate goes with about 6.3% higher food prices in the long run.
2. YES — world food prices matter too: a 10% rise goes with about 5.9% higher food prices.
3. NOT CLEAR — fuel & transport costs: the effect is positive but not statistically significant.
4. When the rupee gets stronger, food prices do NOT fall in the same month. Over the long run we cannot prove the fall is smaller — there were too few months of a rising rupee to tell.
