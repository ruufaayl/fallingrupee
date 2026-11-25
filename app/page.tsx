import { Ch01Opening } from "@/components/chapters/Ch01Opening";
import { Ch02Problem } from "@/components/chapters/Ch02Problem";
import { Ch03Mechanism } from "@/components/chapters/Ch03Mechanism";
import { Ch04Data } from "@/components/chapters/Ch04Data";
import { Ch05Eda } from "@/components/chapters/Ch05Eda";
import { Ch06Engine } from "@/components/chapters/Ch06Engine";
import { Ch07Asymmetry } from "@/components/chapters/Ch07Asymmetry";
import { Ch08Credibility } from "@/components/chapters/Ch08Credibility";
import { Ch09Findings } from "@/components/chapters/Ch09Findings";
import { Ch10Conclusion } from "@/components/chapters/Ch10Conclusion";
import { ChapterNav } from "@/components/navigation/ChapterNav";
import photos from "@/data/research/photos.json";
import { findings, timeseries } from "@/lib/registry";
import { monthLabel } from "@/lib/format";

export default function Page() {
  const r = timeseries.rebased_2015m01;
  const h = findings.headline_numbers;
  const hero = (photos as { hero: { src: string; alt: string; credit: string } | null }).hero;
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
          photo={hero}
        />
        <Ch02Problem />
        <Ch03Mechanism />
        <Ch04Data />
        <Ch05Eda />
        <Ch06Engine />
        <Ch07Asymmetry />
        <Ch08Credibility />
        <Ch09Findings />
        <Ch10Conclusion />
      </main>
      <footer className="border-t border-line bg-ink px-4 py-12 sm:px-8">
        <div className="mx-auto flex max-w-6xl flex-wrap items-baseline justify-between gap-6">
          <div>
            <div className="font-display text-2xl text-paper">The Price of a Falling Rupee</div>
            <p className="mt-1 max-w-xl text-sm text-paper-dim">
              An econometric investigation of exchange-rate depreciation, international food prices and food inflation in Pakistan, 2015–2025.
            </p>
          </div>
          <div className="font-mono text-[0.66rem] leading-relaxed text-faint">
            Data: PBS · IMF · World Bank · FAO
            <br />
            Results registry generated {timeseries._meta.generated_utc.slice(0, 10)} · Macroeconomics final-semester project
            {hero ? (
              <>
                <br />
                Photograph: {hero.credit}
              </>
            ) : null}
          </div>
        </div>
      </footer>
    </>
  );
}
