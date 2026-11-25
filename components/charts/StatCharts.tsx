"use client";

import type { EChartsOption } from "echarts";
import { useMemo, useState } from "react";

import { Segmented } from "@/components/ui/Segmented";
import type { Matrix } from "@/lib/types";

import { EChart } from "./EChart";
import { axisCommon, baseText, C, tooltipBase } from "./theme";

const LBL: Record<string, string> = {
  LFOODCPI: "Food CPI",
  LEXR: "PKR/USD",
  LGFOOD: "FAO food",
  LTRANSCPI: "Transport CPI",
  FOOD_INF_YOY: "Food infl.",
  EXR_DEP_YOY: "Depreciation",
  GFOOD_YOY: "FAO food",
  TRANS_YOY: "Transport",
};

export function CorrelationHeatmap({ levels, diffs, yoy }: { levels: Matrix; diffs: Matrix; yoy: Matrix }) {
  const [mode, setMode] = useState<"levels" | "yoy" | "diffs">("levels");
  const m = mode === "levels" ? levels : mode === "yoy" ? yoy : diffs;
  const option = useMemo<EChartsOption>(() => {
    const labels = m.variables.map((v) => LBL[v] ?? v);
    const data: [number, number, number][] = [];
    m.matrix.forEach((row, i) => row.forEach((v, j) => data.push([j, i, v])));
    return {
      grid: { left: 100, right: 20, top: 10, bottom: 70 },
      tooltip: { ...tooltipBase, formatter: (p: unknown) => {
        const d = (p as { data: [number, number, number] }).data;
        return `${labels[d[1]]} × ${labels[d[0]]}<br/><b style="font-family:monospace">r = ${d[2].toFixed(3)}</b>`;
      } },
      xAxis: { type: "category", data: labels, ...axisCommon({ splitLine: { show: false } }), axisLabel: { ...baseText, rotate: 30 } },
      yAxis: { type: "category", data: labels, inverse: true, ...axisCommon({ splitLine: { show: false } }) },
      visualMap: { min: -1, max: 1, show: false, inRange: { color: ["#2f6fb8", "#383838", "#c8403f"] } },
      series: [{
        type: "heatmap",
        data,
        itemStyle: { borderColor: C.surface, borderWidth: 2 },
        label: { show: true, color: C.paper, fontFamily: baseText.fontFamily, fontSize: 12, formatter: (p: unknown) => (p as { data: number[] }).data[2].toFixed(2) },
        emphasis: { itemStyle: { borderColor: C.gold, borderWidth: 2 } },
      }],
    };
  }, [m]);
  return (
    <div>
      <div className="mb-4">
        <Segmented label="Correlation basis" value={mode} onChange={setMode} options={[
          { value: "levels", label: "Log levels" },
          { value: "yoy", label: "YoY rates" },
          { value: "diffs", label: "Monthly Δlog" },
        ]} />
      </div>
      <EChart option={option} height={360} ariaLabel={`Correlation matrix of ${mode}: ${m.variables.join(", ")}.`} />
      <p className="mt-2 text-sm text-paper-dim">
        {mode === "levels"
          ? "Trending levels correlate almost perfectly — a warning, not evidence: any two upward-trending series do this (Granger & Newbold, 1974)."
          : mode === "yoy"
            ? "Annual rates remove the common trend; the exchange rate still co-moves strongly with food inflation."
            : "Month-to-month changes are noisy; contemporaneous correlations are small because pass-through takes time — which is why the models use lags."}
      </p>
    </div>
  );
}

export function InflationHistogram({ values, dates, outliers }: { values: number[]; dates: string[]; outliers: { date: string; food_inf_mom: number }[] }) {
  const option = useMemo<EChartsOption>(() => {
    const w = 1;
    const lo = Math.floor(Math.min(...values));
    const hi = Math.ceil(Math.max(...values));
    const bins: { x0: number; n: number; out: number }[] = [];
    for (let b = lo; b < hi; b += w) bins.push({ x0: b, n: 0, out: 0 });
    const outSet = new Set(outliers.map((o) => o.date));
    values.forEach((v, i) => {
      const k = Math.min(bins.length - 1, Math.floor((v - lo) / w));
      bins[k].n += 1;
      if (outSet.has(dates[i])) bins[k].out += 1;
    });
    return {
      grid: { left: 44, right: 16, top: 24, bottom: 48 },
      tooltip: { ...tooltipBase, trigger: "axis", axisPointer: { type: "shadow" } },
      xAxis: { type: "category", data: bins.map((b) => `${b.x0}…${b.x0 + w}%`), name: "Monthly food inflation", nameLocation: "middle", nameGap: 32, ...axisCommon({ splitLine: { show: false } }) },
      yAxis: { type: "value", name: "Months", ...axisCommon(), minInterval: 1 },
      series: [
        { name: "Months", type: "bar", stack: "a", data: bins.map((b) => b.n - b.out), itemStyle: { color: C.food, borderRadius: [0, 0, 0, 0] }, barCategoryGap: "8%" },
        { name: "Outlier months (|robust z| > 2.5)", type: "bar", stack: "a", data: bins.map((b) => b.out), itemStyle: { color: C.gold, borderRadius: [3, 3, 0, 0] } },
      ],
      legend: { bottom: 0, right: 0, textStyle: { ...baseText, color: C.dim }, itemWidth: 10, itemHeight: 10 },
    };
  }, [values, dates, outliers]);
  return <EChart option={option} height={320} ariaLabel="Histogram of monthly food inflation rates, 2015 to 2025, with outlier months highlighted." />;
}

export function AnnualBars({ years, food, exr, world }: { years: string[]; food: number[]; exr: number[]; world: number[] }) {
  const option = useMemo<EChartsOption>(() => ({
    grid: { left: 48, right: 16, top: 40, bottom: 36 },
    legend: { top: 0, left: 0, textStyle: { ...baseText, color: C.dim }, itemWidth: 10, itemHeight: 10 },
    tooltip: { ...tooltipBase, trigger: "axis", axisPointer: { type: "shadow" }, valueFormatter: (v) => (typeof v === "number" ? `${v.toFixed(1)}%` : "—") },
    xAxis: { type: "category", data: years, ...axisCommon({ splitLine: { show: false } }) },
    yAxis: { type: "value", ...axisCommon(), axisLabel: { ...baseText, formatter: "{value}%" } },
    series: [
      { name: "Food CPI", type: "bar", data: food, itemStyle: { color: C.food, borderRadius: 3 }, barGap: "12%" },
      { name: "PKR per USD", type: "bar", data: exr, itemStyle: { color: C.exr, borderRadius: 3 } },
      { name: "FAO world food", type: "bar", data: world, itemStyle: { color: C.world, borderRadius: 3 } },
    ],
  }), [years, food, exr, world]);
  return <EChart option={option} height={340} ariaLabel="Grouped bar chart of annual average growth in food CPI, the PKR per USD rate and FAO world food prices, 2016 to 2025." />;
}
