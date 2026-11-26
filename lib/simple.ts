import "server-only";

import regJson from "@/research/outputs/simple_regression.json";
import simpleJson from "@/data/research/simple.json";

export interface Coef {
  code: string;
  name: string;
  symbol: string;
  coef: number;
  se: number;
  t: number;
  p: number;
  ci: [number, number];
  significant: boolean;
  plain: string;
}

export interface SimpleResults {
  title: string;
  problem: string;
  question: string;
  period: string;
  n: number;
  variables: { role: string; name: string; symbol: string; measure: string; source: string; why: string }[];
  equation_general: string;
  equation_estimated: string;
  equation_note: string;
  constant: number;
  coefficients: Coef[];
  hypotheses: { id: string; question: string; h0: string; h1: string; test: string; result: string; p: number; reject: boolean; decision: string }[];
  stationarity: { name: string; level_stat: number; level_p: number; change_stat: number; change_p: number; crit5: number; level_result: string; change_result: string }[];
  vif: { name: string; vif: number; tolerance: number }[];
  tests: { group: string; name: string; checks: string; h0: string | null; result: string; decision: string; pass: boolean | null; meaning: string }[];
  asymmetry: { dep_coef: number; dep_p: number; dep_ci: [number, number]; app_coef: number; app_p: number; app_ci: [number, number]; dep_months: number; app_months: number; F: number; p: number; df: number[] };
  fit: { r2: number; adj_r2: number; F: number; F_p: number; df: number[]; se_regression: number };
  total_effect_rupee: number;
  answer: string[];
  one_line: string;
}

export interface Regression {
  correlation_changes: { variables: string[]; matrix: number[][] };
  correlation_levels: { variables: string[]; matrix: number[][] };
  diagnostics: Record<string, unknown> & { durbin_watson: number };
  fitted: { dates: string[]; actual: number[]; fitted: number[]; resid: number[] };
}

export const simple = simpleJson as unknown as SimpleResults;
export const regression = regJson as unknown as Regression;
