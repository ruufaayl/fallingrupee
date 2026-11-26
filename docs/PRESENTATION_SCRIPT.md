# Presentation Script — word for word

Read naturally; the bold title is what is on the slide.

## Member 1

**Slide 1 — Does a weaker rupee make food more expensive in Pakistan?**

Assalam-o-Alaikum. Our project is called The Price of a Falling Rupee. Between 2015 and 2025, food prices in Pakistan went up 194 percent. The dollar rate went up 178 percent. World food prices went up only 23 percent. So we asked: is the weak rupee driving our food inflation? I will introduce the problem, our variables, our equation and our hypotheses. Then my teammates will show the data, the tests and the results.

**Slide 2 — Food nearly tripled in price. Why?**

Here is the problem. Food is about one third of what a Pakistani family spends. From 2015 to 2025 food prices nearly tripled, and food inflation reached 48.7 percent in May 2023. In the graph, the red line is food inflation and the yellow line is how fast the rupee lost value. They rise and fall together. The green line — world food prices — follows a different pattern. That is our problem statement.

**Slide 3 — What we wanted to find out**

Our research question: does a weaker rupee, along with world food prices and fuel costs, raise food inflation in Pakistan — and does a stronger rupee bring it back down? People say prices go up like a rocket and come down like a feather; we test that too.

**Slide 4 — Dependent and independent variables**

These are our variables. The dependent variable is Food Inflation — the monthly percentage change in Pakistan's food price index. We have four independent variables. X1, Rupee Depreciation: the monthly change in rupees per dollar — positive means the rupee got weaker. X2, World Food Inflation from the FAO. X3, Fuel and Transport Inflation from the transport price index. And X4, last month's food inflation — this is the autoregressive term, because price rises tend to continue. All the X variables are taken from the previous month, because prices need time to react.

**Slide 5 — 132 months · 4 official sources**

Our data is monthly, from January 2015 to December 2025 — 132 months, no missing values. It comes from the Pakistan Bureau of Statistics, the World Bank and the FAO. We combined everything into one Excel file. The 'Regression Data' sheet has the exact monthly percentage changes we used, so anyone can re-run our regression.

**Slide 6 — One equation (OLS regression)**

This is our one equation — a standard regression. Food inflation on the left. On the right: rupee depreciation, world food inflation, fuel inflation and last month's food inflation, each with a beta. Each beta tells us how many percentage points food inflation moves when that variable moves by one point. For example, if beta-one were 0.5, a 1 percent weaker rupee would mean food prices 0.5 percent higher the next month. We estimate it with ordinary least squares, OLS.

**Slide 7 — H₀ (no effect) vs H₁ (effect)**

These are our six hypotheses. H-zero always says 'no effect'; H-one says 'there is an effect'. H1 to H4 test each beta with a t-test. H5 tests the whole model with the F-test. H6 asks whether a rising rupee has the same effect as a falling rupee. Our rule: if the p-value is below 0.05, we reject H-zero. Now my teammate will show the data and the tests.

## Member 2

**Slide 8 — The data and the tests before the regression**

One sentence: “I will now take you through the data and the tests before the regression.”

**Slide 9 — All four series, January 2015 = 100**

Thank you. This graph sets all four series to 100 in January 2015. Food prices — red — end near 294, the dollar rate — yellow — near 278, but world food prices — green — only near 123. Food prices climb with the rupee, especially in 2019 and 2022–23.

**Slide 10 — Summary of the data (N = 132)**

These are the descriptive statistics: average, middle value, spread, lowest and highest. Food prices grew about 10.4 percent a year, the dollar rate 9.8 percent, world food prices only 1.9 percent. On average, food prices rose about 0.84 percent every month.

**Slide 11 — Which variables move together?**

The correlation matrix shows how closely variables move together, from minus one to plus one. On the left, in levels, food prices and the dollar rate have r = 0.98 — almost perfect. But anything that rises over time looks correlated, so levels can mislead. On the right are the monthly changes we actually use: food inflation and last month's rupee depreciation have r = 0.23. Positive, and realistic for monthly data.

**Slide 12 — Stationary or non-stationary?**

Next, stationarity, with the ADF unit root test. H-zero says the series is non-stationary — it keeps trending. In levels all p-values are above 0.05, so all four are non-stationary. That is a problem: regressing trending data can give fake results. So we use monthly percentage changes. For the changes, all p-values are below 0.001 — stationary. Our regression is safe.

**Slide 13 — Are the X variables too similar?**

Last check before the regression: multicollinearity. If the X variables are too similar, the regression cannot separate their effects. We measure it with the Variance Inflation Factor. A VIF above 10 is a problem. Our highest VIF is 1.47 — close to 1 — so there is no multicollinearity. Now my teammate will present the regression results.

## Member 3

**Slide 14 — The regression results and diagnostic tests**

One sentence: “I will now take you through the regression results and diagnostic tests.”

**Slide 15 — The estimated equation**

Thank you. Here is the regression output. The rupee depreciation coefficient is 0.27 with a p-value of 0.007: if the rupee falls 1 percent, food prices rise about 0.27 percent the next month. Last month's food inflation has 0.18, p = 0.040: food inflation carries over. World food inflation and fuel inflation are not significant. The F-test p-value is 0.009, so the model as a whole is significant. R-squared is 0.10: monthly food prices also jump with weather and harvests, so a low R-squared is normal here.

**Slide 16 — How big is each effect?**

This chart shows each coefficient with its 95 percent range. If the range crosses the zero line, the effect is not significant. Rupee depreciation and last month's food inflation are clearly above zero. World food and fuel ranges cross zero.

**Slide 17 — Decision for every hypothesis**

Here is the decision for every hypothesis. H1, rupee: p below 0.05, reject H-zero — a weaker rupee raises food inflation. H2, world food, and H3, fuel: p above 0.05, we fail to reject — no clear monthly effect. H4, autoregression: reject — food inflation persists. H5, the F-test: reject — the model is significant. H6, asymmetry: we fail to reject — explained on the next slides.

**Slide 18 — Can we trust the regression?**

Before trusting the result, we checked the assumptions. Autocorrelation: Durbin-Watson is 2.04, close to the ideal 2, and the Breusch-Godfrey test p is 0.207 — no autocorrelation. Heteroskedasticity: Breusch-Pagan p = 0.830 and White p = 0.555 — constant variance. Normality: Jarque-Bera p = 0.085 — errors are normal. Specification: Ramsey RESET p = 0.587 — correct form. Every diagnostic test passes, so our results can be trusted.

**Slide 19 — Rupee falls vs rupee rises**

Now the second part of our question. We split last month's rupee change into months when the rupee fell and months when it rose. When the rupee falls, the effect is 0.33, p = 0.004 — significant. When the rupee rises, the effect is -0.00, p = 0.988 — basically zero. So a falling rupee raises food prices, but a rising rupee does not bring them down. However, the Wald F-test of equal effects has p = 0.247, so we cannot statistically prove the difference — the rupee rose in only 49 months.

**Slide 20 — What we found**

To conclude. One: a weaker rupee raises food inflation the next month — our main finding. Two: food inflation has momentum. Three: world food and fuel prices showed no clear monthly effect. Four: a rising rupee did not bring food prices down. And the model passes every diagnostic test. For policy: keep the rupee stable, treat a falling rupee as an early warning, and help poor families directly. Thank you — we are happy to take questions.

**Slide 21 — A currency can recover in a season.**

Close here and invite questions. All three members stand together for the Q&A.
