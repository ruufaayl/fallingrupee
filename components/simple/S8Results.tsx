import { MultiplierChart } from "@/components/charts/ModelCharts";
import { Chapter, Panel, SourceNote, SubHead } from "@/components/ui/Chapter";
import { multipliers } from "@/lib/registry";
import { fmt } from "@/lib/format";
import { simple } from "@/lib/simple";

const TONE: Record<string, string> = { LEXR: "#d28e05", LGFOOD: "#00a888", LTRANSCPI: "#338ced" };

export function S8Results() {
  const lo = Math.min(0, ...simple.coefficients.map((c) => c.ci[0]));
  const hi = Math.max(...simple.coefficients.map((c) => c.ci[1]));
  const sc = (v: number) => ((v - lo) / (hi - lo)) * 100;
  const a = simple.asymmetry;
  return (
    <Chapter id="results" n={8} kicker="Results" title={<>The answer, in one equation.</>}>
      <div className="rounded-sm border border-gold/50 bg-graphite px-5 py-10 text-center sm:px-10">
        <div className="kicker">Estimated long-run equation</div>
        <p className="mt-5 font-display text-3xl leading-snug text-paper sm:text-5xl">
          <span className="text-s-food">Food Prices</span> = {fmt(simple.constant)} + {fmt(simple.coefficients[0].coef)}{" "}
          <span className="text-s-exr">Dollar Rate</span> + {fmt(simple.coefficients[1].coef)}{" "}
          <span className="text-s-world">World Food Prices</span> + {fmt(simple.coefficients[2].coef)}{" "}
          <span className="text-s-energy">Fuel &amp; Transport Costs</span>
        </p>
        <p className="mx-auto mt-6 max-w-3xl text-sm leading-relaxed text-paper-dim">{simple.equation_note}</p>
      </div>

      <div className="mt-14 grid gap-10 lg:grid-cols-[1.2fr_1fr]">
        <div>
          <SubHead k="Graph 7">How big is each effect? (with 95% range)</SubHead>
          <Panel>
            <div className="space-y-8">
              {simple.coefficients.map((c) => (
                <div key={c.code}>
                  <div className="flex flex-wrap items-baseline justify-between gap-2">
                    <span className="font-serif text-xl text-paper">
                      {c.symbol} {c.name}
                    </span>
                    <span className="num text-sm text-paper-dim">
                      {fmt(c.coef)} · p = {c.p < 0.001 ? "< 0.001" : c.p.toFixed(3)}{" "}
                      <span className={c.significant ? "text-fall" : "text-faint"}>{c.significant ? "significant" : "not significant"}</span>
                    </span>
                  </div>
                  <div className="relative mt-3 h-6" role="img" aria-label={`${c.name}: ${c.coef}, 95% range ${c.ci[0]} to ${c.ci[1]}`}>
                    <div className="absolute inset-y-0 w-px bg-line-strong" style={{ left: `${sc(0)}%` }} />
                    <div className="absolute top-1/2 h-[3px] -translate-y-1/2" style={{ left: `${sc(c.ci[0])}%`, width: `${sc(c.ci[1]) - sc(c.ci[0])}%`, background: TONE[c.code], opacity: 0.5 }} />
                    <div
                      className="absolute top-1/2 h-4 w-4 -translate-x-1/2 -translate-y-1/2 rounded-full border-2"
                      style={{ left: `${sc(c.coef)}%`, borderColor: TONE[c.code], background: c.significant ? TONE[c.code] : "#0b0c0e" }}
                    />
                  </div>
                  <p className="mt-2 text-sm text-paper-dim">{c.plain}</p>
                </div>
              ))}
              <div className="flex justify-between font-mono text-[0.62rem] text-faint">
                <span>{fmt(lo)}</span>
                <span>effect on food prices (elasticity)</span>
                <span>{fmt(hi)}</span>
              </div>
            </div>
          </Panel>
        </div>
        <div>
          <SubHead k="Table 4">Hypothesis results</SubHead>
          <div className="space-y-3">
            {simple.hypotheses.map((h) => (
              <div key={h.id} className="rounded-sm border border-line bg-ink p-4">
                <div className="flex flex-wrap items-baseline justify-between gap-2">
                  <span className="num text-gold">{h.id}</span>
                  <span className={`font-mono text-[0.7rem] uppercase tracking-[0.08em] ${h.reject ? "text-fall" : "text-rise"}`}>{h.decision}</span>
                </div>
                <p className="mt-1 text-paper">{h.question}</p>
                <p className="num mt-1 text-[0.78rem] text-paper-dim">
                  {h.test}: {h.result}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="mt-20">
        <SubHead k="Graph 8">When the rupee falls vs when it recovers</SubHead>
        <div className="mb-6 grid gap-px overflow-hidden rounded-sm border border-line bg-line sm:grid-cols-3">
          <div className="bg-graphite p-5">
            <div className="font-mono text-[0.64rem] uppercase tracking-[0.12em] text-muted">Rupee falls 1% · long run</div>
            <div className="num mt-2 text-3xl text-rise">+{fmt(a.falling)}%</div>
            <div className="num text-xs text-faint">p = {a.falling_p.toFixed(3)} · significant</div>
          </div>
          <div className="bg-graphite p-5">
            <div className="font-mono text-[0.64rem] uppercase tracking-[0.12em] text-muted">Rupee recovers 1% · same month</div>
            <div className="num mt-2 text-3xl text-fall">+{fmt(a.impact_rising)}%</div>
            <div className="num text-xs text-faint">food prices did not fall</div>
          </div>
          <div className="bg-graphite p-5">
            <div className="font-mono text-[0.64rem] uppercase tracking-[0.12em] text-muted">Same effect? (Wald test)</div>
            <div className="num mt-2 text-xl text-paper">Short run p = {a.p_short.toFixed(3)} → No</div>
            <div className="num text-sm text-paper-dim">Long run p = {a.p_long.toFixed(3)} → can’t tell</div>
          </div>
        </div>
        <Panel>
          <MultiplierChart m={multipliers} />
          <SourceNote>
            Red: how food prices respond, month by month, to a 1% weaker rupee. Green: response to a 1% stronger rupee. Shaded areas are 95% ranges. Estimated with a
            nonlinear ARDL (NARDL) that splits the rupee into “falling” and “rising” parts.
          </SourceNote>
        </Panel>
      </div>
    </Chapter>
  );
}
