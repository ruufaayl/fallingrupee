/* Chart tokens. Series colours are the validated palette (see app/globals.css). */
export const C = {
  surface: "#0e0f11",
  ink: "#0b0c0e",
  paper: "#f1ece2",
  dim: "#c9c3b7",
  muted: "#9a958b",
  faint: "#6c6860",
  grid: "#24272c",
  axis: "#3a3f46",
  gold: "#c9a24a",
  food: "#e5484d",
  exr: "#d28e05",
  energy: "#338ced",
  world: "#00a888",
  rise: "#e5484d",
  fall: "#00a888",
};

export const FONT_MONO = "JetBrains Mono Variable, ui-monospace, monospace";
export const FONT_SANS = "Inter Variable, ui-sans-serif, system-ui, sans-serif";

export const baseText = { color: C.muted, fontFamily: FONT_MONO, fontSize: 11 };

export function axisCommon(extra: Record<string, unknown> = {}) {
  return {
    axisLine: { lineStyle: { color: C.axis } },
    axisTick: { show: false },
    axisLabel: { ...baseText },
    splitLine: { lineStyle: { color: C.grid } },
    nameTextStyle: { ...baseText },
    ...extra,
  };
}

export const tooltipBase = {
  backgroundColor: "rgba(21,23,26,0.96)",
  borderColor: C.axis,
  borderWidth: 1,
  padding: [10, 12],
  textStyle: { color: C.paper, fontFamily: FONT_SANS, fontSize: 12 },
  extraCssText: "box-shadow: 0 8px 28px rgba(0,0,0,.45); border-radius: 2px;",
};

export const SERIES_COLOR: Record<string, string> = {
  FOODCPI: C.food,
  EXR: C.exr,
  TRANSCPI: C.energy,
  GFOOD: C.world,
  CPI: C.dim,
  HOUSCPI: "#9887ef",
  BRENT: "#8a8f98",
  GFOOD_WB: C.world,
};
