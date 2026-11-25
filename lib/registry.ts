/* Central results registry. Every statistic shown on the site flows through here.
   Server-only: JSON is imported at build time, validated, and passed to components as props.
   Updating data/research/*.json (scripts/05_build_registry.py) updates the whole site. */
import "server-only";

import ardlJson from "@/data/research/ardl_results.json";
import corrJson from "@/data/research/correlations.json";
import descJson from "@/data/research/descriptive_statistics.json";
import findingsJson from "@/data/research/findings.json";
import manifestJson from "@/data/research/manifest.json";
import multJson from "@/data/research/multipliers.json";
import nardlJson from "@/data/research/nardl_results.json";
import olsJson from "@/data/research/ols_results.json";
import robJson from "@/data/research/robustness.json";
import sourcesJson from "@/data/research/sources.json";
import statJson from "@/data/research/stationarity.json";
import tsJson from "@/data/research/timeseries.json";
import varsJson from "@/data/research/variables.json";
import waldJson from "@/data/research/wald_tests.json";

import type {
  ArdlModel,
  Correlations,
  Descriptives,
  Findings,
  Manifest,
  Multipliers,
  OlsResults,
  Robustness,
  Source,
  Stationarity,
  Status,
  TimeSeries,
  Variable,
  WaldTests,
} from "./types";

const DISPLAYABLE: Status[] = ["verified", "computed_python_pending_eviews"];

function requireFinite(label: string, ...xs: (number | null | undefined)[]) {
  for (const x of xs) {
    if (typeof x !== "number" || !Number.isFinite(x)) {
      throw new Error(`Registry validation failed: ${label} is not a finite number`);
    }
  }
}

function checked<T extends { _meta: { status: Status } }>(name: string, obj: unknown): T {
  const o = obj as T;
  if (!o || !o._meta || !DISPLAYABLE.concat(["not_available", "not_applicable"]).includes(o._meta.status)) {
    throw new Error(`Registry validation failed: ${name} has no valid _meta.status`);
  }
  return o;
}

export const ardl = checked<ArdlModel>("ardl_results", ardlJson);
export const nardl = checked<ArdlModel>("nardl_results", nardlJson);
export const ols = checked<OlsResults>("ols_results", olsJson);
export const stationarity = checked<Stationarity>("stationarity", statJson);
export const descriptives = checked<Descriptives>("descriptive_statistics", descJson);
export const correlations = checked<Correlations>("correlations", corrJson);
export const multipliers = checked<Multipliers>("multipliers", multJson);
export const wald = checked<WaldTests>("wald_tests", waldJson);
export const robustness = checked<Robustness>("robustness", robJson);
export const timeseries = checked<TimeSeries>("timeseries", tsJson);
export const findings = findingsJson as unknown as Findings;
export const manifest = manifestJson as unknown as Manifest;
export const variables = (varsJson as unknown as {
  variables: Variable[];
  considered_but_excluded: { variable: string; decision: string; reason: string }[];
});
export const sources = (sourcesJson as unknown as { sources: Source[] }).sources;

// Build-time integrity checks: the page will not build if a headline number is missing.
for (const m of [ardl, nardl]) {
  requireFinite(`${m.model_id} bounds F`, m.bounds_test.F, m.bounds_test.t);
  requireFinite(`${m.model_id} ECT`, m.ecm_regression.speed_of_adjustment);
  m.long_run.forEach((l) => requireFinite(`${m.model_id} long run ${l.variable}`, l.coef, l.se, l.p));
}
requireFinite("NARDL asymmetry", nardl.asymmetry?.long_run.p_chi2, nardl.asymmetry?.short_run.p_impact);
requireFinite("headline", findings.headline_numbers.food_cpi_change_pct, findings.headline_numbers.exr_change_pct);
if (multipliers.pos.length !== multipliers.horizon.length) throw new Error("multipliers: length mismatch");

export function isDisplayable(s: Status) {
  return DISPLAYABLE.includes(s);
}

export function longRun(model: ArdlModel, variable: string) {
  const l = model.long_run.find((x) => x.variable === variable);
  if (!l) throw new Error(`long run ${variable} missing in ${model.model_id}`);
  return l;
}

export function modelStatus(id: string): Status {
  return manifest.models.find((m) => m.model_id === id)?.status ?? "not_available";
}
