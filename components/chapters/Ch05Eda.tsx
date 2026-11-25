import { AnnualBars, CorrelationHeatmap, InflationHistogram } from "@/components/charts/StatCharts";
import { Chapter, Panel, SourceNote, SubHead } from "@/components/ui/Chapter";
import { correlations, descriptives, timeseries } from "@/lib/registry";
import { fmt, fmtP, monthLabel } from "@/lib/format";

export function Ch05Eda() {
  const d = descriptives;
  const years = Object.keys(d.annual_growth_pct);
  const g = (k: string) => years.map((y) => d.annual_growth_pct[y][k]);
  const yoy = d.variables.find((v) => v.variable === "FOOD_INF_YOY")!;
  const mom = d.variables.find((v) => v.variable === "FOOD_INF_MOM")!;
  const lvl = d.variables.filter((v) => ["FOODCPI", "EXR", "GFOOD", "TRANSCPI", "CPI"].includes(v.variable));
  const rates = d.variables.filter((v) => v.variable.endsWith("_YOY") || v.variable.endsWith("_MOM"));
  const peakYear = years.reduce((a, b) => (d.annual_growth_pct[b].FOODCPI > d.annual_growth_pct[a].FOODCPI ? b : a));
  const worst = [...d.food_inflation_outliers.items].sort((a, b) => Math.abs(b.robust_z) - Math.abs(a.robust_z))[0];
  const momVals = (timeseries.series.FOOD_INF_MOM as number[]).map((v) => v ?? 0);

  const DescTable = ({ rows, growth }: { rows: typeof lvl; growth?: boolean }) => (
    <div className="overflow-x-auto">
      <table className="data-table">
        <thead>
          <tr>
            <th>Variable</th>
            <th className="text-right">Mean</th>
            <th className="text-right">Median</th>
            <th className="text-right">Std. dev.</th>
            <th className="text-right">Min</th>
            <th className="text-right">Max</th>
            <th className="text-right">Skew.</th>
            <th className="text-right">Kurt.</th>
            <th className="text-right">Jarque-Bera (p)</th>
            {growth ? <th className="text-right">Total Δ %</th> : null}
            {growth ? <th className="text-right">CAGR %</th> : null}
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.variable}>
              <td className="text-paper">{r.label}</td>
              <td className="n">{fmt(r.mean)}</td>
              <td className="n">{fmt(r.median)}</td>
              <td className="n">{fmt(r.sd)}</td>
              <td className="n" title={monthLabel(r.min_date)}>{fmt(r.min)}</td>
              <td className="n" title={monthLabel(r.max_date)}>{fmt(r.max)}</td>
              <td className="n">{fmt(r.skewness)}</td>
              <td className="n">{fmt(r.kurtosis)}</td>
              <td className="n">
                {fmt(r.jarque_bera, 1)} ({fmtP(r.jb_p)})
              </td>
              {growth ? <td className="n">{fmt(r.total_change_pct, 1)}</td> : null}
              {growth ? <td className="n">{fmt(r.cagr_pct, 2)}</td> : null}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );

  return (
    <Chapter
      id="eda"
      n={5}
      tone="graphite"
      kicker="Exploratory Data Analysis"
      title={<>Before the models: what the data say on their own.</>}
      intro={
        <p>
          Description comes before inference. These statistics show the size and shape of the shock, warn us where simple correlation will
          mislead, and flag the months a model will struggle to explain.
        </p>
      }
    >
      <SubHead k="Table 5.1">Descriptive statistics — levels, N = 132</SubHead>
      <DescTable rows={lvl} growth />
      <SourceNote>Hover a minimum or maximum to see its month. Kurtosis is reported as raw kurtosis (normal = 3).</SourceNote>

      <div className="mt-10">
        <SubHead k="Table 5.2">Inflation and growth rates (%)</SubHead>
        <DescTable rows={rates} />
      </div>

      <div className="mt-8 grid gap-6 md:grid-cols-3">
        {[
          { t: "Food inflation is not normal", b: `Monthly food inflation has skewness ${fmt(mom.skewness)} and kurtosis ${fmt(mom.kurtosis)} (JB p ${fmtP(mom.jb_p)}): long quiet spells broken by violent months. Fat tails are why residual normality will be hard to achieve.` },
          { t: "Persistent, not random", b: `Year-on-year food inflation averaged ${fmt(yoy.mean, 1)}% but its median was ${fmt(yoy.median, 1)}% — a right-skewed distribution pulled up by the 2022–23 surge.` },
          { t: "Different speeds", b: `The rupee’s compound depreciation rate (${fmt(lvl.find((r) => r.variable === "EXR")?.cagr_pct, 1)}% a year) is close to food’s (${fmt(lvl.find((r) => r.variable === "FOODCPI")?.cagr_pct, 1)}%); world food prices grew ${fmt(lvl.find((r) => r.variable === "GFOOD")?.cagr_pct, 1)}% a year.` },
        ].map((c) => (
          <article key={c.t} className="border-t border-gold-soft pt-4">
            <h4 className="font-serif text-lg text-paper">{c.t}</h4>
            <p className="mt-2 text-sm leading-relaxed text-paper-dim">{c.b}</p>
          </article>
        ))}
      </div>

      <div className="mt-20 grid gap-10 lg:grid-cols-2">
        <div>
          <SubHead k="Figure 5.3">Annual average growth</SubHead>
          <Panel>
            <AnnualBars years={years} food={g("FOODCPI")} exr={g("EXR")} world={g("GFOOD")} />
            <SourceNote>
              Growth of calendar-year averages. In {peakYear}, food prices rose {fmt(d.annual_growth_pct[peakYear].FOODCPI, 1)}% and rupees per
              dollar {fmt(d.annual_growth_pct[peakYear].EXR, 1)}%, while world food prices changed {fmt(d.annual_growth_pct[peakYear].GFOOD, 1)}%.
            </SourceNote>
          </Panel>
        </div>
        <div>
          <SubHead k="Figure 5.4">Correlation matrix</SubHead>
          <Panel>
            <CorrelationHeatmap levels={correlations.levels_log} diffs={correlations.first_differences_log} yoy={correlations.yoy_rates} />
          </Panel>
        </div>
      </div>

      <div className="mt-20 grid gap-10 lg:grid-cols-[1.4fr_1fr]">
        <div>
          <SubHead k="Figure 5.5">Distribution of monthly food inflation</SubHead>
          <Panel>
            <InflationHistogram values={momVals} dates={timeseries.dates} outliers={d.food_inflation_outliers.items} />
          </Panel>
        </div>
        <div>
          <SubHead k="Table 5.6">Outlier months</SubHead>
          <div className="overflow-x-auto">
          <table className="data-table">
            <thead>
              <tr>
                <th>Month</th>
                <th className="text-right">Food infl. m/m</th>
                <th className="text-right">Robust z</th>
              </tr>
            </thead>
            <tbody>
              {d.food_inflation_outliers.items.map((o) => (
                <tr key={o.date}>
                  <td>{monthLabel(o.date)}</td>
                  <td className="n">{fmt(o.food_inf_mom, 2)}%</td>
                  <td className="n">{fmt(o.robust_z, 2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          </div>
          <p className="mt-4 text-sm leading-relaxed text-paper-dim">
            Method: {d.food_inflation_outliers.method}. The most extreme month is {monthLabel(worst.date)} ({fmt(worst.food_inf_mom, 1)}% in a
            single month). It is kept in the data and tested with an impulse dummy in the robustness checks rather than deleted.
          </p>
        </div>
      </div>
    </Chapter>
  );
}
