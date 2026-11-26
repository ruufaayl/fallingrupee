' =====================================================================================
' THE PRICE OF A FALLING RUPEE — main regression and tests (EViews 10 or later)
'
' Model:  FOODINF = b0 + b1*RUPEEDEP(-1) + b2*WORLDFOODINF(-1) + b3*FUELINF(-1) + b4*FOODINF(-1) + e
' All variables are monthly % changes. Sample 2015M01–2025M12 (132 months).
'
' Data: data/processed/pakistan_food_inflation_monthly.csv holds the monthly price levels from 2008M07.
' If the IMPORT line does not work on your version: File > Open > Foreign Data as Workfile, choose
' data/processed/pakistan_food_inflation_monthly.csv, frequency Monthly, start 2008M07, then run from "SERIES" below.
' =====================================================================================
%path = @runpath
cd %path
wfcreate(wf=falling_rupee_simple, page=monthly) m 2008m07 2025m12
import "..\data\processed\pakistan_food_inflation_monthly.csv" @freq m 2008m07 @smpl @all

' ---- SERIES: monthly % changes
series foodinf      = 100*(foodcpi/foodcpi(-1) - 1)
series rupeedep     = 100*(exr/exr(-1) - 1)
series worldfoodinf = 100*(gfood/gfood(-1) - 1)
series fuelinf      = 100*(transcpi/transcpi(-1) - 1)

smpl 2015m01 2025m12

' ---- 1. Descriptive statistics and correlation
group g_levels foodcpi exr gfood transcpi
freeze(tb_desc) g_levels.stats
freeze(tb_cor_levels) g_levels.cor
group g_reg foodinf rupeedep(-1) worldfoodinf(-1) fuelinf(-1) foodinf(-1)
freeze(tb_cor_reg) g_reg.cor

' ---- 2. Stationarity: ADF with intercept, Schwarz lag selection (levels in logs, then monthly % changes)
for %v foodcpi exr gfood transcpi
  series l_{%v} = log({%v})
  freeze(adf_{%v}_level) l_{%v}.uroot(adf, const, info=sic, maxlag=12)
next
for %v foodinf rupeedep worldfoodinf fuelinf
  freeze(adf_{%v}_change) {%v}.uroot(adf, const, info=sic, maxlag=12)
next

' ---- 3. Regression (OLS)
equation eq_main.ls foodinf c rupeedep(-1) worldfoodinf(-1) fuelinf(-1) foodinf(-1)
freeze(tb_regression) eq_main.output

' ---- 4. Multicollinearity
freeze(tb_vif) eq_main.varinf

' ---- 5. Autocorrelation (Durbin-Watson is in the output; Breusch-Godfrey LM)
freeze(tb_bg) eq_main.auto(12)

' ---- 6. Heteroskedasticity
freeze(tb_bp) eq_main.hettest(type=bpg)
freeze(tb_white) eq_main.hettest(type=white)

' ---- 7. Normality (Jarque-Bera on the residual histogram)
eq_main.makeresids resid_main
freeze(tb_jb) resid_main.hist

' ---- 8. Specification
freeze(tb_reset) eq_main.reset(1)

' ---- 9. Asymmetry: falling vs rising rupee
series dep = @recode(rupeedep > 0, rupeedep, 0)
series app = @recode(rupeedep < 0, rupeedep, 0)
equation eq_asym.ls foodinf c dep(-1) app(-1) worldfoodinf(-1) fuelinf(-1) foodinf(-1)
freeze(tb_asym_wald) eq_asym.wald c(2) = c(3)

smpl @all
wfsave falling_rupee_simple.wf1
