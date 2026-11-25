"use client";

import type { EChartsOption } from "echarts";
import { useMemo, useState } from "react";

import { Segmented } from "@/components/ui/Segmented";
import { monthLabel } from "@/lib/format";

import { EChart } from "./EChart";
import { axisCommon, baseText, C, SERIES_COLOR, tooltipBase } from "./theme";

type Series = Record<string, (number | null)[]>;

const pctFmt = (v: number) => `${v > 0 ? "+" : ""}${v.toFixed(1)}%`;

export function InflationChart({ dates, s, peak }: { dates: string[]; s: Series; peak: { date: string; value: number } }) {
  const option = useMemo<EChartsOption>(() => {
    const x = dates.map(monthLabel);
    const line = (name: string, data: (number | null)[], color: string, width = 2, area = false) => ({
      name,
      type: "line" as const,
      data,
      showSymbol: false,
      symbolSize: 8,
      smooth: false,
      lineStyle: { width, color },
      itemStyle: { color },
      emphasis: { focus: "series" as const },
      ...(area ? { areaStyle: { color: "rgba(229,72,77,0.10)" } } : {}),
    });
    return {
      grid: { left: 48, right: 24, top: 76, bottom: 56 },
      legend: { top: 0, left: 0, textStyle: { ...baseText, color: C.dim }, icon: "rect", itemWidth: 14, itemHeight: 2 },
      tooltip: {
        ...tooltipBase,
        trigger: "axis",
        axisPointer: { type: "line", lineStyle: { color: C.axis } },
        valueFormatter: (v) => (typeof v === "number" ? pctFmt(v) : "—"),
      },
      xAxis: { type: "category", data: x, boundaryGap: false, ...axisCommon({ splitLine: { show: false } }), axisLabel: { ...baseText, interval: 11, formatter: (v: string) => v.slice(-4) } },
      yAxis: { type: "value", name: "% year on year", ...axisCommon(), axisLabel: { ...baseText, formatter: "{value}%" } },
      series: [
        {
          ...line("Food inflation", s.FOOD_INF_YOY, C.food, 2.5, true),
          markPoint: {
            symbol: "circle",
            symbolSize: 9,
            itemStyle: { color: C.food, borderColor: C.surface, borderWidth: 2 },
            label: { show: true, position: "top", color: C.paper, fontFamily: baseText.fontFamily, fontSize: 11, formatter: `Peak ${peak.value.toFixed(1)}%` },
            data: [{ name: "peak", coord: [monthLabel(peak.date), peak.value] }],
          },
        },
        line("Rupee depreciation vs USD", s.EXR_DEP_YOY, C.exr),
        line("World food prices (FAO)", s.GFOOD_YOY, C.world, 1.5),
      ],
    };
  }, [dates, s, peak]);
  return <EChart option={option} height={420} ariaLabel="Line chart: year-on-year food inflation in Pakistan, rupee depreciation against the US dollar, and FAO world food price inflation, 2015 to 2025." />;
}

const EXPLORER_VARS: { key: string; label: string; unit: string }[] = [
  { key: "FOODCPI", label: "Food CPI", unit: "Index 2015-16=100" },
  { key: "EXR", label: "PKR per USD", unit: "Rupees" },
  { key: "GFOOD", label: "FAO world food", unit: "Index 2014-16=100" },
  { key: "TRANSCPI", label: "Transport CPI", unit: "Index 2015-16=100" },
  { key: "CPI", label: "Headline CPI", unit: "Index 2015-16=100" },
  { key: "HOUSCPI", label: "Housing & utilities CPI", unit: "Index 2015-16=100" },
  { key: "BRENT", label: "Brent crude", unit: "USD per barrel" },
];
const YOY_KEY: Record<string, string> = { FOODCPI: "FOOD_INF_YOY", EXR: "EXR_DEP_YOY", GFOOD: "GFOOD_YOY", TRANSCPI: "TRANS_YOY", CPI: "CPI_INF_YOY" };

/** Data Room explorer. Rebased and YoY modes compare several variables on one common axis;
 *  'Levels' mode shows one variable at a time so different units are never forced onto one axis. */
export function SeriesExplorer({ dates, s, rebased }: { dates: string[]; s: Series; rebased: Record<string, number[]> }) {
  const [mode, setMode] = useState<"rebased" | "yoy" | "levels">("rebased");
  const [picked, setPicked] = useState<string[]>(["FOODCPI", "EXR", "GFOOD", "TRANSCPI"]);
  const [single, setSingle] = useState("FOODCPI");

  const available = mode === "rebased" ? EXPLORER_VARS.filter((v) => rebased[v.key]) : mode === "yoy" ? EXPLORER_VARS.filter((v) => YOY_KEY[v.key]) : EXPLORER_VARS;
  const shown = mode === "levels" ? [single] : picked.filter((p) => available.some((a) => a.key === p));

  const option = useMemo<EChartsOption>(() => {
    const x = dates.map(monthLabel);
    const series = shown.map((k) => {
      const meta = EXPLORER_VARS.find((v) => v.key === k)!;
      const data = mode === "rebased" ? rebased[k] : mode === "yoy" ? s[YOY_KEY[k]] : s[k];
      return {
        name: meta.label,
        type: "line" as const,
        data,
        showSymbol: false,
        symbolSize: 8,
        lineStyle: { width: k === "FOODCPI" ? 2.5 : 2, color: SERIES_COLOR[k] },
        itemStyle: { color: SERIES_COLOR[k] },
        emphasis: { focus: "series" as const },
        endLabel: shown.length <= 4 ? { show: true, color: C.dim, fontFamily: baseText.fontFamily, fontSize: 10, formatter: meta.label } : undefined,
      };
    });
    const unit = mode === "rebased" ? "Index, Jan 2015 = 100" : mode === "yoy" ? "% change on a year earlier" : EXPLORER_VARS.find((v) => v.key === single)!.unit;
    return {
      grid: { left: 56, right: shown.length <= 4 && mode !== "levels" ? 130 : 24, top: 76, bottom: 70 },
      legend: { top: 0, left: 0, textStyle: { ...baseText, color: C.dim }, icon: "rect", itemWidth: 14, itemHeight: 2 },
      tooltip: { ...tooltipBase, trigger: "axis", axisPointer: { type: "line", lineStyle: { color: C.axis } }, valueFormatter: (v) => (typeof v === "number" ? v.toFixed(mode === "yoy" ? 1 : 2) : "—") },
      dataZoom: [{ type: "inside" }, { type: "slider", height: 18, bottom: 10, borderColor: C.axis, textStyle: baseText, fillerColor: "rgba(201,162,74,0.15)", handleStyle: { color: C.gold } }],
      xAxis: { type: "category", data: x, boundaryGap: false, ...axisCommon({ splitLine: { show: false } }), axisLabel: { ...baseText, interval: 11, formatter: (v: string) => v.slice(-4) } },
      yAxis: { type: "value", name: unit, scale: mode !== "yoy", ...axisCommon() },
      series,
    };
  }, [dates, s, rebased, mode, shown, single]);

  return (
    <div>
      <div className="mb-5 flex flex-wrap items-center gap-4">
        <Segmented
          label="Display mode"
          value={mode}
          onChange={setMode}
          options={[
            { value: "rebased", label: "Rebased 100" },
            { value: "yoy", label: "YoY %" },
            { value: "levels", label: "Levels" },
          ]}
        />
        <div className="flex flex-wrap gap-2" role="group" aria-label="Variables">
          {available.map((v) => {
            const on = mode === "levels" ? single === v.key : picked.includes(v.key);
            return (
              <button
                key={v.key}
                type="button"
                aria-pressed={on}
                onClick={() =>
                  mode === "levels" ? setSingle(v.key) : setPicked((p) => (p.includes(v.key) ? p.filter((x) => x !== v.key) : [...p, v.key]))
                }
                className={`inline-flex items-center gap-2 rounded-full border px-3 py-1 font-mono text-[0.68rem] transition-colors ${
                  on ? "border-paper/40 text-paper" : "border-line text-faint hover:text-paper-dim"
                }`}
              >
                <span className="h-2 w-2 rounded-full" style={{ background: on ? SERIES_COLOR[v.key] : "transparent", border: `1px solid ${SERIES_COLOR[v.key]}` }} />
                {v.label}
              </button>
            );
          })}
        </div>
      </div>
      <EChart option={option} height={440} ariaLabel={`Time-series explorer showing ${shown.join(", ")} in ${mode} mode, monthly 2015 to 2025.`} />
      <p className="mt-2 font-mono text-[0.65rem] text-faint">
        {mode === "levels" ? "Levels mode shows one variable at a time — different units never share an axis." : "Drag the slider or scroll inside the chart to zoom."}
      </p>
    </div>
  );
}
