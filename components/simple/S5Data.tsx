import { Download, ExternalLink } from "lucide-react";

import { SeriesExplorer } from "@/components/charts/TimeCharts";
import { Chapter, Panel, SourceNote, SubHead } from "@/components/ui/Chapter";
import { descriptives, timeseries } from "@/lib/registry";
import { fmt } from "@/lib/format";
import { simple } from "@/lib/simple";

const LINKS: Record<string, string> = {
  "Food Prices": "https://www.pbs.gov.pk/price-statistics/",
  "Dollar Rate": "https://databank.worldbank.org/source/global-economic-monitor-(gem)",
  "World Food Prices": "https://www.fao.org/worldfoodsituation/foodpricesindex/en/",
  "Fuel & Transport Costs": "https://www.pbs.gov.pk/price-statistics/",
};
const CODE: Record<string, string> = { "Food Prices": "FOODCPI", "Dollar Rate": "EXR", "World Food Prices": "GFOOD", "Fuel & Transport Costs": "TRANSCPI" };
const SERIES = [
  { name: "Food Prices", source: "Pakistan Bureau of Statistics (PBS)", measure: "National food price index (2015-16 = 100)" },
  { name: "Dollar Rate", source: "World Bank (Global Economic Monitor)", measure: "Rupees per US dollar, monthly average" },
  { name: "World Food Prices", source: "Food and Agriculture Organization (FAO)", measure: "FAO Food Price Index (2014–16 = 100)" },
  { name: "Fuel & Transport Costs", source: "Pakistan Bureau of Statistics (PBS)", measure: "Transport price index (2015-16 = 100)" },
];

export function S5Data() {
  const D = Object.fromEntries(descriptives.variables.map((v) => [v.variable, v]));
  return (
    <Chapter
      id="data"
      n={5}
      tone="graphite"
      kicker="The Data"
      title={<>132 months. Four official sources. One table.</>}
      intro={
        <p>
          Monthly data from {simple.period}. Every series was downloaded from its official source and combined month by month into one sheet — no
          missing values, nothing estimated or filled in. The regression uses the monthly % change of each series, which is also in the sheet.
        </p>
      }
    >
      <div className="flex flex-wrap items-center gap-4">
        <a
          href="/Falling_Rupee_Dataset.xlsx"
          download
          className="inline-flex items-center gap-3 border border-gold bg-gold px-5 py-3 font-mono text-[0.72rem] uppercase tracking-[0.16em] text-ink transition-colors hover:bg-transparent hover:text-paper"
        >
          <Download className="h-4 w-4" aria-hidden /> Download the combined dataset (Excel)
        </a>
        <span className="font-mono text-[0.68rem] text-faint">Sheets: Combined Data · Regression Data · Sources · Summary Statistics</span>
      </div>

      <div className="mt-12">
        <SubHead k="Table 1">Data sources</SubHead>
        <div className="overflow-x-auto">
          <table className="data-table">
            <thead>
              <tr>
                <th>Variable</th>
                <th>Source</th>
                <th>Unit</th>
                <th className="text-right">Jan 2015</th>
                <th className="text-right">Dec 2025</th>
                <th className="text-right">Change</th>
              </tr>
            </thead>
            <tbody>
              {SERIES.map((v) => {
                const d = D[CODE[v.name]];
                const s = timeseries.series[CODE[v.name]] as number[];
                return (
                  <tr key={v.name}>
                    <td className="text-paper">{v.name}</td>
                    <td>
                      <a href={LINKS[v.name]} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1.5 text-paper-dim hover:text-gold">
                        {v.source} <ExternalLink className="h-3 w-3" aria-hidden />
                      </a>
                    </td>
                    <td className="text-paper-dim">{v.measure}</td>
                    <td className="n">{fmt(s[0])}</td>
                    <td className="n">{fmt(s[s.length - 1])}</td>
                    <td className="n text-paper">+{fmt(d.total_change_pct, 0)}%</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      <div className="mt-14">
        <SubHead k="Graph 2">All four variables over time</SubHead>
        <Panel>
          <SeriesExplorer dates={timeseries.dates} s={timeseries.series} rebased={timeseries.rebased_2015m01} />
          <SourceNote>Click the variable names to show or hide them. “Rebased 100” sets every series to 100 in January 2015 so they can be compared.</SourceNote>
        </Panel>
      </div>
    </Chapter>
  );
}
