export const fmt = (x: number | null | undefined, d = 2) =>
  x === null || x === undefined || !Number.isFinite(x) ? "—" : x.toFixed(d).replace("-", "−");

export const fmtSigned = (x: number | null | undefined, d = 2) =>
  x === null || x === undefined || !Number.isFinite(x) ? "—" : (x > 0 ? "+" : "") + fmt(x, d);

export const fmtP = (p: number | null | undefined) => {
  if (p === null || p === undefined || !Number.isFinite(p)) return "—";
  if (p < 0.001) return "< 0.001";
  return p.toFixed(3);
};

export const stars = (p: number | null | undefined) =>
  p === null || p === undefined ? "" : p < 0.01 ? "***" : p < 0.05 ? "**" : p < 0.1 ? "*" : "";

export const sig = (p: number | null | undefined, a = 0.05) => typeof p === "number" && p < a;

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
export const monthLabel = (d: string) => {
  const [y, m] = d.split("-");
  return `${MONTHS[Number(m) - 1]} ${y}`;
};

export const VAR_LABEL: Record<string, string> = {
  LFOODCPI: "Food CPI",
  LEXR: "Exchange rate (PKR/USD)",
  LEXR_POS: "Depreciation (EXR⁺)",
  LEXR_NEG: "Appreciation (EXR⁻)",
  LGFOOD: "World food prices (FAO)",
  LGFOOD_WB: "World food prices (World Bank)",
  LTRANSCPI: "Energy: transport CPI",
  LHOUSCPI: "Energy: housing & utilities CPI",
  LBRENT: "Brent crude (USD)",
  LCPI: "Headline CPI",
  C: "Constant",
};

/** Turn engine term names into readable labels, e.g. D(LEXR_NEG) -> Δ Appreciation (EXR⁻). */
export function termLabel(t: string): string {
  if (t === "C" || t === "const") return "Constant";
  if (t === "CointEq(-1)") return "Error-correction term, ECTₜ₋₁";
  const lagM = t.match(/^(.*)\(-(\d+)\)$/);
  const dM = t.match(/^D\((.*)\)$/);
  if (dM) return "Δ " + termLabel(dM[1]);
  if (lagM) return `${termLabel(lagM[1])} ₜ₋${lagM[2]}`;
  const base = t.replace("**", "");
  return VAR_LABEL[base] ?? base;
}
