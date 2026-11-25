import { ExternalLink } from "lucide-react";

import { Reveal } from "@/components/animations/Reveal";
import { Chapter, SubHead } from "@/components/ui/Chapter";
import { Disclosure } from "@/components/ui/Disclosure";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { ardl, descriptives, findings, longRun, manifest, nardl, sources } from "@/lib/registry";
import { fmt, fmtP } from "@/lib/format";
import { REFERENCES } from "@/lib/references";
import type { Status } from "@/lib/types";

export function Ch10Conclusion() {
  const Lx = longRun(ardl, "LEXR");
  const Lg = longRun(ardl, "LGFOOD");
  const Lp = longRun(nardl, "LEXR_POS");
  const Ln = longRun(nardl, "LEXR_NEG");
  const a = nardl.asymmetry!;
  const h = findings.headline_numbers;
  const dFood = Math.log(1 + h.food_cpi_change_pct / 100);
  const shareExr = (100 * Lx.coef * Math.log(1 + h.exr_change_pct / 100)) / dFood;
  const shareWorld = (100 * Lg.coef * Math.log(1 + h.gfood_change_pct / 100)) / dFood;
  const er = descriptives.exchange_rate_months;
  const groups = ["Methodology", "Exchange-rate pass-through & asymmetry", "Pakistan", "Data"] as const;

  const policy = [
    {
      t: "Exchange-rate stability is food policy",
      b: `With a long-run elasticity near ${fmt(Lx.coef, 2)}, a 10% depreciation is associated with food prices roughly ${fmt((Math.exp(Lx.coef * Math.log(1.1)) - 1) * 100, 1)}% higher once pass-through is complete. Avoiding abrupt, disorderly devaluations — and building the reserves that prevent them — protects household food budgets.`,
    },
    {
      t: "Do not count on recovery to reverse the damage quickly",
      b: "Prices did not fall in the months the rupee appreciated, and any later reversal is uncertain. Relief for households after a currency shock must come from targeted transfers, not from waiting for the rupee to recover.",
    },
    {
      t: "Watch the world market — and the import bill",
      b: `World food prices carry a long-run elasticity of about ${fmt(Lg.coef, 2)} in the ARDL. Diversifying edible-oil and pulse supplies, and raising domestic productivity in import-dependent staples, reduces exposure to both channels at once.`,
    },
    {
      t: "Make the transmission chain more competitive",
      b: "Asymmetric short-run adjustment is consistent with market power and inventory behaviour in wholesale and retail food markets. Market-information systems and competition oversight can shorten the lag between cost falls and shelf prices.",
    },
  ];

  const limitations = [
    "Observational time-series evidence: the models establish conditional associations and Granger-type dynamics, not causal effects. Exchange-rate movements are themselves endogenous to inflation and the balance of payments.",
    "Pre-2019 food CPI is the IMF’s back-linked version of the previous CPI; the 2015-16-base national CPI exists only from July 2019. Results in the post-2019 sub-sample (N = 75) are stronger but rest on few observations.",
    `Appreciation episodes are few and small (${er.appreciating} months, cumulatively ${fmt(er.cumulative_appreciation_log, 2)} log points against ${fmt(er.cumulative_depreciation_log, 2)} for depreciation), so the appreciation coefficient is imprecise; failing to reject symmetry is not evidence of symmetry.`,
    "In the NARDL the PSS F-test supports cointegration but the t-test does not; the CUSUM of squares crosses its bound, indicating changing residual variance.",
    "The energy proxy (transport CPI) mixes fuel with vehicle prices and fares; the policy rate and money supply could not be included for the full sample.",
    "All estimates were produced in Python (statsmodels). EViews programs reproduce the specifications, but EViews confirmation is pending until those programs are run.",
  ];

  const further = [
    "Item-level pass-through for wheat flour, edible oil, pulses and sugar using PBS’s SPI price data.",
    "Threshold or Markov-switching models to test whether pass-through is stronger in high-inflation regimes (Choudhri & Hakura, 2006).",
    "Structural VAR or local projections with identified exchange-rate shocks to move from association towards causation.",
    "Separating urban and rural food CPI, which PBS publishes as distinct indices under the 2015-16 base.",
  ];

  return (
    <Chapter
      id="conclusion"
      n={10}
      kicker="The Conclusion"
      title={<>The rupee’s fall is paid for at the market.</>}
      intro={
        <>
          <p>
            <strong>The research question</strong> asked to what extent depreciation, world food prices and domestic energy costs explain food
            inflation in Pakistan, and whether depreciation has a stronger or more persistent effect than appreciation.
          </p>
          <p>
            <strong>The answer.</strong> Food prices share a long-run equilibrium with the exchange rate and world food prices. A permanent 1%
            depreciation is associated with food prices about {fmt(Lx.coef, 2)}% higher in the long run (ARDL; NARDL depreciation effect{" "}
            {fmt(Lp.coef, 2)}, p = {fmtP(Lp.p)}), and a 1% rise in world food prices with about {fmt(Lg.coef, 2)}% higher. The rupee’s{" "}
            {fmt(h.exr_change_pct, 0)}% rise against the dollar, multiplied by that elasticity, corresponds to about {fmt(shareExr, 0)}% of the
            log rise in food prices over 2015–2025, against about {fmt(shareWorld, 0)}% for world food prices — an accounting decomposition with the
            long-run coefficients, not a causal attribution. Appreciation does not show an equivalent, statistically detectable opposite effect (L⁻ ={" "}
            {fmt(Ln.coef, 2)}, p = {fmtP(Ln.p)}); prices do not fall in the month the rupee recovers (impact symmetry rejected, p ={" "}
            {fmtP(a.short_run.p_impact)}); but long-run symmetry cannot be rejected (p = {fmtP(a.long_run.p_chi2)}).
          </p>
        </>
      }
    >
      <div className="grid gap-10 lg:grid-cols-2">
        <div>
          <SubHead k="For Pakistan">Policy implications</SubHead>
          <div className="space-y-6">
            {policy.map((p, i) => (
              <Reveal key={p.t} delay={i * 0.05}>
                <article className="border-t border-gold-soft pt-4">
                  <h4 className="font-serif text-xl text-paper">{p.t}</h4>
                  <p className="mt-2 text-[0.95rem] leading-relaxed text-paper-dim">{p.b}</p>
                </article>
              </Reveal>
            ))}
          </div>
        </div>
        <div>
          <SubHead k="Honesty">Limitations</SubHead>
          <ol className="list-decimal space-y-3 pl-5 text-[0.95rem] leading-relaxed text-paper-dim marker:font-mono marker:text-gold">
            {limitations.map((l) => (
              <li key={l}>{l}</li>
            ))}
          </ol>
          <div className="mt-10">
            <SubHead k="Next">Further research</SubHead>
            <ul className="space-y-2 text-[0.95rem] leading-relaxed text-paper-dim">
              {further.map((f) => (
                <li key={f} className="border-l border-line pl-4">
                  {f}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      <Reveal>
        <blockquote className="mx-auto my-28 max-w-4xl text-center">
          <p className="font-display text-4xl leading-tight text-paper sm:text-6xl">
            A currency can recover in a season. <span className="italic text-gold">The price of bread remembers.</span>
          </p>
          <footer className="mt-6 font-mono text-[0.7rem] uppercase tracking-[0.18em] text-muted">Closing statement</footer>
        </blockquote>
      </Reveal>

      <div id="appendix" className="border-t border-line pt-10">
        <div className="kicker mb-6">Appendices</div>
        <Disclosure title={`Bibliography (${REFERENCES.length})`}>
          {groups.map((g) => (
            <div key={g} className="mb-6">
              <h5 className="mb-3 font-mono text-[0.68rem] uppercase tracking-[0.14em] text-gold">{g}</h5>
              <ul className="space-y-2 text-sm leading-relaxed text-paper-dim">
                {REFERENCES.filter((r) => r.group === g).map((r) => (
                  <li key={r.key} className="pl-6 -indent-6">
                    {r.text}{" "}
                    {r.doi ? (
                      <a className="text-gold hover:underline" href={`https://doi.org/${r.doi}`} target="_blank" rel="noreferrer">
                        doi:{r.doi}
                      </a>
                    ) : r.url ? (
                      <a className="text-gold hover:underline" href={r.url} target="_blank" rel="noreferrer">
                        {r.url}
                      </a>
                    ) : null}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </Disclosure>
        <Disclosure title="Data-source register">
          <ul className="space-y-4 text-sm">
            {sources.map((s) => (
              <li key={s.id}>
                <a href={s.url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-2 text-paper hover:text-gold">
                  {s.institution} <ExternalLink className="h-3 w-3" aria-hidden />
                </a>
                <div className="text-paper-dim">{s.title}</div>
                <ul className="mt-1 font-mono text-[0.66rem] text-faint">
                  {s.downloads.map((d) => (
                    <li key={d.file}>
                      data/raw/{d.file} · {d.downloaded_utc} · sha256 {d.sha256.slice(0, 12)}…
                    </li>
                  ))}
                </ul>
              </li>
            ))}
          </ul>
        </Disclosure>
        <Disclosure title="Methodology appendix & reproducibility">
          <div className="grid gap-8 text-sm leading-relaxed text-paper-dim md:grid-cols-2">
            <div>
              <h5 className="mb-2 text-paper">Pipeline</h5>
              <ol className="list-decimal space-y-1 pl-5">
                <li><code className="font-mono text-gold">scripts/01_fetch_data.py</code> — downloads every raw file, logs URL, time and SHA-256.</li>
                <li><code className="font-mono text-gold">scripts/02_build_dataset.py</code> — builds the dataset; 10 cross-source validation checks.</li>
                <li><code className="font-mono text-gold">scripts/03_estimate.py</code> — all tests and models (uses <code className="font-mono">ardl_engine.py</code>).</li>
                <li><code className="font-mono text-gold">scripts/04_figures.py</code> — report figures.</li>
                <li><code className="font-mono text-gold">scripts/05_build_registry.py</code> — the website’s results registry.</li>
                <li><code className="font-mono text-gold">scripts/06_write_eviews.py</code> → <code className="font-mono">eviews/*.prg</code>; <code className="font-mono text-gold">07_compare_eviews.py</code> marks results verified.</li>
              </ol>
            </div>
            <div>
              <h5 className="mb-2 text-paper">Specification choices</h5>
              <ul className="list-disc space-y-1 pl-5">
                <li>Natural logs of all levels; elasticities interpreted as % responses.</li>
                <li>Lag search: max 4 lags for each variable, common sample, AIC (SIC and HQ in robustness).</li>
                <li>PSS case III (unrestricted intercept, no trend) with 11 monthly dummies.</li>
                <li>Partial sums start at zero in 2015M01; k counts EXR⁺ and EXR⁻ separately (k = 4).</li>
                <li>Long-run standard errors by the delta method; multipliers banded by 5,000 parametric draws.</li>
              </ul>
            </div>
            <div className="md:col-span-2">
              <h5 className="mb-2 text-paper">Verification status of each model</h5>
              <ul className="space-y-2">
                {manifest.models.map((m) => (
                  <li key={m.model_id} className="flex flex-wrap items-center gap-3">
                    <span className="font-mono text-[0.72rem] text-paper">{m.model_id}</span>
                    <span>{m.description}</span>
                    <StatusBadge status={m.status} />
                    <span className="font-mono text-[0.66rem] text-faint">{m.eviews_program}</span>
                  </li>
                ))}
              </ul>
              <ul className="mt-4 space-y-1 font-mono text-[0.66rem] text-faint">
                {(Object.entries(manifest.status_legend) as [Status, string][]).map(([k, v]) => (
                  <li key={k}>
                    {k}: {v}
                  </li>
                ))}
              </ul>
              <p className="mt-2 font-mono text-[0.66rem] text-faint">Registry generated {manifest.generated_utc}.</p>
            </div>
          </div>
        </Disclosure>
        <Disclosure title="Acknowledgements">
          <p className="max-w-3xl text-sm leading-relaxed text-paper-dim">
            This investigation was prepared as a final-semester Macroeconomics project. It relies on the public data of the Pakistan Bureau of
            Statistics, the International Monetary Fund, the World Bank and the Food and Agriculture Organization, and on DBnomics for open access
            to IMF series. Estimation uses the open-source statsmodels, arch, pandas and SciPy libraries; the site is built with Next.js, Apache
            ECharts, GSAP, Framer Motion and KaTeX. Any errors are the author’s.
          </p>
        </Disclosure>
      </div>
    </Chapter>
  );
}
