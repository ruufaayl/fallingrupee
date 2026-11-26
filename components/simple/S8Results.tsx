import { Chapter, Panel, SubHead } from "@/components/ui/Chapter";
import { fmt } from "@/lib/format";
import { simple } from "@/lib/simple";

const TONE: Record<string, string> = { RupeeDep_lag1: "#d28e05", WorldFoodInf_lag1: "#00a888", FuelInf_lag1: "#338ced", FoodInf_lag1: "#c9a24a" };
const pv = (p: number) => (p < 0.001 ? "< 0.001" : p.toFixed(3));
const sgn = (x: number) => (x >= 0 ? `+ ${fmt(x)}` : `− ${fmt(Math.abs(x))}`);

function Dot({ name, coef, ci, p, color, note }: { name: string; coef: number; ci: [number, number]; p: number; color: string; note: string }) {
  return { name, coef, ci, p, color, note };
}

export function S8Results() {
  const c = simple.coefficients;
  const a = simple.asymmetry;
  const rows = c.map((x) => Dot({ name: `${x.symbol} ${x.name}`, coef: x.coef, ci: x.ci, p: x.p, color: TONE[x.code], note: x.plain }));
  const lo = Math.min(0, ...rows.map((r) => r.ci[0]));
  const hi = Math.max(...rows.map((r) => r.ci[1]));
  const sc = (v: number) => ((v - lo) / (hi - lo)) * 100;
  const asym = [
    { name: "Rupee falls (depreciation)", coef: a.dep_coef, ci: a.dep_ci, p: a.dep_p, color: "#e5484d", note: `${a.dep_months} months` },
    { name: "Rupee rises (appreciation)", coef: a.app_coef, ci: a.app_ci, p: a.app_p, color: "#00a888", note: `${a.app_months} months` },
  ];
  const alo = Math.min(...asym.map((r) => r.ci[0]));
  const ahi = Math.max(...asym.map((r) => r.ci[1]));
  const asc = (v: number) => ((v - alo) / (ahi - alo)) * 100;

  const Bar = ({ r, s }: { r: (typeof rows)[number]; s: (v: number) => number }) => (
    <div>
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <span className="font-serif text-lg text-paper">{r.name}</span>
        <span className="num text-sm text-paper-dim">
          {fmt(r.coef, 3)} · p = {pv(r.p)} <span className={r.p < 0.05 ? "text-fall" : "text-faint"}>{r.p < 0.05 ? "significant" : "not significant"}</span>
        </span>
      </div>
      <div className="relative mt-3 h-6" role="img" aria-label={`${r.name}: ${r.coef}, 95% range ${r.ci[0]} to ${r.ci[1]}`}>
        <div className="absolute inset-y-0 w-px bg-line-strong" style={{ left: `${s(0)}%` }} />
        <div className="absolute top-1/2 h-[3px] -translate-y-1/2" style={{ left: `${s(r.ci[0])}%`, width: `${s(r.ci[1]) - s(r.ci[0])}%`, background: r.color, opacity: 0.5 }} />
        <div
          className="absolute top-1/2 h-4 w-4 -translate-x-1/2 -translate-y-1/2 rounded-full border-2"
          style={{ left: `${s(r.coef)}%`, borderColor: r.color, background: r.p < 0.05 ? r.color : "#0b0c0e" }}
        />
      </div>
      <p className="mt-2 text-sm text-paper-dim">{r.note}</p>
    </div>
  );

  return (
    <Chapter id="results" n={8} kicker="Results" title={<>The answer, in one equation.</>}>
      <div className="rounded-sm border border-gold/50 bg-graphite px-5 py-10 text-center sm:px-10">
        <div className="kicker">Estimated regression (OLS)</div>
        <p className="mt-5 font-display text-3xl leading-snug text-paper sm:text-[2.6rem]">
          <span className="text-s-food">Food Inflation</span> = {fmt(simple.constant)} {sgn(c[0].coef)} <span className="text-s-exr">Rupee Depreciation</span>{" "}
          {sgn(c[1].coef)} <span className="text-s-world">World Food Inflation</span> {sgn(c[2].coef)}{" "}
          <span className="text-s-energy">Fuel &amp; Transport Inflation</span> {sgn(c[3].coef)} <span className="text-gold">Last Month&rsquo;s Food Inflation</span>
        </p>
        <p className="num mt-5 text-sm text-paper-dim">
          N = {simple.n} · R² = {simple.fit.r2.toFixed(3)} · adj. R² = {simple.fit.adj_r2.toFixed(3)} · F = {simple.fit.F.toFixed(2)} (p = {pv(simple.fit.F_p)})
        </p>
        <p className="mx-auto mt-3 max-w-3xl text-sm leading-relaxed text-paper-dim">{simple.equation_note}</p>
      </div>

      <div className="mt-14 overflow-x-auto">
        <SubHead k="Table 5">Regression output</SubHead>
        <table className="data-table">
          <thead>
            <tr>
              <th>Variable</th>
              <th className="text-right">Coefficient</th>
              <th className="text-right">Std. error</th>
              <th className="text-right">t-statistic</th>
              <th className="text-right">p-value</th>
              <th>Significant at 5%?</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td className="text-paper">β₀ Constant</td>
              <td className="n">{fmt(simple.constant, 3)}</td>
              <td className="n">—</td>
              <td className="n">—</td>
              <td className="n">—</td>
              <td />
            </tr>
            {c.map((x) => (
              <tr key={x.code}>
                <td className="text-paper">
                  {x.symbol} {x.name}
                </td>
                <td className="n">{fmt(x.coef, 3)}</td>
                <td className="n">{fmt(x.se, 3)}</td>
                <td className="n">{fmt(x.t, 2)}</td>
                <td className="n">{pv(x.p)}</td>
                <td className={x.significant ? "text-fall" : "text-faint"}>{x.significant ? "Yes" : "No"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="mt-14 grid gap-10 lg:grid-cols-[1.2fr_1fr]">
        <div>
          <SubHead k="Graph 6">How big is each effect? (with 95% range)</SubHead>
          <Panel>
            <div className="space-y-7">
              {rows.map((r) => (
                <Bar key={r.name} r={r} s={sc} />
              ))}
              <div className="flex justify-between font-mono text-[0.62rem] text-faint">
                <span>{fmt(lo)}</span>
                <span>if the range crosses the zero line → not significant</span>
                <span>{fmt(hi)}</span>
              </div>
            </div>
          </Panel>
        </div>
        <div>
          <SubHead k="Table 6">Hypothesis results</SubHead>
          <div className="space-y-3">
            {simple.hypotheses.map((h) => (
              <div key={h.id} className="rounded-sm border border-line bg-ink p-4">
                <div className="flex flex-wrap items-baseline justify-between gap-2">
                  <span className="num text-gold">{h.id}</span>
                  <span className={`font-mono text-[0.7rem] uppercase tracking-[0.08em] ${h.reject ? "text-fall" : "text-paper-dim"}`}>{h.decision}</span>
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
        <SubHead k="Graph 7">When the rupee falls vs when it rises</SubHead>
        <Panel>
          <div className="space-y-8">
            {asym.map((r) => (
              <Bar key={r.name} r={r} s={asc} />
            ))}
          </div>
          <p className="mt-6 text-sm leading-relaxed text-paper-dim">
            We split last month’s rupee change into “rupee fell” and “rupee rose” and ran the same regression. A falling rupee raises food inflation
            (p = {pv(a.dep_p)}); a rising rupee has no measurable effect (p = {pv(a.app_p)}). The Wald F-test of “same effect” gives p = {pv(a.p)}, so the
            difference is not statistically proven — partly because the rupee rose in only {a.app_months} of the months.
          </p>
        </Panel>
      </div>
    </Chapter>
  );
}
