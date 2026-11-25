/* Typed contracts for every research output in data/research/*.json.
   These mirror what scripts/03_estimate.py and scripts/05_build_registry.py write. */

export type Status =
  | "verified"
  | "computed_python_pending_eviews"
  | "not_available"
  | "not_applicable";

export interface Meta {
  generated_utc: string;
  engine: { software: string; packages: Record<string, string> };
  status: Status;
  estimation_sample: string;
  script: string;
}

export interface Coef {
  term: string;
  coef: number | null;
  se: number | null;
  t: number | null;
  p: number | null;
}

export interface LongRun {
  variable: string;
  coef: number;
  se: number;
  t: number;
  p: number;
  ci95_low: number;
  ci95_high: number;
}

export interface DiagTest {
  group: string;
  test: string;
  null: string;
  stat_name?: string;
  stat: number | null;
  df?: number | number[];
  p: number | null;
  F?: number | null;
  p_F?: number | null;
  reject_5pct?: boolean;
  note?: string;
  skewness?: number;
  kurtosis?: number;
}

export interface Stability {
  dates: string[];
  cusum: number[];
  cusum_lo: number[];
  cusum_hi: number[];
  cusum_within_bounds: boolean;
  cusumsq: number[];
  cusumsq_expected: number[];
  cusumsq_c0: number;
  cusumsq_within_bounds: boolean;
  cusumsq_max_dev: number;
  cusumsq_max_dev_date: string;
  method: string;
}

export interface BoundsCV {
  F_I0: number;
  F_I1: number;
  t_I0: number;
  t_I1: number;
}

export interface BoundsTest {
  k: number;
  F: number;
  t: number;
  df: number[];
  asymptotic: Record<string, BoundsCV>;
  finite_sample?: Record<string, BoundsCV>;
  finite_sample_nobs?: number;
  finite_sample_nsim?: number;
  p_value_F_I1_sim?: number;
  p_value_F_I0_sim?: number;
  p_value_t_I1_sim?: number;
  decision_F_5pct_asymptotic: string;
  decision_t_5pct_asymptotic: string;
  decision_F_5pct_finite?: string;
  decision_t_5pct_finite?: string;
}

export interface ArdlModel {
  _meta: Meta;
  model_id: string;
  label: string;
  dependent: string;
  regressors: string[];
  deterministics: string;
  selection: {
    criterion: string;
    max_lags: number;
    models_evaluated: number;
    chosen_order: number[];
    top_models: { order: number[]; aic: number; sic: number; hq: number; adj_r2: number }[];
  };
  sample: { start: string; end: string; nobs: number };
  levels_equation: {
    coefficients: Coef[];
    seasonal_dummies_joint_F: number | null;
    seasonal_dummies_joint_p: number | null;
    r2: number;
    adj_r2: number;
    se_regression: number;
    loglik: number;
    F: number;
    F_p: number;
    dw: number;
  };
  cec_equation: { description: string; coefficients: Coef[]; r2: number };
  bounds_test: BoundsTest;
  long_run: LongRun[];
  ecm_regression: {
    description: string;
    coefficients: Coef[];
    r2: number;
    adj_r2: number;
    dw: number;
    speed_of_adjustment: number;
    speed_p: number;
    half_life_months: number;
  };
  diagnostics: DiagTest[];
  stability: Stability;
  fitted: { dates: string[]; actual: number[]; fitted: number[]; resid: number[] };
  asymmetry?: {
    long_run: {
      null: string;
      L_pos: number;
      L_neg: number;
      difference: number;
      se_difference: number;
      wald_chi2: number;
      df: number;
      p_chi2: number;
      F_linear: number;
      F_df: number[];
      p_F_linear: number;
    };
    short_run: {
      null_impact: string;
      beta0_pos: number;
      beta0_neg: number;
      F_impact: number;
      F_impact_df: number[];
      p_impact: number;
      null_additive?: string;
      p_additive?: number;
      F_additive?: number;
    };
  };
}

export interface OlsResults {
  _meta: Meta;
  model_id: string;
  equation: string;
  nobs: number;
  coefficients: Coef[];
  coefficients_hac: Coef[];
  r2: number;
  adj_r2: number;
  F: number;
  F_p: number;
  se_regression: number;
  dw: number;
  aic: number;
  bic: number;
  spurious_regression_check: {
    granger_newbold_rule: string;
    r2_exceeds_dw: boolean;
    engle_granger: { null: string; stat: number; p: number; crit: Record<string, number> };
  };
  diagnostics: DiagTest[];
  first_difference_ols: { equation: string; nobs: number; coefficients: Coef[]; r2: number; dw: number };
}

export interface UnitRootRow {
  variable: string;
  form: "level" | "first_difference" | "second_difference";
  test: "ADF" | "PP" | "KPSS";
  deterministic: "c" | "ct";
  lag_rule: string;
  lags: number;
  stat: number;
  p: number;
  crit: Record<string, number>;
  null: string;
  reject_5pct: boolean;
  p_note?: string;
}

export interface Stationarity {
  _meta: Meta;
  rule: string;
  summary: Record<string, { label: string; integration_order: string; not_I2: boolean }>;
  tests: UnitRootRow[];
  bounds_admissible: boolean;
}

export interface DescRow {
  variable: string;
  label: string;
  n: number;
  mean: number;
  median: number;
  sd: number;
  min: number;
  min_date: string;
  max: number;
  max_date: string;
  skewness: number;
  kurtosis: number;
  jarque_bera: number;
  jb_p: number;
  total_change_pct?: number;
  cagr_pct?: number;
}

export interface Descriptives {
  _meta: Meta;
  variables: DescRow[];
  annual_means: Record<string, Record<string, number>>;
  annual_growth_pct: Record<string, Record<string, number>>;
  food_inflation_outliers: { method: string; items: { date: string; food_inf_mom: number; robust_z: number }[] };
  largest_depreciation_months: { date: string; pct: number }[];
  largest_appreciation_months: { date: string; pct: number }[];
  exchange_rate_months: {
    depreciating: number;
    appreciating: number;
    cumulative_depreciation_log: number;
    cumulative_appreciation_log: number;
  };
}

export interface Matrix {
  variables: string[];
  matrix: number[][];
}

export interface Correlations {
  _meta: Meta;
  levels_log: Matrix;
  first_differences_log: Matrix;
  yoy_rates: Matrix;
  vif_levels: { variable: string; vif: number; tolerance: number }[];
  vif_differences: { variable: string; vif: number; tolerance: number }[];
  vif_nardl_levels: { variable: string; vif: number; tolerance: number }[];
  note: string;
}

export interface Multipliers {
  _meta: Meta;
  model_id: string;
  units: string;
  definitions: Record<string, string>;
  band: string;
  long_run_pos: number;
  long_run_neg: number;
  horizon: number[];
  pos: number[];
  neg: number[];
  asym: number[];
  pos_lo95: number[];
  pos_hi95: number[];
  neg_lo95: number[];
  neg_hi95: number[];
  asym_lo95: number[];
  asym_hi95: number[];
  asym_lo90: number[];
  asym_hi90: number[];
}

export interface WaldTests {
  _meta: Meta;
  tests: {
    id: string;
    model_id: string;
    null: string;
    statistic?: string;
    value?: number;
    df?: number | number[];
    p?: number;
    decision?: string;
    alt_statistic?: string;
    alt_value?: number;
    alt_df?: number[];
    alt_p?: number;
    status?: Status;
    reason?: string;
  }[];
}

export interface RobustRow {
  id: string;
  label: string;
  note?: string;
  sample: string;
  nobs: number;
  order: number[];
  criterion: string;
  bounds_F: number;
  bounds_t: number;
  F_decision_5pct: string;
  t_decision_5pct: string;
  ect: number;
  ect_p: number;
  long_run: Record<string, { coef: number; p: number }>;
  bg2_p: number;
  jb_p: number;
  lr_sym_p?: number;
  impact_sym_p?: number;
  sr_additive_p?: number | null;
  status?: string;
  error?: string;
}

export interface Robustness {
  _meta: Meta;
  nardl_specifications: RobustRow[];
  ardl_specifications: RobustRow[];
  critical_values_note: string;
}

export interface TimeSeries {
  _meta: Meta;
  dates: string[];
  series: Record<string, (number | null)[]>;
  rebased_2015m01: Record<string, number[]>;
}

export interface Variable {
  code: string;
  log_code: string;
  role: string;
  name: string;
  definition: string;
  unit: string;
  source: string[];
  series_id: string;
  transform: string;
  rebasing: string;
}

export interface Source {
  id: string;
  institution: string;
  title: string;
  url: string;
  used_for: string;
  files: string[];
  downloads: { file: string; downloaded_utc: string; sha256: string }[];
}

export interface Findings {
  headline_numbers: {
    food_cpi_change_pct: number;
    exr_change_pct: number;
    gfood_change_pct: number;
    food_infl_peak: number;
    food_infl_peak_date: string;
    food_cagr_pct: number;
    exr_peak: number;
    exr_peak_date: string;
    nobs: number;
  };
  answers: { q: string; model: string; answer: string; strength: string }[];
  speed_of_adjustment: Record<string, number>;
  multiplier_snapshots: {
    h: number;
    depreciation: number;
    appreciation_response: number;
    asym: number;
    asym_lo95: number;
    asym_hi95: number;
  }[];
  robustness_counts: Record<string, number>;
  status: Status;
}

export interface Manifest {
  project: string;
  generated_utc: string;
  estimation_sample: { start: string; end: string; frequency: string; nobs: number };
  status_legend: Record<Status, string>;
  models: { model_id: string; description: string; status: Status; eviews_program: string }[];
  files: string[];
}
