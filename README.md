# The Price of a Falling Rupee

**Does a weaker rupee make food more expensive in Pakistan? (Monthly data, January 2015 – December 2025)**

Website: **https://the-price-of-a-falling-rupee.vercel.app**

## The project in one screen

**Research question.** Do a weaker rupee, world food prices and fuel costs raise food prices in Pakistan — and do food prices fall back
when the rupee gets stronger?

**Variables.**
- Dependent (Y): **Food Prices** — PBS national food price index
- Independent: **Dollar Rate** (X₁, World Bank) · **World Food Prices** (X₂, FAO) · **Fuel & Transport Costs** (X₃, PBS transport index)

**Equation.** Food Prices = β₀ + β₁ Dollar Rate + β₂ World Food Prices + β₃ Fuel & Transport Costs + error

**Estimated (long run, ARDL).** Food Prices = −2.22 + 0.64 Dollar Rate + 0.61 World Food Prices + 0.21 Fuel & Transport Costs

| # | H₀ | Result | Decision |
|---|---|---|---|
| H1 | Dollar rate has no effect | β₁ = 0.64, p = 0.004 | Reject H₀ |
| H2 | World food prices have no effect | β₂ = 0.61, p = 0.002 | Reject H₀ |
| H3 | Fuel & transport costs have no effect | β₃ = 0.21, p = 0.359 | Fail to reject H₀ |
| H4 | No long-run relationship (bounds test) | F = 7.54 > 4.35 | Reject H₀ |
| H5 | Falling and rising rupee have the same effect (Wald) | short run p = 0.023; long run p = 0.495 | Reject (short run) · Fail to reject (long run) |

**Tests run.** Descriptive statistics · correlation matrix · ADF unit root · ARDL bounds test · error correction · Wald (asymmetry) ·
Breusch-Godfrey · Breusch-Pagan-Godfrey · Jarque-Bera · Ramsey RESET · CUSUM / CUSUM of squares.

## Deliverables

| File | What it is |
|---|---|
| `deliverables/Falling_Rupee_Dataset.xlsx` | **All variables combined in one sheet**, with sources, model variables and summary statistics |
| `presentation/The_Price_of_a_Falling_Rupee_Deck.pptx` (+ PDF) | 20 slides split across three members, speaker script in the notes |
| `deliverables/Team_Script_and_Viva_Guide.docx` | Team plan, word-for-word script and viva guide in one document |
| `docs/TEAM_PLAN.md` · `docs/PRESENTATION_SCRIPT.md` · `docs/VIVA_GUIDE.md` | The same, as separate pages |
| `report/The_Price_of_a_Falling_Rupee_Report.docx` (+ PDF) | Short project report (8 pages) |

## Team split

| Member | Slides | Part |
|---|---|---|
| Member 1 | 1–7 | Problem, research question, variables, data, equation, hypotheses |
| Member 2 | 8–13 | Graphs, descriptive statistics, correlation, ADF test, bounds test & ECM |
| Member 3 | 14–20 | Estimated equation, hypothesis decisions, asymmetry, diagnostics, conclusion |

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
python scripts/04_figures.py && python scripts/05_build_registry.py && python scripts/13_build_simple_results.py
```

```bash
python scripts/12_build_dataset_excel.py && python scripts/10_build_deck.py && python scripts/11_build_docs.py && python scripts/09_build_report.py
```

Website: `npm install` then `npm run dev`. The `eviews/` folder contains EViews programs that re-estimate the same models.
