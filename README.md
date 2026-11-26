# The Price of a Falling Rupee

**Does a weaker rupee make food more expensive in Pakistan? (Monthly data, January 2015 – December 2025)**

Website: **https://the-price-of-a-falling-rupee.vercel.app**

## The project in one screen

**Research question.** Does a weaker rupee, along with world food prices and fuel costs, raise food inflation in Pakistan — and does a
stronger rupee bring it down?

**Variables (all monthly % changes; X's from the previous month).**
- Dependent (Y): **Food Inflation** — PBS national food price index
- Independent: **Rupee Depreciation** (X₁, World Bank) · **World Food Inflation** (X₂, FAO) · **Fuel & Transport Inflation** (X₃, PBS) · **Last Month's Food Inflation** (X₄, autoregressive term)

**Equation.** Food Inflation = β₀ + β₁ Rupee Depreciation + β₂ World Food Inflation + β₃ Fuel & Transport Inflation + β₄ Last Month's Food Inflation + error

**Estimated (OLS, N = 132).** Food Inflation = 0.50 + 0.27 Rupee Depreciation + 0.12 World Food Inflation − 0.05 Fuel & Transport Inflation + 0.18 Last Month's Food Inflation
R² = 0.101 · F = 3.56 (p = 0.009)

| # | H₀ | Result | Decision |
|---|---|---|---|
| H1 | Rupee depreciation has no effect (β₁ = 0). | β₁ = 0.266, t = 2.75, p = 0.007 | Reject H₀ |
| H2 | World food inflation has no effect (β₂ = 0). | β₂ = 0.124, t = 1.56, p = 0.122 | Fail to reject H₀ |
| H3 | Fuel & transport inflation has no effect (β₃ = 0). | β₃ = -0.054, t = -0.79, p = 0.428 | Fail to reject H₀ |
| H4 | Last month's food inflation has no effect (β₄ = 0). | β₄ = 0.183, t = 2.08, p = 0.040 | Reject H₀ |
| H5 | All slopes are zero (β₁ = β₂ = β₃ = β₄ = 0). | F(4, 127) = 3.56, p = 0.009 | Reject H₀ |
| H6 | Depreciation and appreciation have the same effect. | Falling rupee 0.33 (p = 0.004); rising rupee -0.00 (p = 0.988); F = 1.35, p = 0.247 | Fail to reject H₀ |

**Tests run.** Descriptive statistics · correlation · stationarity (ADF) · multicollinearity (VIF) · OLS regression (t-tests, F-test, R²) ·
autocorrelation (Durbin-Watson, Breusch-Godfrey) · heteroskedasticity (Breusch-Pagan, White) · normality (Jarque-Bera) ·
specification (Ramsey RESET) · asymmetry (Wald F-test). All diagnostic tests pass.

## Deliverables

| File | What it is |
|---|---|
| `deliverables/Falling_Rupee_Dataset.xlsx` | **All variables combined in one sheet**, with sources, the regression data (monthly % changes) and summary statistics |
| `presentation/The_Price_of_a_Falling_Rupee_Deck.pptx` (+ PDF) | 21 slides split across three members, speaker script in the notes |
| `deliverables/Team_Script_and_Viva_Guide.docx` | Team plan, word-for-word script and viva guide in one document |
| `docs/TEAM_PLAN.md` · `docs/PRESENTATION_SCRIPT.md` · `docs/VIVA_GUIDE.md` | The same, as separate pages |
| `report/The_Price_of_a_Falling_Rupee_Report.docx` (+ PDF) | Short project report (8 pages) |

## Team split

| Member | Slides | Part |
|---|---|---|
| Member 1 | 1–7 | Problem, research question, variables, data, equation, hypotheses |
| Member 2 | 8–13 | Graphs, descriptive statistics, correlation, stationarity (ADF), multicollinearity (VIF) |
| Member 3 | 14–21 | Regression output, hypothesis decisions, autocorrelation, heteroskedasticity, normality, RESET, asymmetry, conclusion |

## Data sources

Pakistan Bureau of Statistics (food and transport price indices) · World Bank Global Economic Monitor (PKR per USD) · FAO Food Price Index ·
IMF CPI dataset (PBS series, via DBnomics). Raw files are in `data/raw/`; their download links and checksums are in `data/metadata/download_log.csv`.

## Rebuild everything

```bash
pip install -r requirements.txt
```

```bash
python scripts/01_fetch_data.py && python scripts/02_build_dataset.py && python scripts/03_estimate.py
```

```bash
python scripts/04_figures.py && python scripts/05_build_registry.py && python scripts/14_simple_regression.py && python scripts/13_build_simple_results.py
```

```bash
python scripts/12_build_dataset_excel.py && python scripts/10_build_deck.py && python scripts/11_build_docs.py && python scripts/09_build_report.py
```

Website: `npm install` then `npm run dev`. `eviews/simple_regression.prg` re-runs the regression and every test in EViews; the 'Regression Data' sheet of the Excel file re-runs it in Excel (Data ▸ Data Analysis ▸ Regression).
