"""
02_build_dataset.py — turn the untouched raw files in data/raw/ into the
analysis dataset used by every model, the EViews programs and the website.

Outputs
  data/processed/pakistan_food_inflation_monthly.csv   full aligned panel (2008M07–2025M12 where available)
  data/processed/estimation_sample.csv                  2015M01–2025M12 (N = 132), levels + logs + partial sums
  data/processed/estimation_sample.xlsx                 same, for EViews import (sheet "data")
  data/metadata/validation_report.json                  every cross-source check and its outcome

Every transformation is documented in data/metadata/data_dictionary.md.
Run:  python scripts/02_build_dataset.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
META = ROOT / "data" / "metadata"
SAMPLE_START, SAMPLE_END = "2015-01", "2025-12"

checks: list[dict] = []


def check(name: str, ok: bool, detail: str) -> None:
    checks.append({"check": name, "passed": bool(ok), "detail": detail})
    print(("PASS " if ok else "FAIL ") + name + " — " + detail)
    if not ok:
        raise SystemExit(f"Validation failed: {name}")


# ---------------------------------------------------------------- readers
def read_dbnomics(fname: str) -> pd.Series:
    doc = json.loads((RAW / fname).read_text())["series"]["docs"][0]
    vals = [np.nan if v == "NA" else float(v) for v in doc["value"]]
    return pd.Series(vals, index=pd.PeriodIndex(doc["period"], freq="M")).dropna()


def read_wb_gem(fname: str) -> pd.Series:
    obs = json.loads((RAW / fname).read_text())["source"]["data"]
    out = {}
    for o in obs:
        t = next(v["value"] for v in o["variable"] if v["concept"] == "Time")
        if "M" in t and o["value"] is not None:
            out[pd.Period(t.replace("M", "-"), freq="M")] = float(o["value"])
    return pd.Series(out).sort_index()


def read_fao() -> pd.Series:
    df = pd.read_csv(RAW / "fao_food_price_indices_data.csv", skiprows=2, encoding="utf-8-sig")
    df = df[["Date", "Food Price Index"]].dropna()
    df = df[df["Date"].astype(str).str.match(r"^\d{4}-\d{2}$")]
    return pd.Series(df["Food Price Index"].astype(float).values,
                     index=pd.PeriodIndex(df["Date"], freq="M"))


def read_pink(sheet: str, col_match: str) -> pd.Series:
    raw = pd.read_excel(RAW / "wb_cmo_historical_data_monthly.xlsx", sheet_name=sheet, header=None)
    hdr_row = next(i for i in range(15) if any(isinstance(v, str) and col_match.lower() in v.lower()
                                               for v in raw.iloc[i].values))
    col = next(j for j, v in enumerate(raw.iloc[hdr_row].values)
               if isinstance(v, str) and col_match.lower() in v.lower())
    body = raw.iloc[hdr_row + 1:, [0, col]].dropna()
    body = body[body[0].astype(str).str.match(r"^\d{4}M\d{2}$")]
    idx = pd.PeriodIndex([s.replace("M", "-") for s in body[0].astype(str)], freq="M")
    return pd.Series(pd.to_numeric(body[col], errors="coerce").values, index=idx).dropna()


def pbs_table1(fname: str) -> dict:
    """Return {(group, column_label): value} from PBS Table 1 (CPI National by group)."""
    path = RAW / "pbs_cpi_reviews" / fname
    rows: dict = {}
    if path.suffix == ".docx":
        import docx
        d = docx.Document(str(path))
        t = next(t for t in d.tables if t.rows[0].cells[0].text.strip().startswith("Table 1: Consumer"))
        cols = [c.text.strip() for c in t.rows[2].cells][3:6]
        for r in t.rows[3:]:
            cs = [c.text.strip() for c in r.cells]
            for key, pat in (("general", r"^General"), ("food", r"^Food"),
                             ("housing", r"^Housing"), ("transport", r"^Transport")):
                if re.match(pat, cs[1]):
                    rows[key] = dict(zip(cols, map(float, cs[3:6])))
    else:
        import pdfplumber
        with pdfplumber.open(str(path)) as pdf:
            tx = next(p.extract_text() for p in pdf.pages
                      if "Table 1: Consumer Price Index (National)" in (p.extract_text() or ""))
        lines = tx.splitlines()
        hdr = next(l for l in lines if re.match(r"^(Jan|Feb|Mar|Apr|May|June?|July?|Aug|Sep|Oct|Nov|Dec)\w* \d\d ", l))
        toks = hdr.split()
        cols = [" ".join(toks[i:i + 2]) for i in (0, 2, 4)]
        num = r"([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+)"
        for key, pat in (("general", r"^General " + num), ("food", r"^1\. Food & Non-alcoholic Bev\. " + num),
                         ("housing", r"^4\. " + num), ("transport", r"^7\. Transport " + num)):
            m = next(re.match(pat, l) for l in lines if re.match(pat, l))
            rows[key] = dict(zip(cols, map(float, m.groups()[1:4])))
    return rows


MONTHS = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
          "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}


def label_to_period(lbl: str) -> pd.Period:
    m, y = lbl.split()
    return pd.Period(year=2000 + int(y), month=MONTHS[m.lower()[:3]], freq="M")


# ---------------------------------------------------------------- build
def build() -> None:
    PROC.mkdir(parents=True, exist_ok=True)

    imf = {k: read_dbnomics(f"imf_cpi_PK_{c}.json") for k, c in
           (("food", "PCPIF_IX"), ("general", "PCPI_IX"), ("transport", "PCPIT_IX"), ("housing", "PCPIH_IX"))}

    # PBS reviews: take month m from the review of month m+1 ("previous month" column) so the
    # latest published revision is used (PBS revised Aug–Oct 2025 for an FCA correction).
    reviews = ["Monthly-Review-July-2025.pdf", "Revised-Monthly-Review-August-2025.docx",
               "1.-Monthly-Review-September-2025-Revised.docx", "Monthly-Review-October-2025.docx",
               "Monthly-Review-November-2025.docx", "Monthly-Review-December-2025.docx",
               "Monthly-Review-January-2026-1.pdf"]
    pbs: dict[str, dict[pd.Period, float]] = {k: {} for k in imf}
    for f in reviews:                       # later reviews overwrite earlier ones → latest revision wins
        t = pbs_table1(f)
        for g, cols in t.items():
            for lbl, v in cols.items():
                pbs[g][label_to_period(lbl)] = v

    for g in imf:
        s_pbs = pd.Series(pbs[g]).sort_index()
        overlap = s_pbs.index.intersection(imf[g].index)
        diff = (s_pbs[overlap] - imf[g][overlap]).abs().max()
        check(f"PBS Table 1 vs IMF CPI ({g}) on {len(overlap)} overlapping months",
              diff < 0.06, f"max |diff| = {diff:.3f} index points over {', '.join(str(p) for p in overlap)}")
        ext = s_pbs[s_pbs.index > imf[g].index.max()]
        imf[g] = pd.concat([imf[g], ext]).sort_index()

    exr = read_wb_gem("wb_gem_PAK_DPANUSSPB.json")
    exr_ifs = read_dbnomics("imf_ifs_PK_ENDA_XDC_USD_RATE.json")
    exr_eop = read_dbnomics("imf_ifs_PK_ENDE_XDC_USD_RATE.json")
    ov = exr.index.intersection(exr_ifs.index)
    ov = ov[(ov >= pd.Period(SAMPLE_START)) & (ov <= pd.Period(SAMPLE_END))]
    rel = ((exr[ov] / exr_ifs[ov]) - 1).abs()
    check("World Bank GEM PKR/USD vs IMF IFS period-average (2015M01–2025M06)",
          rel.max() < 0.02 and np.corrcoef(exr[ov], exr_ifs[ov])[0, 1] > 0.999,
          f"max relative gap {rel.max():.4f} ({rel.idxmax()}), corr {np.corrcoef(exr[ov], exr_ifs[ov])[0, 1]:.5f}")

    ffpi = read_fao()
    wbfood = read_pink("Monthly Indices", "Food")
    brent = read_pink("Monthly Prices", "Brent")
    check("FAO FFPI covers the sample", ffpi.index.min() <= pd.Period(SAMPLE_START) and
          ffpi.index.max() >= pd.Period(SAMPLE_END), f"{ffpi.index.min()}–{ffpi.index.max()}")
    check("Pink Sheet covers the sample", wbfood.index.max() >= pd.Period(SAMPLE_END) and
          brent.index.max() >= pd.Period(SAMPLE_END), f"food idx to {wbfood.index.max()}, Brent to {brent.index.max()}")

    panel = pd.DataFrame({
        "FOODCPI": imf["food"], "CPI": imf["general"], "TRANSCPI": imf["transport"],
        "HOUSCPI": imf["housing"], "EXR": exr, "EXR_IFS": exr_ifs, "EXR_EOP": exr_eop,
        "GFOOD": ffpi, "GFOOD_WB": wbfood, "BRENT": brent,
    })
    panel = panel.loc[pd.Period("2008-07"):pd.Period(SAMPLE_END)]
    panel.index.name = "period"
    full = panel.copy()
    full.insert(0, "date", full.index.strftime("%YM%m"))
    full.to_csv(PROC / "pakistan_food_inflation_monthly.csv", index=False, float_format="%.6f")

    s = panel.loc[pd.Period(SAMPLE_START):pd.Period(SAMPLE_END)].copy()
    core = ["FOODCPI", "EXR", "GFOOD", "TRANSCPI"]
    miss = s[core].isna().sum()
    check("No missing observations in core variables", miss.sum() == 0,
          f"N = {len(s)}; missing = {miss.to_dict()}")
    check("Sample length", len(s) == 132, f"{s.index[0]}–{s.index[-1]}, N = {len(s)}")

    # logs (natural) ---------------------------------------------------------
    for v in ["FOODCPI", "CPI", "TRANSCPI", "HOUSCPI", "EXR", "GFOOD", "GFOOD_WB", "BRENT"]:
        s["L" + v] = np.log(s[v])
    s["LBRENT_PKR"] = np.log(s["BRENT"] * s["EXR"])
    # NARDL partial-sum decomposition of ln(EXR), Shin, Yu & Greenwood-Nimmo (2014):
    #   ΔLEXR = ΔLEXR⁺ + ΔLEXR⁻,  LEXR_POS_t = Σ max(ΔLEXR_j, 0),  LEXR_NEG_t = Σ min(ΔLEXR_j, 0)
    # A rise in PKR per USD is a depreciation, so LEXR_POS accumulates depreciation and
    # LEXR_NEG (≤ 0) accumulates appreciation. Both start at 0 in 2015M01.
    d = s["LEXR"].diff().fillna(0.0)
    s["LEXR_POS"] = d.clip(lower=0).cumsum()
    s["LEXR_NEG"] = d.clip(upper=0).cumsum()
    check("Partial sums reconstruct ln(EXR)",
          np.allclose(s["LEXR"].iloc[0] + s["LEXR_POS"] + s["LEXR_NEG"], s["LEXR"]),
          "LEXR_t = LEXR_0 + POS_t + NEG_t holds exactly")

    # inflation rates (%) -----------------------------------------------------
    s["FOOD_INF_YOY"] = (panel["FOODCPI"].pct_change(12, fill_method=None) * 100).loc[s.index]
    s["FOOD_INF_MOM"] = (panel["FOODCPI"].pct_change(fill_method=None) * 100).loc[s.index]
    s["CPI_INF_YOY"] = (panel["CPI"].pct_change(12, fill_method=None) * 100).loc[s.index]
    s["EXR_DEP_YOY"] = (panel["EXR"].pct_change(12, fill_method=None) * 100).loc[s.index]
    s["GFOOD_YOY"] = (panel["GFOOD"].pct_change(12, fill_method=None) * 100).loc[s.index]
    s["TRANS_YOY"] = (panel["TRANSCPI"].pct_change(12, fill_method=None) * 100).loc[s.index]

    # deterministic dummies ---------------------------------------------------
    p = s.index
    s["D_REBASE"] = (p >= pd.Period("2019-07")).astype(int)        # PBS 2015-16 base, new national CPI
    s["D_COVID"] = ((p >= pd.Period("2020-03")) & (p <= pd.Period("2020-06"))).astype(int)
    s["D_FLOOD"] = ((p >= pd.Period("2022-08")) & (p <= pd.Period("2022-10"))).astype(int)
    # Month in which Ramadan begins (Gregorian), from the published Islamic calendar.
    ramadan = {2015: 6, 2016: 6, 2017: 5, 2018: 5, 2019: 5, 2020: 4, 2021: 4, 2022: 4, 2023: 3, 2024: 3, 2025: 3}
    s["D_RAMADAN"] = [int(q.month == ramadan[q.year]) for q in p]
    for m in range(1, 12):
        s[f"SEAS{m:02d}"] = (p.month == m).astype(int)

    out = s.copy()
    out.insert(0, "date", out.index.strftime("%YM%m"))
    out.to_csv(PROC / "estimation_sample.csv", index=False, float_format="%.8f")
    with pd.ExcelWriter(PROC / "estimation_sample.xlsx") as xw:
        out.to_excel(xw, sheet_name="data", index=False)

    META.mkdir(parents=True, exist_ok=True)
    (META / "validation_report.json").write_text(json.dumps(
        {"sample": f"{SAMPLE_START}–{SAMPLE_END}", "n_obs": len(s), "checks": checks}, indent=2))
    print(f"\nWrote {len(s)} rows × {out.shape[1]} columns to data/processed/estimation_sample.csv")


if __name__ == "__main__":
    build()
