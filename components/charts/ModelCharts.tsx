"use client";

import type { EChartsOption } from "echarts";
import { useMemo, useState } from "react";

import { Segmented } from "@/components/ui/Segmented";
import { fmt, monthLabel } from "@/lib/format";
import type { Multipliers, RobustRow, Stability } from "@/lib/types";

import { EChart } from "./EChart";
import { axisCommon, baseText, C, tooltipBase } from "./theme";

/* ------------------------------------------------------------------------------------------------ */
/* Band helper: a confidence band drawn as a stacked transparent base + filled width.               */
function band(name: string, lo: number[], hi: number[], color: string, stack: string) {
  return [
    { name: `${name} lower`, type: "line" as const, data: lo, stack, stackStrategy: "all" as const, lineStyle: { opacity: 0 }, symbol: "none", tooltip: { show: false }, silent: true },
    {
      name: `${name} 95% band`,
      type: "line" as const,
      data: hi.map((h, i) => h - lo[i]),
      stack,
      stackStrategy: "all" as const,
      lineStyle: { opacity: 0 },
      symbol: "none",
      areaStyle: { color, opacity: 0.2 },
      tooltip: { show: false },
      silent: true,
    },
  ];
}

export function MultiplierChart({ m }: { m: Multipliers }) {
  const [view, setView] = useState<"both" | "dep" | "app" | "asym">("both");
  const [h, setH] = useState(12);
  const appr = useMemo(() => m.neg.map((v) => -v), [m.neg]);
  const apprLo = useMemo(() => m.neg_hi95.map((v) => -v), [m.neg_hi95]);
  const apprHi = useMemo(() => m.neg_lo95.map((v) => -v), [m.neg_lo95]);

  const option = useMemo<EChartsOption>(() => {
    const x = m.horizon.map(String);
    const s: EChartsOption["series"] = [];
    if (view === "both" || view === "dep") {
      s.push(...band("Depreciation", m.pos_lo95, m.pos_hi95, C.rise, "dep"));
      s.push({ name: "Response to a 1% depreciation", type: "line", data: m.pos, symbol: "none", lineStyle: { width: 2.5, color: C.rise }, itemStyle: { color: C.rise } });
    }
    if (view === "both" || view === "app") {
      s.push(...band("Appreciation", apprLo, apprHi, C.fall, "app"));
      s.push({ name: "Response to a 1% appreciation", type: "line", data: appr, symbol: "none", lineStyle: { width: 2.5, color: C.fall }, itemStyle: { color: C.fall } });
    }
    if (view === "asym") {
      s.push(...band("Asymmetry", m.asym_lo95, m.asym_hi95, C.gold, "asym"));
      s.push({ name: "Asymmetry m⁺ − m⁻", type: "line", data: m.asym, symbol: "none", lineStyle: { width: 2.5, color: C.gold }, itemStyle: { color: C.gold } });
    }
    (s as { markLine?: unknown }[])[s.length - 1].markLine = {
      symbol: "none",
      silent: true,
      label: { show: true, color: C.dim, fontFamily: baseText.fontFamily, fontSize: 10, formatter: `h = ${h}` },
      lineStyle: { color: C.dim, type: "dashed" },
      data: [{ xAxis: String(h) }],
    };
    return {
      grid: { left: 52, right: 24, top: 84, bottom: 48 },
      legend: { top: 0, left: 0, textStyle: { ...baseText, color: C.dim }, itemWidth: 14, itemHeight: 2, data: (s as { name: string }[]).map((x) => x.name).filter((n) => !n.includes("band") && !n.includes("lower")) },
      tooltip: { ...tooltipBase, trigger: "axis", valueFormatter: (v) => (typeof v === "number" ? `${v >= 0 ? "+" : ""}${v.toFixed(3)}%` : "—") },
      xAxis: { type: "category", data: x, name: "Months after the change", nameLocation: "middle", nameGap: 30, boundaryGap: false, ...axisCommon({ splitLine: { show: false } }), axisLabel: { ...baseText, interval: 5 } },
      yAxis: { type: "value", name: "Cumulative % change in food CPI", ...axisCommon() },
      series: s.concat([{ type: "line", data: [], markLine: { symbol: "none", silent: true, lineStyle: { color: C.axis }, label: { show: false }, data: [{ yAxis: 0 }] } }]),
    };
  }, [m, view, h, appr, apprLo, apprHi]);

  const row = {
    dep: m.pos[h],
    depLo: m.pos_lo95[h],
    depHi: m.pos_hi95[h],
    app: appr[h],
    appLo: apprLo[h],
    appHi: apprHi[h],
    asym: m.asym[h],
    aLo: m.asym_lo95[h],
    aHi: m.asym_hi95[h],
  };
  const asymSig = row.aLo > 0 || row.aHi < 0;

  return (
    <div>
      <div className="mb-5 flex flex-wrap items-center justify-between gap-4">
        <Segmented
          label="Multiplier view"
          value={view}
          onChange={setView}
          options={[
            { value: "both", label: "Both" },
            { value: "dep", label: "Depreciation" },
            { value: "app", label: "Appreciation" },
            { value: "asym", label: "Asymmetry" },
          ]}
        />
        <label className="flex items-center gap-3 font-mono text-[0.7rem] uppercase tracking-[0.12em] text-muted">
          Horizon
          <input
            type="range"
            min={0}
            max={m.horizon.length - 1}
            value={h}
            onChange={(e) => setH(Number(e.target.value))}
            className="w-40 accent-[#c9a24a]"
            aria-label="Horizon in months"
          />
          <span className="num w-16 text-paper">{h} mo</span>
        </label>
      </div>
      <EChart option={option} height={440} ariaLabel="Cumulative dynamic multipliers: response of food CPI to a 1% depreciation and to a 1% appreciation of the rupee, with 95% bands, over 36 months." />
      <div className="mt-6 grid gap-px overflow-hidden rounded-sm border border-line bg-line sm:grid-cols-3">
        {[
          { k: "1% depreciation", v: row.dep, lo: row.depLo, hi: row.depHi, c: "text-rise" },
          { k: "1% appreciation", v: row.app, lo: row.appLo, hi: row.appHi, c: "text-fall" },
          { k: "Asymmetry (m⁺ − m⁻)", v: row.asym, lo: row.aLo, hi: row.aHi, c: "text-gold" },
        ].map((c) => (
          <div key={c.k} className="bg-graphite p-5">
            <div className="font-mono text-[0.66rem] uppercase tracking-[0.14em] text-muted">
              {c.k} · after {h} months
            </div>
            <div className={`num mt-2 text-3xl ${c.c}`}>
              {c.v >= 0 ? "+" : ""}
              {fmt(c.v, 3)}%
            </div>
            <div className="num mt-1 text-[0.72rem] text-faint">
              95% band [{fmt(c.lo, 2)}, {fmt(c.hi, 2)}]
            </div>
          </div>
        ))}
      </div>
      <p className="mt-4 text-sm leading-relaxed text-paper-dim">
        At {h} months the asymmetry band {asymSig ? "excludes" : "includes"} zero:{" "}
        {asymSig
          ? "the response to depreciation and appreciation differs significantly at this horizon."
          : "we cannot statistically distinguish the depreciation and appreciation responses at this horizon."}
      </p>
    </div>
  );
}

/* ------------------------------------------------------------------------------------------------ */
export function PartialSumsChart({ dates, exr, pos, neg }: { dates: string[]; exr: number[]; pos: number[]; neg: number[] }) {
  const option = useMemo<EChartsOption>(() => {
    const x = dates.map(monthLabel);
    const l0 = Math.log(exr[0]);
    return {
      grid: { left: 52, right: 70, top: 84, bottom: 40 },
      legend: { top: 0, left: 0, textStyle: { ...baseText, color: C.dim }, itemWidth: 14, itemHeight: 2 },
      tooltip: { ...tooltipBase, trigger: "axis", valueFormatter: (v) => (typeof v === "number" ? v.toFixed(3) : "—") },
      xAxis: { type: "category", data: x, boundaryGap: false, ...axisCommon({ splitLine: { show: false } }), axisLabel: { ...baseText, interval: 11, formatter: (v: string) => v.slice(-4) } },
      yAxis: { type: "value", name: "Log points since Jan 2015", ...axisCommon() },
      series: [
        { name: "ln EXR − ln EXR₀ (net)", type: "line", data: exr.map((v) => Math.log(v) - l0), showSymbol: false, lineStyle: { color: C.dim, width: 1.5, type: "dashed" }, itemStyle: { color: C.dim }, endLabel: { show: true, color: C.dim, fontSize: 10, fontFamily: baseText.fontFamily, formatter: "Net change" } },
        { name: "EXR⁺ cumulative depreciation", type: "line", data: pos, showSymbol: false, lineStyle: { color: C.rise, width: 2.5 }, itemStyle: { color: C.rise }, areaStyle: { color: C.rise, opacity: 0.08 }, endLabel: { show: true, color: C.dim, fontSize: 10, fontFamily: baseText.fontFamily, formatter: "EXR⁺" } },
        { name: "EXR⁻ cumulative appreciation", type: "line", data: neg, showSymbol: false, lineStyle: { color: C.fall, width: 2.5 }, itemStyle: { color: C.fall }, areaStyle: { color: C.fall, opacity: 0.08 }, endLabel: { show: true, color: C.dim, fontSize: 10, fontFamily: baseText.fontFamily, formatter: "EXR⁻" } },
      ],
    };
  }, [dates, exr, pos, neg]);
  return <EChart option={option} height={380} ariaLabel="Decomposition of the log exchange rate into cumulative depreciation (positive partial sum) and cumulative appreciation (negative partial sum)." />;
}

/* ------------------------------------------------------------------------------------------------ */
export function StabilityChart({ st, label }: { st: Stability; label: string }) {
  const [which, setWhich] = useState<"cusum" | "cusumsq">("cusum");
  const option = useMemo<EChartsOption>(() => {
    const x = st.dates.map(monthLabel);
    const cs = which === "cusum";
    const lo = cs ? st.cusum_lo : st.cusumsq_expected.map((e) => e - st.cusumsq_c0);
    const hi = cs ? st.cusum_hi : st.cusumsq_expected.map((e) => e + st.cusumsq_c0);
    const val = cs ? st.cusum : st.cusumsq;
    return {
      grid: { left: 48, right: 20, top: 36, bottom: 36 },
      legend: { top: 0, left: 0, textStyle: { ...baseText, color: C.dim }, itemWidth: 14, itemHeight: 2 },
      tooltip: { ...tooltipBase, trigger: "axis", valueFormatter: (v) => (typeof v === "number" ? v.toFixed(3) : "—") },
      xAxis: { type: "category", data: x, boundaryGap: false, ...axisCommon({ splitLine: { show: false } }), axisLabel: { ...baseText, interval: 11, formatter: (v: string) => v.slice(-4) } },
      yAxis: { type: "value", ...axisCommon() },
      series: [
        { name: cs ? "CUSUM" : "CUSUM of squares", type: "line", data: val, showSymbol: false, lineStyle: { color: C.paper, width: 2 }, itemStyle: { color: C.paper } },
        { name: "5% significance bounds", type: "line", data: hi, showSymbol: false, lineStyle: { color: C.rise, width: 1.2, type: "dashed" }, itemStyle: { color: C.rise } },
        { name: "lower", type: "line", data: lo, showSymbol: false, lineStyle: { color: C.rise, width: 1.2, type: "dashed" }, tooltip: { show: false } },
      ],
    };
  }, [st, which]);
  const ok = which === "cusum" ? st.cusum_within_bounds : st.cusumsq_within_bounds;
  return (
    <div>
      <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
        <Segmented label="Stability test" value={which} onChange={setWhich} options={[{ value: "cusum", label: "CUSUM" }, { value: "cusumsq", label: "CUSUM²" }]} />
        <span className={`font-mono text-[0.7rem] uppercase tracking-[0.12em] ${ok ? "text-fall" : "text-rise"}`}>
          {ok ? "Within 5% bounds — stable" : "Crosses 5% bounds — instability"}
        </span>
      </div>
      <EChart option={option} height={300} ariaLabel={`${which === "cusum" ? "CUSUM" : "CUSUM of squares"} stability test for the ${label}, with 5% significance bounds.`} />
    </div>
  );
}

/* ------------------------------------------------------------------------------------------------ */
export function ForestChart({ rows }: { rows: RobustRow[] }) {
  const ok = rows.filter((r) => r.long_run && r.long_run.LEXR_POS);
  const option = useMemo<EChartsOption>(() => {
    const cats = ok.map((r) => r.id);
    const pt = (r: RobustRow, k: "LEXR_POS" | "LEXR_NEG") => r.long_run[k];
    const mk = (k: "LEXR_POS" | "LEXR_NEG", color: string, offset: number) => ({
      name: k === "LEXR_POS" ? "Depreciation L⁺" : "Appreciation L⁻",
      type: "scatter" as const,
      data: ok.map((r, i) => ({
        value: [pt(r, k).coef, i + offset],
        name: `${r.label}|${pt(r, k).p}`,
        itemStyle: { color: pt(r, k).p < 0.05 ? color : "transparent", borderColor: color, borderWidth: 2 },
      })),
      symbolSize: 11,
      itemStyle: { color },
    });
    return {
      grid: { left: 110, right: 24, top: 36, bottom: 44 },
      legend: { top: 0, left: 0, textStyle: { ...baseText, color: C.dim } },
      tooltip: {
        ...tooltipBase,
        formatter: (p: unknown) => {
          const d = (p as { data: { value: number[]; name: string } }).data;
          const sn = (p as { seriesName: string }).seriesName;
          const [lab, pv] = d.name.split("|");
          return `<div style="max-width:260px;white-space:normal">${lab}</div><b>${sn}</b>: <span style="font-family:monospace">${d.value[0].toFixed(3)} (p = ${Number(pv).toFixed(3)})</span>`;
        },
      },
      xAxis: { type: "value", min: (v: { min: number }) => Math.min(0, Math.floor(v.min * 10) / 10), name: "Long-run elasticity of food CPI", nameLocation: "middle", nameGap: 28, ...axisCommon({ axisLine: { onZero: false, lineStyle: { color: C.axis } } }) },
      yAxis: { type: "value", min: -1, max: ok.length, inverse: true, interval: 1, ...axisCommon({ splitLine: { show: false } }), axisLabel: { ...baseText, formatter: (v: number) => cats[v] ?? "" } },
      series: [mk("LEXR_POS", C.rise, -0.15), mk("LEXR_NEG", C.fall, 0.15)],
    };
  }, [ok]);
  return <EChart option={option} height={Math.max(380, ok.length * 34 + 90)} ariaLabel="Forest plot of long-run depreciation and appreciation elasticities across robustness specifications; filled markers are significant at 5%." />;
}

/* ------------------------------------------------------------------------------------------------ */
export function EcmDecay({ rho, label }: { rho: number; label: string }) {
  const option = useMemo<EChartsOption>(() => {
    const H = 36;
    const d = Array.from({ length: H + 1 }, (_, h) => 100 * Math.pow(1 + rho, h));
    const half = Math.log(0.5) / Math.log(1 + rho);
    return {
      grid: { left: 48, right: 20, top: 24, bottom: 44 },
      tooltip: { ...tooltipBase, trigger: "axis", valueFormatter: (v) => (typeof v === "number" ? `${v.toFixed(1)}% of the gap remains` : "") },
      xAxis: { type: "category", data: d.map((_, i) => String(i)), name: "Months after a shock", nameLocation: "middle", nameGap: 28, boundaryGap: false, ...axisCommon({ splitLine: { show: false } }), axisLabel: { ...baseText, interval: 5 } },
      yAxis: { type: "value", max: 100, name: "% of disequilibrium remaining", ...axisCommon() },
      series: [{
        name: label,
        type: "line",
        data: d,
        showSymbol: false,
        lineStyle: { color: C.gold, width: 2.5 },
        areaStyle: { color: C.gold, opacity: 0.1 },
        markLine: { symbol: "none", label: { color: C.dim, fontFamily: baseText.fontFamily, fontSize: 10, formatter: `half-life ≈ ${half.toFixed(1)} months` }, lineStyle: { color: C.dim, type: "dashed" }, data: [{ xAxis: String(Math.round(half)) }] },
      }],
    };
  }, [rho, label]);
  return <EChart option={option} height={280} ariaLabel={`Share of a deviation from the long-run equilibrium remaining after each month, given an adjustment coefficient of ${rho.toFixed(3)}.`} />;
}

/* ------------------------------------------------------------------------------------------------ */
export function FitChart({ dates, actual, fitted }: { dates: string[]; actual: number[]; fitted: number[] }) {
  const option = useMemo<EChartsOption>(() => ({
    grid: { left: 52, right: 20, top: 64, bottom: 36 },
    legend: { top: 0, left: 0, textStyle: { ...baseText, color: C.dim }, itemWidth: 14, itemHeight: 2 },
    tooltip: { ...tooltipBase, trigger: "axis", valueFormatter: (v) => (typeof v === "number" ? v.toFixed(4) : "—") },
    xAxis: { type: "category", data: dates.map(monthLabel), boundaryGap: false, ...axisCommon({ splitLine: { show: false } }), axisLabel: { ...baseText, interval: 11, formatter: (v: string) => v.slice(-4) } },
    yAxis: { type: "value", scale: true, name: "ln food CPI", ...axisCommon() },
    series: [
      { name: "Actual", type: "line", data: actual, showSymbol: false, lineStyle: { color: C.paper, width: 2 }, itemStyle: { color: C.paper } },
      { name: "NARDL fitted", type: "line", data: fitted, showSymbol: false, lineStyle: { color: C.gold, width: 1.5, type: "dashed" }, itemStyle: { color: C.gold } },
    ],
  }), [dates, actual, fitted]);
  return <EChart option={option} height={300} ariaLabel="Actual and fitted log food CPI from the NARDL model." />;
}
