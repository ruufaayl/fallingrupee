import { Reveal } from "@/components/animations/Reveal";
import { Chapter, SubHead } from "@/components/ui/Chapter";
import { simple } from "@/lib/simple";

export function S4Model() {
  return (
    <Chapter
      id="model"
      n={4}
      kicker="The Equation & Hypotheses"
      title={<>One equation answers the question.</>}
      intro={<p>Food inflation on the left; the possible causes on the right. The β (beta) numbers tell us how strongly each cause moves food inflation.</p>}
    >
      <Reveal>
        <div className="rounded-sm border border-line bg-graphite px-5 py-10 text-center sm:px-10">
          <p className="font-display text-3xl leading-snug text-paper sm:text-5xl">
            <span className="text-s-food">Food Inflation</span> = β₀ + β₁ <span className="text-s-exr">Rupee Depreciation</span> + β₂{" "}
            <span className="text-s-world">World Food Inflation</span> + β₃ <span className="text-s-energy">Fuel &amp; Transport Inflation</span> + β₄{" "}
            <span className="text-gold">Last Month&rsquo;s Food Inflation</span> + error
          </p>
          <p className="mx-auto mt-6 max-w-3xl text-sm leading-relaxed text-paper-dim">
            Every variable is a monthly % change. Each β says how many percentage points food inflation moves when that variable moves by 1
            point. β₁ = 0.5 would mean “a 1% weaker rupee → food prices 0.5% higher the next month”. This is a standard OLS regression.
          </p>
        </div>
      </Reveal>

      <div className="mt-16">
        <SubHead k="Hypotheses">What we test — H₀ (no effect) against H₁ (effect)</SubHead>
        <div className="overflow-x-auto">
          <table className="data-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Question</th>
                <th>H₀ (null hypothesis)</th>
                <th>H₁ (alternative)</th>
                <th>Test used</th>
              </tr>
            </thead>
            <tbody>
              {simple.hypotheses.map((h) => (
                <tr key={h.id}>
                  <td className="num text-gold">{h.id}</td>
                  <td className="min-w-[14rem] text-paper">{h.question}</td>
                  <td className="min-w-[14rem] text-paper-dim">{h.h0}</td>
                  <td className="min-w-[14rem] text-paper-dim">{h.h1}</td>
                  <td className="min-w-[10rem] font-mono text-[0.75rem] text-paper-dim">{h.test}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="mt-4 text-sm text-paper-dim">
          Decision rule: if the p-value is below 0.05, we <strong className="text-paper">reject H₀</strong> — the effect is statistically significant at 5%.
        </p>
      </div>
    </Chapter>
  );
}
