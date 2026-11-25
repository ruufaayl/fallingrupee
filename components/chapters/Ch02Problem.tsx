import { CountUp } from "@/components/animations/CountUp";
import { Reveal } from "@/components/animations/Reveal";
import { InflationChart } from "@/components/charts/TimeCharts";
import { Chapter, Panel, SourceNote, SubHead } from "@/components/ui/Chapter";
import { descriptives, findings, timeseries } from "@/lib/registry";
import { fmt, monthLabel } from "@/lib/format";

export function Ch02Problem() {
  const h = findings.headline_numbers;
  const food = timeseries.series.FOODCPI as number[];
  const cost = (1000 * food[food.length - 1]) / food[0];
  const dep = descriptives.largest_depreciation_months[0];
  const er = descriptives.exchange_rate_months;
  const yoy = descriptives.variables.find((v) => v.variable === "FOOD_INF_YOY")!;

  const concepts = [
    {
      t: "Food inflation",
      d: "The rate at which the prices of the food basket rise. In Pakistan’s national CPI, food and non-alcoholic beverages carry a weight of 34.58% — over a third of the typical household budget.",
      s: "PBS, Monthly Review on Price Indices, Table 1 (base 2015-16).",
    },
    {
      t: "Purchasing power",
      d: `What a rupee can buy. Food that cost Rs 1,000 in January 2015 cost about Rs ${Math.round(cost).toLocaleString("en-GB")} in December 2025 — the same rupee buys roughly a third as much food.`,
      s: "Computed from the national food CPI, Jan 2015 → Dec 2025.",
    },
    {
      t: "Cost of living",
      d: `Average food inflation over 2015–2025 was ${fmt(yoy.mean, 1)}% a year, but averages hide the shock: the year-on-year rate swung from ${fmt(yoy.min, 1)}% (${monthLabel(yoy.min_date)}) to ${fmt(yoy.max, 1)}% (${monthLabel(yoy.max_date)}).`,
      s: "Descriptive statistics, Chapter 05.",
    },
    {
      t: "Exchange-rate depreciation",
      d: `A rise in rupees per US dollar. The rupee depreciated in ${er.depreciating} of 131 months and appreciated in ${er.appreciating}. The largest single-month move was +${fmt(dep.pct, 1)}% in ${monthLabel(dep.date)}.`,
      s: "World Bank GEM, PKR/USD period average; log changes.",
    },
    {
      t: "Imported inflation",
      d: "When the currency weakens, every dollar-priced input — edible oil, fertiliser, fuel, imported wheat and pulses — costs more rupees, even if world prices do not move. Part of that cost reaches the shop shelf.",
      s: "Transmission channels are developed in Chapter 03.",
    },
    {
      t: "The Pakistani context",
      d: "A structurally import-dependent economy with recurrent balance-of-payments pressure, managed and then market-based exchange-rate regimes, energy price adjustments, and the 2022 floods — all inside our eleven-year window.",
      s: "Event dummies for the 2019 CPI rebase, COVID-19 and the 2022 floods are tested in Chapter 08.",
    },
  ];

  return (
    <Chapter
      id="problem"
      n={2}
      kicker="The Problem"
      title={
        <>
          A third of the budget, <em className="text-s-food">tripled</em> in price.
        </>
      }
      intro={
        <>
          <p>
            Between January 2015 and December 2025 Pakistan’s food price index rose by <strong>{fmt(h.food_cpi_change_pct, 0)}%</strong> — a compound
            rate of <strong>{fmt(h.food_cagr_pct, 1)}% a year</strong>. Over the same months the number of rupees needed to buy one US dollar rose by{" "}
            <strong>{fmt(h.exr_change_pct, 0)}%</strong>, while world food prices measured by the FAO rose only{" "}
            <strong>{fmt(h.gfood_change_pct, 0)}%</strong>.
          </p>
          <p>The gap between the last two numbers is the puzzle this investigation sets out to explain.</p>
        </>
      }
    >
      <div className="grid gap-px overflow-hidden rounded-sm border border-line bg-line md:grid-cols-3">
        {[
          { v: h.food_infl_peak, d: 1, suf: "%", k: `Peak food inflation, ${monthLabel(h.food_infl_peak_date)}`, c: "text-s-food" },
          { v: h.exr_peak, d: 1, pre: "Rs ", k: `Weakest rupee per US$, ${monthLabel(h.exr_peak_date)} (monthly avg.)`, c: "text-s-exr" },
          { v: cost, d: 0, pre: "Rs ", k: "Cost in Dec 2025 of Rs 1,000 of food bought in Jan 2015", c: "text-paper" },
        ].map((s) => (
          <div key={s.k} className="bg-graphite p-6 sm:p-8">
            <CountUp value={s.v} decimals={s.d} prefix={s.pre ?? ""} suffix={s.suf ?? ""} className={`block text-4xl sm:text-5xl ${s.c}`} />
            <p className="mt-3 font-mono text-[0.68rem] uppercase leading-relaxed tracking-[0.12em] text-muted">{s.k}</p>
          </div>
        ))}
      </div>

      <div className="mt-20">
        <SubHead k="Evidence 2.1">Food inflation moved with the rupee, not with world food prices</SubHead>
        <Panel>
          <InflationChart dates={timeseries.dates} s={timeseries.series} peak={{ date: h.food_infl_peak_date, value: h.food_infl_peak }} />
          <SourceNote>
            Sources: PBS national CPI, food group (IMF CPI dataset to Jul 2025; PBS Monthly Reviews Aug–Dec 2025); World Bank GEM PKR/USD; FAO Food
            Price Index. Year-on-year % changes. Co-movement is descriptive — Chapters 06–07 test it formally.
          </SourceNote>
        </Panel>
      </div>

      <div className="mt-20">
        <SubHead k="Six ideas you need">The vocabulary of the investigation</SubHead>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {concepts.map((c, i) => (
            <Reveal key={c.t} delay={i * 0.05}>
              <article className="h-full border-t border-gold-soft pt-5">
                <h4 className="font-serif text-xl text-paper">{c.t}</h4>
                <p className="mt-3 text-[0.95rem] leading-relaxed text-paper-dim">{c.d}</p>
                <p className="mt-3 font-mono text-[0.64rem] text-faint">{c.s}</p>
              </article>
            </Reveal>
          ))}
        </div>
      </div>
    </Chapter>
  );
}
