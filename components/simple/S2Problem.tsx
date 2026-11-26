import { CountUp } from "@/components/animations/CountUp";
import { InflationChart } from "@/components/charts/TimeCharts";
import { Chapter, Panel, SourceNote, SubHead } from "@/components/ui/Chapter";
import { findings, timeseries } from "@/lib/registry";
import { monthLabel } from "@/lib/format";
import { simple } from "@/lib/simple";

export function S2Problem() {
  const h = findings.headline_numbers;
  return (
    <Chapter id="problem" n={2} kicker="Problem Statement" title={<>Food nearly tripled in price. Why?</>} intro={<p>{simple.problem}</p>}>
      <div className="grid gap-px overflow-hidden rounded-sm border border-line bg-line md:grid-cols-3">
        {[
          { v: h.food_cpi_change_pct, k: "Food prices in Pakistan, 2015 → 2025", c: "text-s-food" },
          { v: h.exr_change_pct, k: "Rupees per US dollar, 2015 → 2025", c: "text-s-exr" },
          { v: h.gfood_change_pct, k: "World food prices, 2015 → 2025", c: "text-s-world" },
        ].map((s) => (
          <div key={s.k} className="bg-graphite p-6 sm:p-8">
            <CountUp value={s.v} prefix="+" suffix="%" className={`block text-5xl ${s.c}`} />
            <p className="mt-3 font-mono text-[0.68rem] uppercase tracking-[0.12em] text-muted">{s.k}</p>
          </div>
        ))}
      </div>

      <div className="mt-14 rounded-sm border border-gold/50 bg-gold/5 p-6 sm:p-10">
        <div className="kicker">Research question</div>
        <p className="mt-4 font-serif text-2xl leading-snug text-paper sm:text-3xl">{simple.question}</p>
      </div>

      <div className="mt-16">
        <SubHead k="Graph 1">Food inflation followed the rupee, not world prices</SubHead>
        <Panel>
          <InflationChart dates={timeseries.dates} s={timeseries.series} peak={{ date: h.food_infl_peak_date, value: h.food_infl_peak }} />
          <SourceNote>
            Year-on-year % change. Food inflation peaked at {h.food_infl_peak.toFixed(1)}% in {monthLabel(h.food_infl_peak_date)}. Sources: PBS, World Bank,
            FAO.
          </SourceNote>
        </Panel>
      </div>
    </Chapter>
  );
}
