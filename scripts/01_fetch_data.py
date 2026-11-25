"""
01_fetch_data.py — download every raw source file used in the study.

Raw files are written to data/raw/ exactly as served and are never modified.
Each download is appended to data/metadata/download_log.csv (URL, file, UTC
timestamp, bytes, SHA-256) so the provenance of every number is auditable.

Run:  python scripts/01_fetch_data.py
"""
from __future__ import annotations

import csv
import hashlib
import json
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
META = ROOT / "data" / "metadata"
LOG = META / "download_log.csv"

UA = {"User-Agent": "Mozilla/5.0 (research data retrieval; academic project)"}

DBNOMICS = "https://api.db.nomics.world/v22/series/{ds}/{code}?observations=1&format=json"
WB_GEM = ("https://api.worldbank.org/v2/sources/15/country/PAK/series/{code}"
          "/time/all?format=json&per_page=5000")

# (local filename, url)
SOURCES: list[tuple[str, str]] = [
    # --- IMF Consumer Price Index dataset (PBS national CPI, COICOP groups), via DBnomics mirror
    ("imf_cpi_PK_PCPIF_IX.json", DBNOMICS.format(ds="IMF/CPI", code="M.PK.PCPIF_IX")),
    ("imf_cpi_PK_PCPI_IX.json", DBNOMICS.format(ds="IMF/CPI", code="M.PK.PCPI_IX")),
    ("imf_cpi_PK_PCPIT_IX.json", DBNOMICS.format(ds="IMF/CPI", code="M.PK.PCPIT_IX")),
    ("imf_cpi_PK_PCPIH_IX.json", DBNOMICS.format(ds="IMF/CPI", code="M.PK.PCPIH_IX")),
    # --- IMF International Financial Statistics, via DBnomics mirror
    ("imf_ifs_PK_ENDA_XDC_USD_RATE.json", DBNOMICS.format(ds="IMF/IFS", code="M.PK.ENDA_XDC_USD_RATE")),
    ("imf_ifs_PK_ENDE_XDC_USD_RATE.json", DBNOMICS.format(ds="IMF/IFS", code="M.PK.ENDE_XDC_USD_RATE")),
    ("imf_ifs_PK_FMB_XDC.json", DBNOMICS.format(ds="IMF/IFS", code="M.PK.FMB_XDC")),
    # --- World Bank Global Economic Monitor (source 15)
    ("wb_gem_PAK_DPANUSSPB.json", WB_GEM.format(code="DPANUSSPB")),
    ("wb_gem_PAK_CPTOTNSXN.json", WB_GEM.format(code="CPTOTNSXN")),
    # --- FAO Food Price Index (2014-2016 = 100)
    ("fao_food_price_indices_data.csv",
     "https://www.fao.org/media/docs/worldfoodsituationlibraries/wfs-library/food_price_indices_data.csv?download=true"),
    ("fao_ffpi_nominal_real.xlsx",
     "https://www.fao.org/media/docs/worldfoodsituationlibraries/wfs-library/food_price_index_nominal_real.xlsx"),
    # --- World Bank Commodity Price Data (Pink Sheet), monthly
    ("wb_cmo_historical_data_monthly.xlsx",
     "https://thedocs.worldbank.org/en/doc/18675f1d1639c7a34d463f59263ba0a2-0050012025/related/CMO-Historical-Data-Monthly.xlsx"),
]

# PBS Monthly Review on Price Indices (base 2015-16) — Table 1: CPI (National) by group.
PBS = "https://www.pbs.gov.pk/wp-content/uploads/2020/07/"
PBS_REVIEWS = [
    "Monthly-Review-July-2025.pdf",
    "Revised-Monthly-Review-August-2025.docx",
    "1.-Monthly-Review-September-2025-Revised.docx",
    "Monthly-Review-October-2025.docx",
    "Monthly-Review-November-2025.docx",
    "Monthly-Review-December-2025.docx",
    "Monthly-Review-January-2026-1.pdf",
]
for f in PBS_REVIEWS:
    SOURCES.append((f"pbs_cpi_reviews/{f}", PBS + f))


def fetch(url: str, dest: Path, retries: int = 4) -> bytes:
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read()
        except Exception as exc:  # network hiccup: back off and retry
            if attempt == retries - 1:
                raise
            wait = 2 ** (attempt + 1)
            print(f"  retry {attempt + 1} in {wait}s ({exc})", file=sys.stderr)
            time.sleep(wait)
    raise RuntimeError("unreachable")


def main(only_missing: bool = True) -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    META.mkdir(parents=True, exist_ok=True)
    new_log = not LOG.exists()
    with LOG.open("a", newline="") as fh:
        w = csv.writer(fh)
        if new_log:
            w.writerow(["file", "url", "downloaded_utc", "bytes", "sha256"])
        for name, url in SOURCES:
            dest = RAW / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            if only_missing and dest.exists():
                print(f"[skip] {name} (exists — raw files are never overwritten)")
                continue
            print(f"[get ] {name}")
            data = fetch(url, dest)
            if name.endswith(".json"):
                json.loads(data)  # fail loudly on an error page
            dest.write_bytes(data)
            w.writerow([name, url, datetime.now(timezone.utc).isoformat(timespec="seconds"),
                        len(data), hashlib.sha256(data).hexdigest()])


if __name__ == "__main__":
    main(only_missing="--force" not in sys.argv)
