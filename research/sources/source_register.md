# Source register

Every raw file is stored unmodified in `data/raw/`; its URL, UTC download time and SHA-256 are in `data/metadata/download_log.csv`.

## PBS_CPI — Pakistan Bureau of Statistics (PBS)

- **Title:** Monthly Review on Price Indices, Table 1: Consumer Price Index (National) by Group (base 2015-16)
- **URL:** https://www.pbs.gov.pk/price-statistics/
- **Used for:** Food, headline, transport and housing CPI, 2025M08–2025M12; overlap validation 2024M07–2025M07
- **Files:**
  - `data/raw/pbs_cpi_reviews/Monthly-Review-July-2025.pdf` — downloaded 2026-11-25T15:51:46+00:00, sha256 `6009bb8fdba873b3…`
  - `data/raw/pbs_cpi_reviews/Revised-Monthly-Review-August-2025.docx` — downloaded 2026-11-25T15:51:48+00:00, sha256 `f24dbfd95485e2b0…`
  - `data/raw/pbs_cpi_reviews/1.-Monthly-Review-September-2025-Revised.docx` — downloaded 2026-11-25T15:51:50+00:00, sha256 `fe53498a4ea0515b…`
  - `data/raw/pbs_cpi_reviews/Monthly-Review-October-2025.docx` — downloaded 2026-11-25T15:51:53+00:00, sha256 `b5230dc2460bfa57…`
  - `data/raw/pbs_cpi_reviews/Monthly-Review-November-2025.docx` — downloaded 2026-11-25T15:51:55+00:00, sha256 `c8b664a34721a6a5…`
  - `data/raw/pbs_cpi_reviews/Monthly-Review-December-2025.docx` — downloaded 2026-11-25T15:51:57+00:00, sha256 `e88b8a129de5a149…`
  - `data/raw/pbs_cpi_reviews/Monthly-Review-January-2026-1.pdf` — downloaded 2026-11-25T15:52:00+00:00, sha256 `8b9dab8d024a4f16…`

## IMF_CPI — International Monetary Fund — Consumer Price Index dataset (accessed via DBnomics mirror)

- **Title:** Pakistan, monthly CPI by COICOP group: PCPIF_IX (food & non-alcoholic beverages), PCPI_IX, PCPIT_IX, PCPIH_IX
- **URL:** https://db.nomics.world/IMF/CPI
- **Used for:** Food, headline, transport and housing CPI, 2008M07–2025M07
- **Files:**
  - `data/raw/imf_cpi_PK_PCPIF_IX.json` — downloaded 2026-11-25T15:51:37+00:00, sha256 `0b3b374bebf89fba…`
  - `data/raw/imf_cpi_PK_PCPI_IX.json` — downloaded 2026-11-25T15:51:38+00:00, sha256 `a6e35aacf00cbd7c…`
  - `data/raw/imf_cpi_PK_PCPIT_IX.json` — downloaded 2026-11-25T15:51:38+00:00, sha256 `18dddebd593c3d99…`
  - `data/raw/imf_cpi_PK_PCPIH_IX.json` — downloaded 2026-11-25T15:51:39+00:00, sha256 `a1f57188e16e521a…`

## IMF_IFS — International Monetary Fund — International Financial Statistics (via DBnomics)

- **Title:** Pakistan: ENDA_XDC_USD_RATE (period average), ENDE_XDC_USD_RATE (end of period), FMB_XDC (broad money)
- **URL:** https://db.nomics.world/IMF/IFS
- **Used for:** Cross-check of the exchange rate; end-of-period rate; broad money (coverage ends 2025M04, not used)
- **Files:**
  - `data/raw/imf_ifs_PK_ENDA_XDC_USD_RATE.json` — downloaded 2026-11-25T15:51:40+00:00, sha256 `bcdcd44081055bce…`
  - `data/raw/imf_ifs_PK_ENDE_XDC_USD_RATE.json` — downloaded 2026-11-25T15:51:41+00:00, sha256 `3d6a5a4f40666256…`
  - `data/raw/imf_ifs_PK_FMB_XDC.json` — downloaded 2026-11-25T15:51:42+00:00, sha256 `af7ca156e5a3af5b…`

## WB_GEM — World Bank — Global Economic Monitor (data source 15)

- **Title:** Pakistan: DPANUSSPB, official exchange rate, LCU per USD, period average
- **URL:** https://api.worldbank.org/v2/sources/15/country/PAK/series/DPANUSSPB
- **Used for:** EXR, 2015M01–2025M12
- **Files:**
  - `data/raw/wb_gem_PAK_DPANUSSPB.json` — downloaded 2026-11-25T15:51:42+00:00, sha256 `96c305577c9d6ef2…`
  - `data/raw/wb_gem_PAK_CPTOTNSXN.json` — downloaded 2026-11-25T15:51:42+00:00, sha256 `d4eaf20f85b88d44…`

## FAO_FFPI — Food and Agriculture Organization of the United Nations (FAO)

- **Title:** FAO Food Price Index, nominal, 2014–2016 = 100
- **URL:** https://www.fao.org/worldfoodsituation/foodpricesindex/en/
- **Used for:** GFOOD
- **Files:**
  - `data/raw/fao_food_price_indices_data.csv` — downloaded 2026-11-25T15:51:42+00:00, sha256 `6f26341212b13546…`
  - `data/raw/fao_ffpi_nominal_real.xlsx` — downloaded 2026-11-25T15:51:43+00:00, sha256 `706557a9f16d6d5f…`

## WB_PINK — World Bank — Commodity Markets (Pink Sheet)

- **Title:** CMO Historical Data Monthly: food price index (2010 = 100) and Brent crude (USD/bbl)
- **URL:** https://www.worldbank.org/en/research/commodity-markets
- **Used for:** GFOOD_WB and BRENT (robustness)
- **Files:**
  - `data/raw/wb_cmo_historical_data_monthly.xlsx` — downloaded 2026-11-25T15:51:43+00:00, sha256 `83a320affafc8351…`

## Access notes

- The State Bank of Pakistan statistics portal (sbp.org.pk, easydata.sbp.org.pk) returned HTTP 403 to automated requests during data collection, so the exchange rate was taken from the World Bank GEM and cross-checked against IMF IFS; the policy rate could not be obtained and is not used.
- IMF series were read from the DBnomics mirror (api.db.nomics.world), which republishes the IMF CPI and IFS datasets unchanged; the mirror's last IMF update covers data to 2025M07 (CPI) and 2025M06 (IFS).
