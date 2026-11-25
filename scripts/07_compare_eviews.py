"""
07_compare_eviews.py — mark results as EViews-verified.

After running eviews/00_master.prg in EViews, the folder eviews/output/ contains CSV coefficient tables
(ols.csv, ardl_main_cec.csv, ardl_main_lev.csv, nardl_main_cec.csv, nardl_main_lev.csv). This script re-fits the
same equations in Python and compares every coefficient and standard error. If all agree within tolerance, the model
is recorded as verified in research/eviews_verification.json; scripts/05_build_registry.py then propagates the
"verified" status to the website registry.

Run: python scripts/07_compare_eviews.py && python scripts/05_build_registry.py
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

sys.path.insert(0, str(Path(__file__).parent))
import ardl_engine as E  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
EVO = ROOT / "eviews" / "output"
VER = ROOT / "research" / "eviews_verification.json"
RTOL, ATOL = 1e-4, 1e-7

df = pd.read_csv(ROOT / "data" / "processed" / "estimation_sample.csv")
df.index = pd.period_range("2015-01", periods=len(df), freq="M")
SEAS = [c for c in df if c.startswith("SEAS")]
out = json.loads(VER.read_text()) if VER.exists() else {"models": {}}


def compare(model_id, py_params, py_se, csv):
    path = EVO / csv
    if not path.exists():
        print(f"[missing] {csv} — run eviews/00_master.prg first")
        return None
    ev = pd.read_csv(path)
    ok = len(ev) == len(py_params)
    rows = []
    for i, (name, b, s) in enumerate(zip(py_params.index, py_params.values, py_se.values)):
        eb, es = (float(ev.loc[i, "coef"]), float(ev.loc[i, "se"])) if i < len(ev) else (np.nan, np.nan)
        good = bool(np.isclose(eb, b, rtol=RTOL, atol=ATOL) and np.isclose(es, s, rtol=RTOL, atol=ATOL))
        ok &= good
        rows.append({"term": name, "python": b, "eviews": eb, "python_se": s, "eviews_se": es, "match": good})
    print(f"[{'OK' if ok else 'MISMATCH'}] {model_id} / {csv}")
    return {"file": csv, "all_match": bool(ok), "rows": rows}


def run():
    ols = sm.OLS(df["LFOODCPI"], sm.add_constant(df[["LEXR", "LGFOOD", "LTRANSCPI"]])).fit()
    checks = {"OLS_LEVELS": [compare("OLS_LEVELS", ols.params, ols.bse, "ols.csv")]}
    for mid, fname, xs in (("ARDL_MAIN", "ardl_results", ["LEXR", "LGFOOD", "LTRANSCPI"]),
                           ("NARDL_MAIN", "nardl_results", ["LEXR_POS", "LEXR_NEG", "LGFOOD", "LTRANSCPI"])):
        order = tuple(json.loads((ROOT / "research" / "outputs" / f"{fname}.json").read_text())["selection"]["chosen_order"])
        r = E.fit(df, "LFOODCPI", xs, order, SEAS, start=4)
        checks[mid] = [compare(mid, r.cec.params, r.cec.bse, f"{mid.lower()}_cec.csv"),
                       compare(mid, r.levels.params, r.levels.bse, f"{mid.lower()}_lev.csv")]
    for mid, res in checks.items():
        if any(x is None for x in res):
            continue
        out["models"][mid] = {"checked_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                              "tolerance": {"rtol": RTOL, "atol": ATOL},
                              "all_within_tolerance": all(x["all_match"] for x in res), "comparisons": res}
    VER.write_text(json.dumps(out, indent=2))
    print(f"wrote {VER}")


if __name__ == "__main__":
    run()
