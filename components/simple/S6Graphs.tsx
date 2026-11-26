import { AnnualBars, CorrelationHeatmap } from "@/components/charts/StatCharts";
import { Chapter, Panel, SourceNote, SubHead } from "@/components/ui/Chapter";
import { correlations, descriptives } from "@/lib/registry";
import { fmt, monthLabel } from "@/lib/format";

const ROWS: [string, string][] = [
  ["FOODCPI", "Food Prices"],
  ["EXR", "Dollar Rate"],
  ["GFOOD", "World Food Prices"],
  ["TRANSCPI", "Fuel & Transport Costs"],
  ["FOOD_INF_YOY", "Food inflation (% per year)"],
];

export function S6Graphs() {
  const D = Object.fromEntries(descriptives.variables.map((v) => [v.variable, v]));
  const years = Object.keys(descriptives.annual_growth_pct);
  const g = (k: string) => years.map((y) => descriptives.annual_growth_pct[y][k]);
  return (
    <Chapter id="graphs" n={6} kicker="Descriptive Statistics & Graphs" title={<>What the numbers look like before any test.</>}>
      <SubHead k="Table 2">Descriptive statistics (N = 132 months)</SubHead>
      <div className="overflow-x-auto">
        <table className="data-table">
          <thead>
            <tr>
              <th>Variable</th>
              <th className="text-right">Mean</th>
              <th className="text-right">Median</th>
              <th className="text-right">Std. dev.</th>
              <th className="text-right">Minimum</th>
              <th className="text-right">Maximum</th>
              <th className="text-right">Avg. growth / year</th>
            </tr>
          </thead>
          <tbody>
            {ROWS.map(([k, name]) => {
              const d = D[k];
              return (
                <tr key={k}>
                  <td className="text-paper">{name}</td>
                  <td className="n">{fmt(d.mean)}</td>
                  <td className="n">{fmt(d.median)}</td>
                  <td className="n">{fmt(d.sd)}</td>
                  <td className="n" title={monthLabel(d.min_date)}>{fmt(d.min)}</td>
                  <td className="n" title={monthLabel(d.max_date)}>{fmt(d.max)}</td>
                  <td className="n">{d.cagr_pct !== undefined ? `${fmt(d.cagr_pct, 1)}%` : "—"}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="mt-16 grid gap-10 lg:grid-cols-2">
        <div>
          <SubHead k="Graph 3">Correlation matrix</SubHead>
          <Panel>
            <CorrelationHeatmap levels={correlations.levels_log} diffs={correlations.first_differences_log} yoy={correlations.yoy_rates} />
          </Panel>
        </div>
        <div>
          <SubHead k="Graph 4">Yearly growth: food vs dollar vs world food</SubHead>
          <Panel>
            <AnnualBars years={years} food={g("FOODCPI")} exr={g("EXR")} world={g("GFOOD")} />
            <SourceNote>Growth of the yearly average. In the years the dollar rate jumped (2019, 2022, 2023), food prices jumped too.</SourceNote>
          </Panel>
        </div>
      </div>
    </Chapter>
  );
}
