/* Bibliography. Only real, verifiable works are listed; every entry is cited in the report or on the site. */
export interface Ref {
  key: string;
  text: string;
  doi?: string;
  url?: string;
  group: "Methodology" | "Exchange-rate pass-through & asymmetry" | "Pakistan" | "Data";
}

export const REFERENCES: Ref[] = [
  { key: "PSS2001", group: "Methodology", text: "Pesaran, M. H., Shin, Y., & Smith, R. J. (2001). Bounds testing approaches to the analysis of level relationships. Journal of Applied Econometrics, 16(3), 289–326.", doi: "10.1002/jae.616" },
  { key: "PS1999", group: "Methodology", text: "Pesaran, M. H., & Shin, Y. (1999). An autoregressive distributed lag modelling approach to cointegration analysis. In S. Strøm (Ed.), Econometrics and Economic Theory in the 20th Century: The Ragnar Frisch Centennial Symposium (pp. 371–413). Cambridge University Press." },
  { key: "SYG2014", group: "Methodology", text: "Shin, Y., Yu, B., & Greenwood-Nimmo, M. (2014). Modelling asymmetric cointegration and dynamic multipliers in a nonlinear ARDL framework. In R. C. Sickles & W. C. Horrace (Eds.), Festschrift in Honor of Peter Schmidt (pp. 281–314). Springer.", doi: "10.1007/978-1-4899-8008-3_9" },
  { key: "Narayan2005", group: "Methodology", text: "Narayan, P. K. (2005). The saving and investment nexus for China: Evidence from cointegration tests. Applied Economics, 37(17), 1979–1990.", doi: "10.1080/00036840500278103" },
  { key: "EG1987", group: "Methodology", text: "Engle, R. F., & Granger, C. W. J. (1987). Co-integration and error correction: Representation, estimation, and testing. Econometrica, 55(2), 251–276.", doi: "10.2307/1913236" },
  { key: "GN1974", group: "Methodology", text: "Granger, C. W. J., & Newbold, P. (1974). Spurious regressions in econometrics. Journal of Econometrics, 2(2), 111–120.", doi: "10.1016/0304-4076(74)90034-7" },
  { key: "DF1979", group: "Methodology", text: "Dickey, D. A., & Fuller, W. A. (1979). Distribution of the estimators for autoregressive time series with a unit root. Journal of the American Statistical Association, 74(366), 427–431.", doi: "10.2307/2286348" },
  { key: "PP1988", group: "Methodology", text: "Phillips, P. C. B., & Perron, P. (1988). Testing for a unit root in time series regression. Biometrika, 75(2), 335–346.", doi: "10.1093/biomet/75.2.335" },
  { key: "KPSS1992", group: "Methodology", text: "Kwiatkowski, D., Phillips, P. C. B., Schmidt, P., & Shin, Y. (1992). Testing the null hypothesis of stationarity against the alternative of a unit root. Journal of Econometrics, 54(1–3), 159–178.", doi: "10.1016/0304-4076(92)90104-Y" },
  { key: "Breusch1978", group: "Methodology", text: "Breusch, T. S. (1978). Testing for autocorrelation in dynamic linear models. Australian Economic Papers, 17(31), 334–355." },
  { key: "Godfrey1978", group: "Methodology", text: "Godfrey, L. G. (1978). Testing against general autoregressive and moving average error models when the regressors include lagged dependent variables. Econometrica, 46(6), 1293–1301.", doi: "10.2307/1913829" },
  { key: "BP1979", group: "Methodology", text: "Breusch, T. S., & Pagan, A. R. (1979). A simple test for heteroscedasticity and random coefficient variation. Econometrica, 47(5), 1287–1294.", doi: "10.2307/1911963" },
  { key: "White1980", group: "Methodology", text: "White, H. (1980). A heteroskedasticity-consistent covariance matrix estimator and a direct test for heteroskedasticity. Econometrica, 48(4), 817–838.", doi: "10.2307/1912934" },
  { key: "Engle1982", group: "Methodology", text: "Engle, R. F. (1982). Autoregressive conditional heteroscedasticity with estimates of the variance of United Kingdom inflation. Econometrica, 50(4), 987–1007.", doi: "10.2307/1912773" },
  { key: "JB1980", group: "Methodology", text: "Jarque, C. M., & Bera, A. K. (1980). Efficient tests for normality, homoscedasticity and serial independence of regression residuals. Economics Letters, 6(3), 255–259.", doi: "10.1016/0165-1765(80)90024-5" },
  { key: "Ramsey1969", group: "Methodology", text: "Ramsey, J. B. (1969). Tests for specification errors in classical linear least-squares regression analysis. Journal of the Royal Statistical Society: Series B, 31(2), 350–371." },
  { key: "BDE1975", group: "Methodology", text: "Brown, R. L., Durbin, J., & Evans, J. M. (1975). Techniques for testing the constancy of regression relationships over time. Journal of the Royal Statistical Society: Series B, 37(2), 149–192.", doi: "10.1111/j.2517-6161.1975.tb01532.x" },
  { key: "Durbin1969", group: "Methodology", text: "Durbin, J. (1969). Tests for serial correlation in regression analysis based on the periodogram of least-squares residuals. Biometrika, 56(1), 1–15.", doi: "10.1093/biomet/56.1.1" },
  { key: "NW1987", group: "Methodology", text: "Newey, W. K., & West, K. D. (1987). A simple, positive semi-definite, heteroskedasticity and autocorrelation consistent covariance matrix. Econometrica, 55(3), 703–708.", doi: "10.2307/1913610" },
  { key: "Dornbusch1987", group: "Exchange-rate pass-through & asymmetry", text: "Dornbusch, R. (1987). Exchange rates and prices. American Economic Review, 77(1), 93–106." },
  { key: "Taylor2000", group: "Exchange-rate pass-through & asymmetry", text: "Taylor, J. B. (2000). Low inflation, pass-through, and the pricing power of firms. European Economic Review, 44(7), 1389–1408.", doi: "10.1016/S0014-2921(00)00037-4" },
  { key: "CG2005", group: "Exchange-rate pass-through & asymmetry", text: "Campa, J. M., & Goldberg, L. S. (2005). Exchange rate pass-through into import prices. Review of Economics and Statistics, 87(4), 679–690.", doi: "10.1162/003465305775098189" },
  { key: "CH2006", group: "Exchange-rate pass-through & asymmetry", text: "Choudhri, E. U., & Hakura, D. S. (2006). Exchange rate pass-through to domestic prices: Does the inflationary environment matter? Journal of International Money and Finance, 25(4), 614–639." },
  { key: "DLV2012", group: "Exchange-rate pass-through & asymmetry", text: "Delatte, A.-L., & López-Villavicencio, A. (2012). Asymmetric exchange rate pass-through: Evidence from major countries. Journal of Macroeconomics, 34(3), 833–844." },
  { key: "Peltzman2000", group: "Exchange-rate pass-through & asymmetry", text: "Peltzman, S. (2000). Prices rise faster than they fall. Journal of Political Economy, 108(3), 466–502.", doi: "10.1086/262126" },
  { key: "Bacon1991", group: "Exchange-rate pass-through & asymmetry", text: "Bacon, R. W. (1991). Rockets and feathers: The asymmetric speed of adjustment of UK retail gasoline prices to cost changes. Energy Economics, 13(3), 211–218.", doi: "10.1016/0140-9883(91)90022-R" },
  { key: "CK2002", group: "Pakistan", text: "Choudhri, E. U., & Khan, M. S. (2002). The exchange rate and consumer prices in Pakistan: Is rupee devaluation inflationary? The Pakistan Development Review, 41(2), 107–120." },
  { key: "HS2004", group: "Pakistan", text: "Hyder, Z., & Shah, S. (2004). Exchange rate pass-through to domestic prices in Pakistan (SBP Working Paper No. 5). State Bank of Pakistan." },
  { key: "KS2006", group: "Pakistan", text: "Khan, M. S., & Schimmelpfennig, A. (2006). Inflation in Pakistan: Money or wheat? (IMF Working Paper WP/06/60). International Monetary Fund." },
  { key: "PBS", group: "Data", text: "Pakistan Bureau of Statistics. Monthly Review on Price Indices (base 2015-16), July 2025 – January 2026. Islamabad: PBS.", url: "https://www.pbs.gov.pk/price-statistics/" },
  { key: "IMFCPI", group: "Data", text: "International Monetary Fund. Consumer Price Index (CPI) dataset and International Financial Statistics, Pakistan, accessed through DBnomics.", url: "https://db.nomics.world/IMF/CPI" },
  { key: "WBGEM", group: "Data", text: "World Bank. Global Economic Monitor (GEM): official exchange rate, LCU per USD, period average (DPANUSSPB).", url: "https://databank.worldbank.org/source/global-economic-monitor-(gem)" },
  { key: "FAO", group: "Data", text: "Food and Agriculture Organization of the United Nations. FAO Food Price Index (2014–2016 = 100).", url: "https://www.fao.org/worldfoodsituation/foodpricesindex/en/" },
  { key: "WBPINK", group: "Data", text: "World Bank. Commodity Markets: Pink Sheet monthly historical data (CMO-Historical-Data-Monthly).", url: "https://www.worldbank.org/en/research/commodity-markets" },
];
