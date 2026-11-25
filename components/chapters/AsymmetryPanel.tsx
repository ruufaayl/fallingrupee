"use client";

import { useState } from "react";

import { Segmented } from "@/components/ui/Segmented";
import { fmt, fmtP } from "@/lib/format";

interface Est { coef: number; lo: number; hi: number; p: number }

export function AsymmetryPanel({
  sr,
  lr,
  srTest,
  lrTest,
}: {
  sr: { dep: Est; app: Est };
  lr: { dep: Est; app: Est };
  srTest: { stat: string; p: number };
  lrTest: { stat: string; p: number };
}) {
  const [horizon, setHorizon] = useState<"lr" | "sr">("lr");
  const d = horizon === "lr" ? lr : sr;
  const t = horizon === "lr" ? lrTest : srTest;
  const all = [d.dep.lo, d.dep.hi, d.app.lo, d.app.hi, 0];
  const min = Math.min(...all);
  const max = Math.max(...all);
  const pad = (max - min) * 0.08;
  const sc = (v: number) => ((v - (min - pad)) / (max - min + 2 * pad)) * 100;
  const rows = [
    { k: "Depreciation", e: d.dep, c: "#e5484d", note: horizon === "lr" ? "L⁺ — response to a permanent 1% depreciation" : "β⁺₀ — within-month response to depreciation" },
    { k: "Appreciation", e: d.app, c: "#00a888", note: horizon === "lr" ? "L⁻ — coefficient on cumulative appreciation" : "β⁻₀ — within-month coefficient on appreciation" },
  ];
  const rejected = t.p < 0.05;

  return (
    <div>
      <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <Segmented label="Horizon" value={horizon} onChange={setHorizon} options={[{ value: "lr", label: "Long run" }, { value: "sr", label: "Short run (impact)" }]} />
        <span className={`font-mono text-[0.7rem] uppercase tracking-[0.12em] ${rejected ? "text-gold" : "text-paper-dim"}`}>
          Symmetry {rejected ? "rejected" : "not rejected"} · {t.stat}, p = {fmtP(t.p)}
        </span>
      </div>
      <div className="space-y-8">
        {rows.map((r) => (
          <div key={r.k}>
            <div className="flex flex-wrap items-baseline justify-between gap-2">
              <span className="font-serif text-xl text-paper">{r.k}</span>
              <span className="num text-sm text-paper-dim">
                {fmt(r.e.coef, 3)} <span className="text-faint">[{fmt(r.e.lo, 2)}, {fmt(r.e.hi, 2)}] · p = {fmtP(r.e.p)}</span>
              </span>
            </div>
            <div className="relative mt-3 h-8" role="img" aria-label={`${r.k}: estimate ${fmt(r.e.coef, 3)}, 95% interval ${fmt(r.e.lo, 2)} to ${fmt(r.e.hi, 2)}`}>
              <div className="absolute inset-y-0 w-px bg-line-strong" style={{ left: `${sc(0)}%` }} />
              <div className="absolute top-1/2 h-[2px] -translate-y-1/2 transition-all duration-500" style={{ left: `${sc(r.e.lo)}%`, width: `${sc(r.e.hi) - sc(r.e.lo)}%`, background: r.c, opacity: 0.55 }} />
              <div
                className="absolute top-1/2 h-4 w-4 -translate-x-1/2 -translate-y-1/2 rounded-full border-2 transition-all duration-500"
                style={{ left: `${sc(r.e.coef)}%`, borderColor: r.c, background: r.e.p < 0.05 ? r.c : "#0b0c0e" }}
              />
            </div>
            <p className="mt-1 font-mono text-[0.64rem] text-faint">{r.note}{r.e.p < 0.05 ? " · significant at 5%" : " · not significant at 5%"}</p>
          </div>
        ))}
        <div className="flex justify-between font-mono text-[0.62rem] text-faint">
          <span>{fmt(min - pad, 2)}</span>
          <span>0</span>
          <span>{fmt(max + pad, 2)}</span>
        </div>
      </div>
      <p className="mt-6 text-sm leading-relaxed text-paper-dim">
        {horizon === "lr"
          ? "Because EXR⁻ falls when the rupee appreciates, a positive L⁻ means appreciation lowers food prices. Equal L⁺ and L⁻ would mean symmetric pass-through."
          : "Impact coefficients are the within-month effects in the levels ARDL. A negative β⁻₀ means that in the month the rupee appreciates (EXR⁻ falls), food prices tend to rise rather than fall."}
      </p>
    </div>
  );
}
