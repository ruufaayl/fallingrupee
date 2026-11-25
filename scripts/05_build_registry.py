"""
05_build_registry.py — assemble the website's results registry in data/research/.

The website never contains a hand-typed coefficient: every number it shows is read from these files,
which are generated from research/outputs/*.json (Python estimates) and, once available,
research/eviews_verification.json (EViews confirmation written by scripts/06_compare_eviews.py).

Status vocabulary (see data/research/manifest.json):
  verified                        – reproduced in EViews within tolerance
  computed_python_pending_eviews  – computed reproducibly in Python; EViews confirmation outstanding
  not_available                   – could not be computed / data not obtainable
  not_applicable                  – test does not apply to the selected specification
Run: python scripts/05_build_registry.py
"""
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research" / "outputs"
REG = ROOT / "data" / "research"
META = ROOT / "data" / "metadata"
REG.mkdir(parents=True, exist_ok=True)
NOW = datetime.now(timezone.utc).isoformat(timespec="seconds")


def load(n):
    return json.loads((OUT / f"{n}.json").read_text())


def write(name, obj):
    (REG / f"{name}.json").write_text(json.dumps(obj, indent=2, ensure_ascii=False))
    print("  data/research/" + name + ".json")


# ------------------------------------------------------------------ verification state
VER_FILE = ROOT / "research" / "eviews_verification.json"
ver = json.loads(VER_FILE.read_text()) if VER_FILE.exists() else {"models": {}}


def status_for(model_id: str) -> str:
    m = ver.get("models", {}).get(model_id)
    return "verified" if m and m.get("all_within_tolerance") else "computed_python_pending_eviews"


# ------------------------------------------------------------------ variables & sources
log = {}
for line in (META / "download_log.csv").read_text().splitlines()[1:]:
    parts = line.split(",")
    log[parts[0]] = {"downloaded_utc": parts[-3], "sha256": parts[-1]}

SOURCES = [
    {"id": "PBS_CPI", "institution": "Pakistan Bureau of Statistics (PBS)",
     "title": "Monthly Review on Price Indices, Table 1: Consumer Price Index (National) by Group (base 2015-16)",
     "url": "https://www.pbs.gov.pk/price-statistics/", "used_for": "Food, headline, transport and housing CPI, 2025M08–2025M12; overlap validation 2024M07–2025M07",
     "files": [k for k in log if k.startswith("pbs_cpi_reviews/")]},
    {"id": "IMF_CPI", "institution": "International Monetary Fund — Consumer Price Index dataset (accessed via DBnomics mirror)",
     "title": "Pakistan, monthly CPI by COICOP group: PCPIF_IX (food & non-alcoholic beverages), PCPI_IX, PCPIT_IX, PCPIH_IX",
     "url": "https://db.nomics.world/IMF/CPI", "used_for": "Food, headline, transport and housing CPI, 2008M07–2025M07",
     "files": [k for k in log if k.startswith("imf_cpi")]},
    {"id": "IMF_IFS", "institution": "International Monetary Fund — International Financial Statistics (via DBnomics)",
     "title": "Pakistan: ENDA_XDC_USD_RATE (period average), ENDE_XDC_USD_RATE (end of period), FMB_XDC (broad money)",
     "url": "https://db.nomics.world/IMF/IFS", "used_for": "Cross-check of the exchange rate; end-of-period rate; broad money (coverage ends 2025M04, not used)",
     "files": [k for k in log if k.startswith("imf_ifs")]},
    {"id": "WB_GEM", "institution": "World Bank — Global Economic Monitor (data source 15)",
     "title": "Pakistan: DPANUSSPB, official exchange rate, LCU per USD, period average",
     "url": "https://api.worldbank.org/v2/sources/15/country/PAK/series/DPANUSSPB", "used_for": "EXR, 2015M01–2025M12",
     "files": [k for k in log if k.startswith("wb_gem")]},
    {"id": "FAO_FFPI", "institution": "Food and Agriculture Organization of the United Nations (FAO)",
     "title": "FAO Food Price Index, nominal, 2014–2016 = 100", "url": "https://www.fao.org/worldfoodsituation/foodpricesindex/en/",
     "used_for": "GFOOD", "files": [k for k in log if k.startswith("fao")]},
    {"id": "WB_PINK", "institution": "World Bank — Commodity Markets (Pink Sheet)",
     "title": "CMO Historical Data Monthly: food price index (2010 = 100) and Brent crude (USD/bbl)",
     "url": "https://www.worldbank.org/en/research/commodity-markets", "used_for": "GFOOD_WB and BRENT (robustness)",
     "files": [k for k in log if k.startswith("wb_cmo")]},
]
for s in SOURCES:
    s["downloads"] = [{"file": f, **log[f]} for f in s["files"]]

VARIABLES = [
    {"code": "FOODCPI", "log_code": "LFOODCPI", "role": "Dependent variable", "name": "Food CPI (National)",
     "definition": "National Consumer Price Index, group 1 'Food & non-alcoholic beverages' (weight 34.58%)",
     "unit": "Index, 2015-16 = 100", "source": ["IMF_CPI", "PBS_CPI"],
     "series_id": "IMF CPI M.PK.PCPIF_IX (2008M07–2025M07); PBS Table 1 (2025M08–2025M12)",
     "transform": "Natural log. Monthly and year-on-year % changes for description.",
     "rebasing": ("From 2019M07 the series is PBS's 2015-16-base national CPI (identical to PBS Table 1, verified to "
                  "±0.003 index points). Earlier months are the IMF's back-linked series, which chains the previous "
                  "(2007-08-base) CPI onto the new base; its FY2015-16 average is 101.6 rather than 100. The linkage is "
                  "documented and tested with a 2019M07 step dummy and a post-2019M07 sub-sample.")},
    {"code": "EXR", "log_code": "LEXR", "role": "Key regressor", "name": "Exchange rate, PKR per USD",
     "definition": "Official exchange rate, Pakistani rupees per US dollar, monthly period average",
     "unit": "PKR per USD", "source": ["WB_GEM", "IMF_IFS"], "series_id": "World Bank GEM DPANUSSPB",
     "transform": "Natural log; a rise is a DEPRECIATION of the rupee.",
     "rebasing": "None. Cross-checked against IMF IFS ENDA_XDC_USD_RATE (2015M01–2025M06): correlation 0.99997."},
    {"code": "LEXR_POS", "log_code": "LEXR_POS", "role": "NARDL regressor", "name": "Cumulative depreciation (EXR⁺)",
     "definition": "Partial sum of positive monthly changes in ln(EXR) since 2015M01", "unit": "Log points",
     "source": ["WB_GEM"], "series_id": "Derived", "transform": "Σ max(Δln EXR, 0)", "rebasing": "—"},
    {"code": "LEXR_NEG", "log_code": "LEXR_NEG", "role": "NARDL regressor", "name": "Cumulative appreciation (EXR⁻)",
     "definition": "Partial sum of negative monthly changes in ln(EXR) since 2015M01 (≤ 0)", "unit": "Log points",
     "source": ["WB_GEM"], "series_id": "Derived", "transform": "Σ min(Δln EXR, 0)", "rebasing": "—"},
    {"code": "GFOOD", "log_code": "LGFOOD", "role": "Key regressor", "name": "International food prices",
     "definition": "FAO Food Price Index (nominal, US dollar based)", "unit": "Index, 2014–2016 = 100",
     "source": ["FAO_FFPI"], "series_id": "FAO FFPI, column 'Food Price Index'", "transform": "Natural log",
     "rebasing": "None"},
    {"code": "TRANSCPI", "log_code": "LTRANSCPI", "role": "Key regressor (energy proxy)",
     "name": "Domestic energy cost: Transport CPI",
     "definition": ("National CPI group 7 'Transport' (weight 5.91%), dominated by motor fuel; captures domestic petrol/"
                    "diesel prices and freight-related fares that feed food distribution costs"),
     "unit": "Index, 2015-16 = 100", "source": ["IMF_CPI", "PBS_CPI"],
     "series_id": "IMF CPI M.PK.PCPIT_IX; PBS Table 1", "transform": "Natural log", "rebasing": "As FOODCPI"},
    {"code": "HOUSCPI", "log_code": "LHOUSCPI", "role": "Robustness (energy)",
     "name": "Housing, water, electricity, gas & fuels CPI", "definition": "National CPI group 4 (weight 23.63%)",
     "unit": "Index, 2015-16 = 100", "source": ["IMF_CPI", "PBS_CPI"], "series_id": "IMF CPI M.PK.PCPIH_IX; PBS Table 1",
     "transform": "Natural log", "rebasing": "As FOODCPI"},
    {"code": "BRENT", "log_code": "LBRENT", "role": "Robustness (energy)", "name": "Brent crude oil price",
     "definition": "Crude oil, Brent, US dollars per barrel", "unit": "USD/bbl", "source": ["WB_PINK"],
     "series_id": "Pink Sheet 'CRUDE_BRENT'", "transform": "Natural log", "rebasing": "None"},
    {"code": "GFOOD_WB", "log_code": "LGFOOD_WB", "role": "Robustness (global food)", "name": "World Bank food price index",
     "definition": "Pink Sheet food price index, nominal US dollars", "unit": "Index, 2010 = 100", "source": ["WB_PINK"],
     "series_id": "Pink Sheet 'Monthly Indices' — Food", "transform": "Natural log", "rebasing": "None"},
    {"code": "CPI", "log_code": "LCPI", "role": "Context / extension", "name": "Headline CPI (National)",
     "definition": "National CPI, general index", "unit": "Index, 2015-16 = 100", "source": ["IMF_CPI", "PBS_CPI"],
     "series_id": "IMF CPI M.PK.PCPI_IX; PBS Table 1", "transform": "Natural log", "rebasing": "As FOODCPI"},
]

CONSIDERED = [
    {"variable": "Policy interest rate", "decision": "Excluded",
     "reason": "SBP's statistics portal refused automated access (HTTP 403) and the IMF IFS policy-rate series is not in the mirror; monetary policy works mainly through the exchange rate and demand, whose effect on food prices is partly captured by EXR."},
    {"variable": "Broad money (M2)", "decision": "Excluded",
     "reason": "IMF IFS FMB_XDC ends in 2025M04 (8 missing months); adding it would shorten the common sample."},
    {"variable": "International oil price", "decision": "Robustness only",
     "reason": "Brent (USD) substitutes for the domestic energy proxy in a robustness model."},
    {"variable": "Import prices / agricultural output / rainfall", "decision": "Excluded",
     "reason": "No consistent monthly official series for 2015–2025 was obtainable; event dummies for the 2022 floods are tested instead."},
]

write("variables", {"variables": VARIABLES, "considered_but_excluded": CONSIDERED})
write("sources", {"sources": SOURCES})

# ------------------------------------------------------------------ copy core outputs, tagging status
copies = {"descriptive_statistics": None, "correlations": None, "stationarity": None, "ols_results": "OLS_LEVELS",
          "ardl_results": "ARDL_MAIN", "nardl_results": "NARDL_MAIN", "wald_tests": "NARDL_MAIN",
          "robustness": "ROBUSTNESS", "multipliers": "NARDL_MAIN", "timeseries": None}
for name, mid in copies.items():
    obj = load(name)
    obj["_meta"]["status"] = status_for(mid) if mid else (
        "verified" if ver.get("models", {}).get(name, {}).get("all_within_tolerance") else "computed_python_pending_eviews")
    write(name, obj)

ardl, nardl = load("ardl_results"), load("nardl_results")
write("bounds_test", {"ARDL_MAIN": {**ardl["bounds_test"], "status": status_for("ARDL_MAIN")},
                      "NARDL_MAIN": {**nardl["bounds_test"], "status": status_for("NARDL_MAIN")}})
write("ecm_results", {"ARDL_MAIN": {**ardl["ecm_regression"], "status": status_for("ARDL_MAIN")},
                      "NARDL_MAIN": {**nardl["ecm_regression"], "status": status_for("NARDL_MAIN")}})
write("diagnostics", {m: {"tests": load(f)["diagnostics"], "stability": load(f).get("stability"),
                          "status": status_for(m)}
                      for m, f in (("OLS_LEVELS", "ols_results"), ("ARDL_MAIN", "ardl_results"),
                                   ("NARDL_MAIN", "nardl_results"))
                      if "diagnostics" in load(f)})

# ------------------------------------------------------------------ findings derived from numbers
lr = {x["variable"]: x for x in nardl["long_run"]}
lra = {x["variable"]: x for x in ardl["long_run"]}
asym = nardl["asymmetry"]
rob = load("robustness")["nardl_specifications"]
rob_ok = [r for r in rob if "long_run" in r and r["id"] != "HEADLINE"]  # HEADLINE has a different dependent variable
n_pos_sig = sum(r["long_run"]["LEXR_POS"]["p"] < 0.05 for r in rob_ok)
n_pos_positive = sum(r["long_run"]["LEXR_POS"]["coef"] > 0 for r in rob_ok)
n_neg_sig = sum(r["long_run"]["LEXR_NEG"]["p"] < 0.05 for r in rob_ok)
n_lr_rej = sum((r.get("lr_sym_p") or 1) < 0.05 for r in rob_ok)
lr_rej_ids = ", ".join(r["label"] for r in rob_ok if (r.get("lr_sym_p") or 1) < 0.05) or "none"
n_imp_rej = sum((r.get("impact_sym_p") or 1) < 0.05 for r in rob_ok)
desc = {v["variable"]: v for v in load("descriptive_statistics")["variables"]}
ba, bn = ardl["bounds_test"], nardl["bounds_test"]
mult = load("multipliers")

findings = {
    "headline_numbers": {
        "food_cpi_change_pct": desc["FOODCPI"]["total_change_pct"], "exr_change_pct": desc["EXR"]["total_change_pct"],
        "gfood_change_pct": desc["GFOOD"]["total_change_pct"], "food_infl_peak": desc["FOOD_INF_YOY"]["max"],
        "food_infl_peak_date": desc["FOOD_INF_YOY"]["max_date"], "food_cagr_pct": desc["FOODCPI"]["cagr_pct"],
        "exr_peak": desc["EXR"]["max"], "exr_peak_date": desc["EXR"]["max_date"], "nobs": 132,
    },
    "answers": [
        {"q": "Is there evidence of a long-run relationship?", "model": "ARDL_MAIN / NARDL_MAIN",
         "answer": (f"Yes in the linear ARDL: F = {ba['F']:.2f} exceeds the 5% I(1) bound ({ba['asymptotic']['5%']['F_I1']}) "
                    f"and t = {ba['t']:.2f} lies below its I(1) bound ({ba['asymptotic']['5%']['t_I1']}). In the NARDL, the F-test "
                    f"rejects (F = {bn['F']:.2f}) but the t-test does not (t = {bn['t']:.2f} vs {bn['asymptotic']['5%']['t_I1']}), so the "
                    "asymmetric long-run relationship is supported by one of the two PSS tests only."),
         "strength": "strong (ARDL) / partial (NARDL)"},
        {"q": "Does depreciation affect food CPI?", "model": "NARDL_MAIN",
         "answer": (f"Yes. A permanent 1% depreciation is associated with a {lr['LEXR_POS']['coef']:.2f}% higher food CPI in the "
                    f"long run (p = {lr['LEXR_POS']['p']:.3f}; 95% CI {lr['LEXR_POS']['ci95_low']:.2f} to {lr['LEXR_POS']['ci95_high']:.2f}). "
                    f"The linear ARDL gives {lra['LEXR']['coef']:.2f} (p = {lra['LEXR']['p']:.3f}). The sign is positive in "
                    f"{n_pos_positive}/{len(rob_ok)} robustness specifications and significant at 5% in {n_pos_sig}."),
         "strength": "robust in sign; significant in most specifications"},
        {"q": "Does appreciation have an equivalent opposite effect?", "model": "NARDL_MAIN",
         "answer": (f"Not demonstrably. The long-run appreciation coefficient ({lr['LEXR_NEG']['coef']:.2f}, p = {lr['LEXR_NEG']['p']:.2f}) "
                    f"is statistically indistinguishable from zero and is significant in {n_neg_sig} of {len(rob_ok)} specifications. "
                    f"Long-run symmetry is NOT rejected (Wald χ²(1) = {asym['long_run']['wald_chi2']:.2f}, p = {asym['long_run']['p_chi2']:.2f}); "
                    f"it is rejected in {n_lr_rej} of {len(rob_ok)} specifications ({lr_rej_ids}). Short-run (impact) "
                    f"symmetry IS rejected (F = {asym['short_run']['F_impact']:.2f}, p = {asym['short_run']['p_impact']:.3f}; rejected in "
                    f"{n_imp_rej}/{len(rob_ok)} specifications)" + (": in the month the rupee appreciates, food prices do not fall — the "
                    f"point estimate implies they edge up ({-asym['short_run']['beta0_neg']:.2f}% per 1% appreciation) before reversing."
                    if asym['short_run']['beta0_neg'] < 0 else ".")),
         "strength": "short-run asymmetry significant; long-run asymmetry not established"},
        {"q": "Which variables have statistically significant effects?", "model": "ARDL_MAIN / NARDL_MAIN",
         "answer": (f"Long run (ARDL): exchange rate {lra['LEXR']['coef']:.2f} (p = {lra['LEXR']['p']:.3f}) and FAO food prices "
                    f"{lra['LGFOOD']['coef']:.2f} (p = {lra['LGFOOD']['p']:.3f}); transport CPI {lra['LTRANSCPI']['coef']:.2f} is not "
                    f"significant (p = {lra['LTRANSCPI']['p']:.2f}). In the NARDL, transport CPI becomes significant "
                    f"({lr['LTRANSCPI']['coef']:.2f}, p = {lr['LTRANSCPI']['p']:.3f}) and FAO prices are marginal (p = {lr['LGFOOD']['p']:.3f})."),
         "strength": "see coefficient tables"},
        {"q": "Is the estimated model stable?", "model": "ARDL_MAIN / NARDL_MAIN",
         "answer": (f"The linear ARDL passes both CUSUM and CUSUM-of-squares. The NARDL passes CUSUM "
                    f"({'within' if nardl['stability']['cusum_within_bounds'] else 'outside'} bounds) but its CUSUM-of-squares "
                    f"{'stays within' if nardl['stability']['cusumsq_within_bounds'] else 'crosses'} the 5% band "
                    f"(max deviation {nardl['stability']['cusumsq_max_dev']:.3f} vs {nardl['stability']['cusumsq_c0']:.3f}, around "
                    f"{nardl['stability']['cusumsq_max_dev_date']}), signalling a change in residual variance over the sample (consistent with calm 2015–18 and volatile 2022–25 food prices)."),
         "strength": "ARDL stable; NARDL variance instability"},
        {"q": "Are the results robust?", "model": "ROBUSTNESS",
         "answer": (f"The positive depreciation pass-through survives alternative lag rules, energy and global-food proxies, an "
                    f"outlier dummy and sub-samples in sign ({n_pos_positive}/{len(rob_ok)}) and mostly in significance ({n_pos_sig}/{len(rob_ok)}). "
                    "It weakens when a 2019M07 step dummy and other event dummies are added, because the rebasing step absorbs part of the level shift."),
         "strength": "moderately robust"},
    ],
    "speed_of_adjustment": {"ARDL_MAIN": ardl["ecm_regression"]["speed_of_adjustment"],
                            "ARDL_half_life": ardl["ecm_regression"]["half_life_months"],
                            "NARDL_MAIN": nardl["ecm_regression"]["speed_of_adjustment"],
                            "NARDL_half_life": nardl["ecm_regression"]["half_life_months"]},
    "multiplier_snapshots": [{"h": h, "depreciation": mult["pos"][h], "appreciation_response": -mult["neg"][h],
                              "asym": mult["asym"][h], "asym_lo95": mult["asym_lo95"][h], "asym_hi95": mult["asym_hi95"][h]}
                             for h in (0, 1, 3, 6, 12, 24, 36)],
    "robustness_counts": {"n_specs": len(rob_ok), "pos_positive": n_pos_positive, "pos_significant": n_pos_sig,
                          "neg_significant": n_neg_sig, "lr_symmetry_rejected": n_lr_rej, "impact_symmetry_rejected": n_imp_rej},
    "status": status_for("NARDL_MAIN"),
}
write("findings", findings)

# ------------------------------------------------------------------ manifest
files = sorted(p.name for p in REG.glob("*.json") if p.name != "manifest.json")
models = {"OLS_LEVELS": "Static OLS in log levels", "ARDL_MAIN": f"ARDL{tuple(ardl['selection']['chosen_order'])}",
          "NARDL_MAIN": f"NARDL{tuple(nardl['selection']['chosen_order'])}", "ROBUSTNESS": "13 NARDL + 5 ARDL alternatives"}
write("manifest", {
    "project": "The Price of a Falling Rupee",
    "generated_utc": NOW,
    "estimation_sample": {"start": "2015M01", "end": "2025M12", "frequency": "monthly", "nobs": 132},
    "status_legend": {
        "verified": "Reproduced in EViews within tolerance (see research/eviews_verification.json)",
        "computed_python_pending_eviews": "Computed reproducibly in Python (statsmodels); EViews confirmation outstanding",
        "not_available": "Could not be computed or the data could not be obtained",
        "not_applicable": "The test does not apply to the selected specification"},
    "models": [{"model_id": k, "description": v, "status": status_for(k),
                "eviews_program": {"OLS_LEVELS": "eviews/03_ols.prg", "ARDL_MAIN": "eviews/04_ardl.prg",
                                   "NARDL_MAIN": "eviews/05_nardl.prg", "ROBUSTNESS": "eviews/06_robustness.prg"}[k]}
               for k, v in models.items()],
    "files": files,
    "eviews_verification": ver,
})
print("done")

# ------------------------------------------------------------------ human-readable dictionary & source register
dd = ["# Data dictionary", "", f"Generated by `scripts/05_build_registry.py` on {NOW}. Estimation sample 2015M01–2025M12, "
      "monthly, N = 132, no missing observations in any model variable.", "",
      "| Code | Name | Role | Unit | Source / series ID | Transformation | Base-year / comparability notes |",
      "|---|---|---|---|---|---|---|"]
for v in VARIABLES:
    dd.append(f"| `{v['code']}` (`{v['log_code']}`) | {v['name']} | {v['role']} | {v['unit']} | {', '.join(v['source'])}: "
              f"{v['series_id']} | {v['transform']} | {v['rebasing']} |")
dd += ["", "## Derived columns in `data/processed/estimation_sample.csv`", "",
       "| Column | Definition |", "|---|---|",
       "| `L*` | Natural logarithm of the level series |",
       "| `LEXR_POS`, `LEXR_NEG` | Partial sums Σmax(ΔLEXR,0) and Σmin(ΔLEXR,0) from 2015M01 (both start at 0); LEXR = LEXR₀ + POS + NEG exactly |",
       "| `LBRENT_PKR` | ln(Brent USD × PKR/USD) |",
       "| `FOOD_INF_YOY`, `FOOD_INF_MOM`, `CPI_INF_YOY`, `EXR_DEP_YOY`, `GFOOD_YOY`, `TRANS_YOY` | Percentage changes over 12 months / 1 month, computed on the full 2008M07 panel so 2015 values are defined |",
       "| `D_REBASE` | 1 from 2019M07 (first month of PBS's 2015-16-base national CPI) |",
       "| `D_COVID` | 1 in 2020M03–2020M06 |", "| `D_FLOOD` | 1 in 2022M08–2022M10 (monsoon floods) |",
       "| `D_RAMADAN` | 1 in the Gregorian month in which Ramadan begins |",
       "| `SEAS01`–`SEAS11` | Monthly dummies (December is the base month) |", "",
       "## Variables considered but not used", "", "| Variable | Decision | Reason |", "|---|---|---|"]
dd += [f"| {c['variable']} | {c['decision']} | {c['reason']} |" for c in CONSIDERED]
(META / "data_dictionary.md").write_text("\n".join(dd) + "\n")

sr = ["# Source register", "", "Every raw file is stored unmodified in `data/raw/`; its URL, UTC download time and SHA-256 "
      "are in `data/metadata/download_log.csv`.", ""]
for s in SOURCES:
    sr += [f"## {s['id']} — {s['institution']}", "", f"- **Title:** {s['title']}", f"- **URL:** {s['url']}",
           f"- **Used for:** {s['used_for']}", "- **Files:**"]
    sr += [f"  - `data/raw/{d['file']}` — downloaded {d['downloaded_utc']}, sha256 `{d['sha256'][:16]}…`" for d in s["downloads"]]
    sr.append("")
sr += ["## Access notes", "",
       "- The State Bank of Pakistan statistics portal (sbp.org.pk, easydata.sbp.org.pk) returned HTTP 403 to automated "
       "requests during data collection, so the exchange rate was taken from the World Bank GEM and cross-checked against "
       "IMF IFS; the policy rate could not be obtained and is not used.",
       "- IMF series were read from the DBnomics mirror (api.db.nomics.world), which republishes the IMF CPI and IFS "
       "datasets unchanged; the mirror's last IMF update covers data to 2025M07 (CPI) and 2025M06 (IFS).", ""]
(ROOT / "research" / "sources" / "source_register.md").write_text("\n".join(sr))
print("  data/metadata/data_dictionary.md, research/sources/source_register.md")
