# Presentation Script — word for word

Read naturally; the bold title is what is on the slide.

## Member 1

**Slide 1 — Does a weaker rupee make food more expensive in Pakistan?**

Assalam-o-Alaikum. Our project is called The Price of a Falling Rupee. In one line: between 2015 and 2025, food prices in Pakistan went up 194 percent. The dollar rate went up 178 percent. But world food prices went up only 23 percent. So we asked: is the weak rupee the reason our food became so expensive? I will introduce the problem, our variables, our equation and our hypotheses. Then my teammates will show the data, the tests and the results.

**Slide 2 — Food nearly tripled in price. Why?**

Here is the problem. Food is about one third of what a normal Pakistani family spends. From 2015 to 2025 food prices nearly tripled. Food inflation hit 48.7 percent in May 2023 — the highest in our sample. At the same time the rupee became much weaker against the dollar. Look at the graph: the red line is food inflation, the yellow line is how fast the rupee was losing value. They rise and fall together. The green line — world food prices — does not follow the same pattern. That is our problem statement.

**Slide 3 — What we wanted to find out**

Our research question has two parts. First: do a weaker rupee, world food prices and fuel costs raise food prices in Pakistan? Second: when the rupee gets stronger again, do food prices come back down? The second part is important because people often say prices go up like a rocket and come down like a feather.

**Slide 4 — Dependent and independent variables**

These are our variables. The dependent variable — the thing we are explaining — is Food Prices, Pakistan's national food price index from the Pakistan Bureau of Statistics. We have three independent variables, the possible causes. X1 is the Dollar Rate — how many rupees you need to buy one dollar; a higher number means a weaker rupee. X2 is World Food Prices, the FAO index of world prices of wheat, oil, sugar, dairy and meat. X3 is Fuel and Transport Costs — the transport price index, which is mostly petrol and diesel.

**Slide 5 — 132 months · 4 official sources**

Our data is monthly, from January 2015 to December 2025 — that is 132 months, with no missing values. Every variable comes from an official source: the Pakistan Bureau of Statistics, the World Bank and the FAO. We combined all of them month by month into one Excel sheet, which we have submitted. It shows every value and where it came from.

**Slide 6 — One equation**

This is the one equation of our project. Food prices on the left. On the right, the three causes, each with a beta. The beta tells us how strongly that cause moves food prices. We use logarithms, so each beta is an elasticity — a percentage effect. For example, if beta-one is 0.5, then a 10 percent weaker rupee means about 5 percent more expensive food.

**Slide 7 — H₀ (no effect) vs H₁ (effect)**

These are our five hypotheses. In each one, H-zero says there is no effect, and H-one says there is an effect. H1 is about the dollar rate, H2 world food prices, H3 fuel costs. H4 asks whether these variables are tied together in the long run. H5 asks whether a falling rupee and a rising rupee have the same effect. Our rule is simple: if the p-value is below 0.05, we reject H-zero. Now my teammate will show the data and the tests.

## Member 2

**Slide 8 — The data and the tests**

One sentence: “I will now take you through the data and the tests.”

**Slide 9 — All four variables, January 2015 = 100**

Thank you. I'll start with the data itself. This graph sets all four variables to 100 in January 2015 so we can compare them. Food prices — red — end at about 294. The dollar rate — yellow — ends at about 278. They climb together, especially in 2019 and in 2022–23. World food prices — green — end at only about 123. Just by looking, food prices follow the rupee, not the world.

**Slide 10 — Summary of the data (N = 132)**

These are the descriptive statistics. For each variable: the average, the middle value, how spread out it is, and the lowest and highest values. The key column is the last one. Food prices grew about 10.4 percent every year on average, the dollar rate about 9.8 percent, but world food prices only about 1.9 percent.

**Slide 11 — Which variables move together?**

The correlation matrix shows how closely each pair of variables moves together, from minus one to plus one. Food prices and the dollar rate have a correlation of 0.98 — almost perfect. But correlation is not enough: two things that both rise over time will always look correlated. That is why we need the proper tests that come next.

**Slide 12 — Do the variables trend over time?**

Test one is the ADF unit root test. It checks whether a variable has a stable average or keeps trending upward. H-zero says it is not stationary. In levels, all p-values are above 0.05, so the variables trend. After we take the monthly change, all p-values are below 0.05, so they become stationary. We call this I(1). This matters because ordinary regression on trending data can give fake results. The ARDL method we use is designed exactly for I(1) data.

**Slide 13 — Are the variables tied together in the long run?**

Test two is the ARDL Bounds Test. It answers H4: are the variables tied together in the long run? H-zero says no. Our F statistic is 7.54. The critical value at 5 percent is 4.35. Our F is bigger, so we reject H-zero: there is a long-run relationship. Then the error correction term is -0.12. It is negative and significant, which means when food prices move away from the long-run path, about 12 percent of the gap closes every month — half the gap is gone in about 5.4 months. Now my teammate will present the results.

## Member 3

**Slide 14 — The results and the conclusion**

One sentence: “I will now take you through the results and the conclusion.”

**Slide 15 — The estimated equation**

Thank you. Here is our main result — the estimated equation. The numbers replace the betas. For the dollar rate the number is 0.64: if the dollar rate rises 10 percent, food prices rise about 6.3 percent in the long run. For world food prices it is 0.61: a 10 percent rise means about 5.9 percent higher food prices. Fuel and transport costs have 0.21, but its p-value is 0.36, so we cannot say it is different from zero.

**Slide 16 — Decision for every hypothesis**

This table gives the decision for every hypothesis. H1, dollar rate: p is 0.004, below 0.05, so we reject H-zero — a weaker rupee does raise food prices. H2, world food prices: p is 0.002, reject H-zero. H3, fuel costs: p is 0.36, above 0.05, so we fail to reject H-zero — no clear effect. H4: the bounds test rejected H-zero, so there is a long-run relationship. H5 has two answers: in the short run the effects are different, but in the long run we cannot tell.

**Slide 17 — When the rupee falls vs when it recovers**

This is the second part of our question: does food become cheaper when the rupee recovers? We split the rupee into 'falling' and 'rising' months. When the rupee falls 1 percent, food prices end up about 0.53 percent higher, and this is significant. But in the month the rupee gets stronger, food prices do not fall — they actually still go up a little. The Wald test confirms the short-run effects are different, p = 0.023. In the long run the p-value is 0.49, so we cannot prove a difference — there were too few months of a strong rupee. Simple message: prices go up fast, and do not come down quickly.

**Slide 18 — Can we trust the model?**

Before trusting the result we checked the model. Serial correlation — Breusch-Godfrey — passed. Heteroskedasticity — Breusch-Pagan — passed. The functional form — Ramsey RESET — passed. Stability — CUSUM — the line stays inside the bands, so the relationship was stable from 2015 to 2025. Only normality, Jarque-Bera, failed, because of a few extreme months like May 2024. With 128 months this does not change our conclusions.

**Slide 19 — What we found**

To conclude. One: a weaker rupee raises food prices — this is our strongest finding. Two: world food prices matter too, but the rupee matters more for Pakistan. Three: fuel costs had no clear effect in our model. Four: when the rupee recovers, food prices do not come back down quickly. For policy: keep the rupee stable, support poor families directly instead of waiting for the rupee to recover, and diversify food imports. A limit: our model shows strong links, not proof of cause. Thank you — we are happy to take questions.

**Slide 20 — A currency can recover in a season.**

Close here and invite questions. All three members stand together for the Q&A.
