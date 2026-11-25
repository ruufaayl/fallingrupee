// Pre-build gate: refuses to build the site if the results registry is incomplete or carries an
// unknown status. Runs automatically via `npm run build`.
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

const REG = join(process.cwd(), "data", "research");
const STATUSES = new Set(["verified", "computed_python_pending_eviews", "not_available", "not_applicable"]);
const errors = [];
const read = (f) => JSON.parse(readFileSync(join(REG, f), "utf8"));
const finite = (label, x) => {
  if (typeof x !== "number" || !Number.isFinite(x)) errors.push(`${label} is not a finite number`);
};

if (!existsSync(join(REG, "manifest.json"))) {
  console.error("✗ data/research/manifest.json missing — run python scripts/05_build_registry.py");
  process.exit(1);
}
const manifest = read("manifest.json");
for (const f of manifest.files) if (!existsSync(join(REG, f))) errors.push(`missing registry file ${f}`);
for (const m of manifest.models) if (!STATUSES.has(m.status)) errors.push(`model ${m.model_id}: bad status ${m.status}`);

for (const f of manifest.files) {
  const o = read(f);
  if (o._meta && !STATUSES.has(o._meta.status)) errors.push(`${f}: bad _meta.status ${o._meta.status}`);
}

for (const name of ["ardl_results.json", "nardl_results.json"]) {
  const m = read(name);
  finite(`${name} bounds F`, m.bounds_test.F);
  finite(`${name} bounds t`, m.bounds_test.t);
  finite(`${name} ECM speed`, m.ecm_regression.speed_of_adjustment);
  for (const l of m.long_run) ["coef", "se", "p", "ci95_low", "ci95_high"].forEach((k) => finite(`${name} LR ${l.variable}.${k}`, l[k]));
  if (!(m.ecm_regression.speed_of_adjustment < 0 && m.ecm_regression.speed_of_adjustment > -2))
    errors.push(`${name}: error-correction coefficient outside (-2, 0)`);
}
const n = read("nardl_results.json");
finite("NARDL LR symmetry p", n.asymmetry?.long_run?.p_chi2);
finite("NARDL impact symmetry p", n.asymmetry?.short_run?.p_impact);
const mult = read("multipliers.json");
for (const k of ["pos", "neg", "asym", "pos_lo95", "pos_hi95", "neg_lo95", "neg_hi95", "asym_lo95", "asym_hi95"])
  if (mult[k].length !== mult.horizon.length || mult[k].some((v) => !Number.isFinite(v))) errors.push(`multipliers.${k} malformed`);
const ts = read("timeseries.json");
for (const k of ["FOODCPI", "EXR", "GFOOD", "TRANSCPI"]) if (ts.series[k].some((v) => v === null)) errors.push(`timeseries ${k} has gaps`);
const f = read("findings.json");
if (!Array.isArray(f.answers) || f.answers.length < 6) errors.push("findings.answers incomplete");

if (errors.length) {
  console.error("✗ Results registry failed validation:\n  - " + errors.join("\n  - "));
  process.exit(1);
}
const counts = manifest.models.map((m) => `${m.model_id}=${m.status}`).join(", ");
console.log(`✓ Results registry valid (${manifest.files.length} files). ${counts}`);
