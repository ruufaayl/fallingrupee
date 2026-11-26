"""
12_build_dataset_excel.py — one Excel workbook with every variable used in the study, combined month by month,
with its source. Written to deliverables/Falling_Rupee_Dataset.xlsx and public/Falling_Rupee_Dataset.xlsx (website download).
Run: python scripts/12_build_dataset_excel.py
"""
from __future__ import annotations

import shutil
from pathlib import Path

import numpy as np
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "deliverables"
OUT.mkdir(exist_ok=True)

s = pd.read_csv(ROOT / "data" / "processed" / "estimation_sample.csv")

HEAD = PatternFill("solid", fgColor="1F2328")
SUB = PatternFill("solid", fgColor="EFE9DD")
BAND = PatternFill("solid", fgColor="FAF8F3")
WHITE = Font(color="FFFFFF", bold=True, name="Calibri", size=11)
BOLD = Font(bold=True, name="Calibri", size=11)
THIN = Side(style="thin", color="D5CFC2")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(wrap_text=True, vertical="top")
CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)

# simple name, column in data, role, unit, source, series id, url, notes
VARS = [
    ("Food Prices", "FOODCPI", "Dependent variable (Y)", "Index, 2015-16 = 100",
     "Pakistan Bureau of Statistics (PBS) — National CPI, group 'Food & non-alcoholic beverages'",
     "IMF CPI dataset, series M.PK.PCPIF_IX (Jan 2015 – Jul 2025); PBS Monthly Review on Price Indices, Table 1 (Aug – Dec 2025)",
     "https://www.pbs.gov.pk/price-statistics/  |  https://db.nomics.world/IMF/CPI/M.PK.PCPIF_IX",
     "The IMF series is PBS's national food CPI. The two sources agree to within 0.003 index points on every overlapping month. "
     "PBS moved to a new CPI base (2015-16) in July 2019; earlier months are the IMF's linked series."),
    ("Dollar Rate", "EXR", "Independent variable (X1)", "Pakistani rupees per 1 US dollar (monthly average)",
     "World Bank — Global Economic Monitor", "DPANUSSPB (official exchange rate, LCU per USD, period average)",
     "https://api.worldbank.org/v2/sources/15/country/PAK/series/DPANUSSPB",
     "A higher number means a weaker rupee (depreciation). Cross-checked with IMF IFS ENDA_XDC_USD_RATE: correlation 0.99997."),
    ("World Food Prices", "GFOOD", "Independent variable (X2)", "Index, 2014–2016 = 100",
     "Food and Agriculture Organization (FAO) — FAO Food Price Index", "FAO Food Price Index (nominal), column 'Food Price Index'",
     "https://www.fao.org/worldfoodsituation/foodpricesindex/en/",
     "Average world prices of cereals, vegetable oils, dairy, meat and sugar, in US dollars."),
    ("Fuel & Transport Costs", "TRANSCPI", "Independent variable (X3)", "Index, 2015-16 = 100",
     "Pakistan Bureau of Statistics (PBS) — National CPI, group 'Transport'",
     "IMF CPI dataset, series M.PK.PCPIT_IX (Jan 2015 – Jul 2025); PBS Monthly Review, Table 1 (Aug – Dec 2025)",
     "https://www.pbs.gov.pk/price-statistics/  |  https://db.nomics.world/IMF/CPI/M.PK.PCPIT_IX",
     "Used as the domestic energy-cost variable: its largest item is motor fuel (petrol/diesel)."),
]


def style_header(ws, row, ncol):
    for c in range(1, ncol + 1):
        cell = ws.cell(row=row, column=c)
        cell.fill, cell.font, cell.alignment, cell.border = HEAD, WHITE, CENTER, BOX


def widths(ws, ws_widths):
    for i, w in enumerate(ws_widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w


wb = Workbook()

# ---------------------------------------------------------------------------------------------- 1. README
ws = wb.active
ws.title = "Read Me"
rows = [
    ("THE PRICE OF A FALLING RUPEE — DATASET", None),
    ("Does a weaker rupee make food more expensive in Pakistan?", None),
    ("", None),
    ("Period", "January 2015 – December 2025"),
    ("Frequency", "Monthly"),
    ("Observations", f"{len(s)} months per variable — no missing values"),
    ("Dependent variable (Y)", "Food Inflation — monthly % change in Pakistan's national food price index"),
    ("Independent variables (X)", "Rupee Depreciation (PKR per USD) · World Food Inflation (FAO index) · Fuel & Transport Inflation (transport index) · last month's Food Inflation — all monthly % changes, previous month"),
    ("", None),
    ("Sheets in this file", None),
    ("1. Combined Data", "All four variables side by side, one row per month, exactly as used in the study."),
    ("2. Sources", "Where each variable comes from: institution, series code, link, unit and notes."),
    ("3. Regression Data", "The monthly % changes used in the regression (Y and X1–X4), one row per month — ready to re-run the regression."),
    ("4. Summary Statistics", "Mean, median, minimum, maximum, standard deviation and growth of each variable."),
    ("", None),
    ("How the data were combined", "Each series was downloaded from its official source, matched by calendar month, and placed in one table. "
     "Food and transport prices for Aug–Dec 2025 come from the PBS monthly reviews because the IMF copy ends in July 2025; the two "
     "sources were checked against each other on overlapping months before joining. No values were estimated or filled in."),
]
for r, (a, b) in enumerate(rows, 1):
    ws.cell(row=r, column=1, value=a)
    if b is not None:
        ws.cell(row=r, column=2, value=b).alignment = WRAP
        ws.cell(row=r, column=1).font = BOLD
ws["A1"].font = Font(bold=True, size=16, name="Calibri")
ws["A2"].font = Font(italic=True, size=12, name="Calibri", color="7A5C1E")
ws["A10"].font = Font(bold=True, size=12, name="Calibri")
ws.row_dimensions[16].height = 75
widths(ws, [30, 110])

# ---------------------------------------------------------------------------------------------- 2. Combined Data
ws = wb.create_sheet("Combined Data")
hdr = ["Month"] + [v[0] for v in VARS]
units = ["(year-month)"] + [v[3] for v in VARS]
srcs = ["Source →"] + ["PBS (food CPI)", "World Bank GEM", "FAO", "PBS (transport CPI)"]
for c, h in enumerate(hdr, 1):
    ws.cell(row=1, column=c, value=h)
style_header(ws, 1, len(hdr))
for c, (u, so) in enumerate(zip(units, srcs), 1):
    for r, val in ((2, u), (3, so)):
        cell = ws.cell(row=r, column=c, value=val)
        cell.fill, cell.alignment, cell.border = SUB, CENTER, BOX
        cell.font = Font(italic=(r == 2), size=9, name="Calibri", bold=(r == 3))
for i, row in s.iterrows():
    r = i + 4
    y, m = row["date"].split("M")
    ws.cell(row=r, column=1, value=f"{y}-{m}").alignment = Alignment(horizontal="center")
    for c, v in enumerate(VARS, 2):
        cell = ws.cell(row=r, column=c, value=round(float(row[v[1]]), 2))
        cell.number_format = "0.00"
    for c in range(1, len(hdr) + 1):
        ws.cell(row=r, column=c).border = BOX
        if i % 2:
            ws.cell(row=r, column=c).fill = BAND
ws.freeze_panes = "B4"
ws.row_dimensions[2].height = 32
widths(ws, [12, 18, 18, 18, 22])

# ---------------------------------------------------------------------------------------------- 3. Sources
ws = wb.create_sheet("Sources")
hdr = ["Variable (simple name)", "Code", "Role in the study", "Unit", "Source institution", "Series used", "Link", "Notes"]
for c, h in enumerate(hdr, 1):
    ws.cell(row=1, column=c, value=h)
style_header(ws, 1, len(hdr))
for r, v in enumerate(VARS, 2):
    for c, val in enumerate([v[0], v[1], v[2], v[3], v[4], v[5], v[6], v[7]], 1):
        cell = ws.cell(row=r, column=c, value=val)
        cell.alignment, cell.border = WRAP, BOX
    ws.cell(row=r, column=1).font = BOLD
    ws.row_dimensions[r].height = 95
widths(ws, [22, 11, 20, 20, 32, 40, 38, 50])

# ---------------------------------------------------------------------------------------------- 4. Regression Data
ws = wb.create_sheet("Regression Data")
rd = pd.read_csv(ROOT / "data" / "processed" / "regression_data.csv")
cols = [("Month", "Month"), ("Food Inflation (Y)", "FoodInf"), ("Rupee Depreciation, last month (X1)", "RupeeDep_lag1"),
        ("World Food Inflation, last month (X2)", "WorldFoodInf_lag1"), ("Fuel & Transport Inflation, last month (X3)", "FuelInf_lag1"),
        ("Food Inflation, last month (X4)", "FoodInf_lag1")]
for c, (h, _) in enumerate(cols, 1):
    ws.cell(row=1, column=c, value=h)
style_header(ws, 1, len(cols))
ws.row_dimensions[1].height = 45
note = ("Every value is a monthly % change: (this month − last month) ÷ last month × 100, from the Combined Data sheet. X1–X4 are taken from "
        "the previous month. These are exactly the 132 rows used in the regression — it can be re-run with Excel (Data ▸ Data Analysis ▸ "
        "Regression, Y = column B, X = columns C:F) or EViews.")
ws.cell(row=2, column=1, value=note).alignment = WRAP
ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=len(cols))
ws.row_dimensions[2].height = 48
for i, row in rd.iterrows():
    r = i + 3
    ws.cell(row=r, column=1, value=str(row["Month"]))
    for c, (_, k) in enumerate(cols[1:], 2):
        ws.cell(row=r, column=c, value=round(float(row[k]), 4)).number_format = "0.0000"
    for c in range(1, len(cols) + 1):
        ws.cell(row=r, column=c).border = BOX
ws.freeze_panes = "B3"
widths(ws, [12, 18, 22, 22, 24, 20])

# ---------------------------------------------------------------------------------------------- 5. Summary Statistics
ws = wb.create_sheet("Summary Statistics")
hdr = ["Variable", "Observations", "Mean", "Median", "Std. deviation", "Minimum", "Maximum", "Jan 2015", "Dec 2025", "Total change %", "Average yearly growth %"]
for c, h in enumerate(hdr, 1):
    ws.cell(row=1, column=c, value=h)
style_header(ws, 1, len(hdr))
for r, v in enumerate(VARS, 2):
    x = s[v[1]].astype(float)
    yrs = (len(x) - 1) / 12
    vals = [v[0], len(x), x.mean(), x.median(), x.std(), x.min(), x.max(), x.iloc[0], x.iloc[-1],
            (x.iloc[-1] / x.iloc[0] - 1) * 100, ((x.iloc[-1] / x.iloc[0]) ** (1 / yrs) - 1) * 100]
    for c, val in enumerate(vals, 1):
        cell = ws.cell(row=r, column=c, value=round(val, 2) if isinstance(val, float) else val)
        cell.border = BOX
        if c > 2:
            cell.number_format = "0.00"
    ws.cell(row=r, column=1).font = BOLD
widths(ws, [24, 13, 11, 11, 15, 11, 11, 11, 11, 15, 22])

out = OUT / "Falling_Rupee_Dataset.xlsx"
wb.save(out)
(ROOT / "public").mkdir(exist_ok=True)
shutil.copy(out, ROOT / "public" / "Falling_Rupee_Dataset.xlsx")
print("wrote", out.relative_to(ROOT), "and public/Falling_Rupee_Dataset.xlsx")
