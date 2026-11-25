# The Price of a Falling Rupee

**An econometric investigation of exchange-rate depreciation, international food prices and food inflation in Pakistan (January 2015 – December 2025).**

Live interactive documentary: **https://the-price-of-a-falling-rupee.vercel.app**

> **Verification status.** Every estimate in this repository was computed in Python (`statsmodels` 0.15, `arch` 9) by
> `scripts/03_estimate.py`. EViews was not available in the build environment. The EViews programs in `/eviews` reproduce every
> specification term by term; results stay labelled **"Python estimate · EViews pending"** on the website, in the report and in
> `data/research/manifest.json` until `scripts/07_compare_eviews.py` confirms them against EViews output.

## Research question

To what extent do exchange-rate depreciation, international food commodity prices and domestic energy costs explain food inflation in
Pakistan, and does depreciation have a stronger or more persistent impact on food prices than appreciation?

## Headline results

See [`docs/EXECUTIVE_SUMMARY.md`](docs/EXECUTIVE_SUMMARY.md). In brief: a linear ARDL finds a long-run relationship (both PSS bounds
tests reject) with a long-run exchange-rate elasticity of about 0.64 and a world-food-price elasticity of about 0.61. A nonlinear ARDL finds
a significant long-run depreciation effect (≈ 0.53) but no statistically detectable appreciation effect; impact symmetry is rejected, long-run
symmetry is not. These are conditional associations, not causal estimates.

## Repository map

| Path | Contents |
|---|---|
| `data/raw/` | Untouched source files (IMF via DBnomics, World Bank GEM & Pink Sheet, FAO, PBS monthly reviews) |
| `data/metadata/` | `download_log.csv` (URL, UTC time, SHA-256), `validation_report.json`, `data_dictionary.md` |
| `data/processed/` | `estimation_sample.csv` / `.xlsx` (2015M01–2025M12, N = 132) and the full 2008M07–2025M12 panel |
| `data/research/` | **Results registry** read by the website: typed JSON with verification status (`manifest.json` lists all files) |
| `research/outputs/` | Raw estimation output (JSON) and report figures (`figures/*.png`) |
| `research/sources/` | `source_register.md` |
| `research/eviews_verification.json` | EViews ↔ Python comparison record (empty until EViews has been run) |
| `scripts/` | The reproducible pipeline (below) |
| `eviews/` | EViews 10+ programs (`00_master.prg` …) and `EVIEWS_EXECUTION_GUIDE.md` |
| `report/` | Academic report (DOCX and PDF) |
| `presentation/` | Slide deck (PPTX and PDF) with speaker notes |
| `docs/` | Executive summary, methodology summary, viva preparation |
| `app/`, `components/`, `lib/` | The Next.js website |

## Reproduce everything

Python 3.11+ (versions used are pinned in `requirements.txt`):

```bash
pip install -r requirements.txt
```

```bash
python scripts/01_fetch_data.py        # download raw data (skips files already present; --force to re-download)
python scripts/02_build_dataset.py     # build + validate the dataset (fails loudly if any check fails)
python scripts/03_estimate.py          # all tests and models (~2.5 min)
python scripts/04_figures.py           # report figures
python scripts/05_build_registry.py    # website results registry, data dictionary, source register
python scripts/06_write_eviews.py      # regenerate EViews programs from the estimated specifications
python scripts/09_build_report.py      # academic report (DOCX)
python scripts/10_build_deck.py        # slide deck (PPTX)
python scripts/11_build_docs.py        # executive summary, methodology summary, viva preparation
```

PDF versions:

```bash
soffice --headless --convert-to pdf report/The_Price_of_a_Falling_Rupee_Report.docx --outdir report
```

```bash
soffice --headless --convert-to pdf presentation/The_Price_of_a_Falling_Rupee_Deck.pptx --outdir presentation
```

### EViews verification

1. Open `eviews/00_master.prg` in EViews 10+ and run it (see `eviews/EVIEWS_EXECUTION_GUIDE.md`).
2. `python scripts/07_compare_eviews.py` — compares EViews coefficient tables in `eviews/output/` with the Python fits (relative tolerance 1e-4).
3. `python scripts/05_build_registry.py` — models that match are marked `verified`; commit and push to redeploy the site.

## Website

Next.js 16 (App Router, static), React 19, TypeScript, Tailwind CSS 4, Apache ECharts 6, GSAP, Framer Motion, KaTeX, Lucide.

```bash
npm install
```

```bash
npm run dev
```

`npm run build` first runs `scripts/validate-registry.mjs`, which refuses to build if any registry file is missing, carries an unknown
status, or contains a non-finite headline statistic. All numbers on the site are read from `data/research/*.json` through
`lib/registry.ts`; no coefficient is typed into a component.

Ten chapters: Opening · Problem · Transmission mechanism (interactive) · Data room (explorer) · Exploratory analysis · Econometric engine ·
Asymmetry investigation (interactive multipliers) · Credibility lab (diagnostics, robustness) · Findings · Conclusion (bibliography,
source register, methodology appendix). Press **p** for presentation mode, **← →** to move between chapters, **1–0** to jump.

Deployed on Vercel (project `the-price-of-a-falling-rupee`), building from this repository.

## Data sources

Pakistan Bureau of Statistics (Monthly Review on Price Indices, Table 1, base 2015-16) · IMF Consumer Price Index and International
Financial Statistics datasets (via DBnomics) · World Bank Global Economic Monitor (DPANUSSPB) and Commodity Markets Pink Sheet · FAO Food
Price Index. Full provenance: `research/sources/source_register.md`.

## Known limitations

- Observational time-series evidence; no causal identification is claimed.
- Pre-July-2019 food CPI is the IMF's back-linked series of the previous CPI (tested with a step dummy and a post-2019 sub-sample).
- Few, small appreciation episodes make the appreciation coefficient imprecise.
- NARDL: PSS F-test supports cointegration, t-test does not; CUSUM of squares indicates changing residual variance.
- The State Bank of Pakistan portal refused automated access, so the policy rate is not included; broad money ends in 2025M04.
- Documentary photography could not be retrieved (Wikimedia Commons rate-limited the build environment); `data/research/photos.json` is the hook for adding licensed images with attribution.
- EViews confirmation pending (see top of this file).
