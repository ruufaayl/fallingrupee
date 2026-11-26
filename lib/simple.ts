import "server-only";

import simpleJson from "@/data/research/simple.json";

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
  coefficients: { code: string; name: string; symbol: string; coef: number; se: number; p: number; ci: [number, number]; significant: boolean; plain: string }[];
  hypotheses: { id: string; question: string; h0: string; h1: string; test: string; result: string; reject: boolean; decision: string; partial?: boolean }[];
  unit_roots: { name: string; level_p: number; diff_p: number; order: string }[];
  tests: { name: string; checks: string; h0: string | null; result: string; decision: string; pass: boolean | null; meaning: string }[];
  asymmetry: { falling: number; falling_p: number; rising: number; rising_p: number; impact_falling: number; impact_rising: number; p_short: number; p_long: number };
  fit: { r2: number; adj_r2: number; nobs: number };
  answer: string[];
  one_line: string;
}

export const simple = simpleJson as unknown as SimpleResults;
