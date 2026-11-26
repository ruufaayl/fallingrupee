import { Ch01Opening } from "@/components/chapters/Ch01Opening";
import { ChapterNav } from "@/components/navigation/ChapterNav";
import { S2Problem } from "@/components/simple/S2Problem";
import { S3Variables } from "@/components/simple/S3Variables";
import { S4Model } from "@/components/simple/S4Model";
import { S5Data } from "@/components/simple/S5Data";
import { S6Graphs } from "@/components/simple/S6Graphs";
import { S7Tests } from "@/components/simple/S7Tests";
import { S8Results } from "@/components/simple/S8Results";
import { S9Conclusion } from "@/components/simple/S9Conclusion";
import { findings, timeseries } from "@/lib/registry";
import { monthLabel } from "@/lib/format";

export default function Page() {
  const r = timeseries.rebased_2015m01;
  const h = findings.headline_numbers;
  return (
    <>
      <noscript>
        <style>{`[data-o]{opacity:1!important;transform:none!important}`}</style>
      </noscript>
      <ChapterNav />
      <main>
        <Ch01Opening
          exr={r.EXR}
          food={r.FOODCPI}
          world={r.GFOOD}
          headline={{ food: h.food_cpi_change_pct, exr: h.exr_change_pct, world: h.gfood_change_pct, peak: h.food_infl_peak, peakDate: monthLabel(h.food_infl_peak_date) }}
          photo={null}
        />
        <S2Problem />
        <S3Variables />
        <S4Model />
        <S5Data />
        <S6Graphs />
        <S7Tests />
        <S8Results />
        <S9Conclusion />
      </main>
      <footer className="border-t border-line bg-ink px-4 py-12 sm:px-8">
        <div className="mx-auto flex max-w-6xl flex-wrap items-baseline justify-between gap-6">
          <div>
            <div className="font-display text-2xl text-paper">The Price of a Falling Rupee</div>
            <p className="mt-1 max-w-xl text-sm text-paper-dim">Exchange rate, world food prices and food inflation in Pakistan, 2015–2025.</p>
          </div>
          <div className="font-mono text-[0.66rem] leading-relaxed text-faint">
            Data: Pakistan Bureau of Statistics · World Bank · FAO · IMF
            <br />
            Macroeconomics final-semester project
          </div>
        </div>
      </footer>
    </>
  );
}
