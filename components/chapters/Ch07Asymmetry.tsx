import { MultiplierChart, PartialSumsChart } from "@/components/charts/ModelCharts";
import { BoundsLine } from "@/components/econometrics/BoundsLine";
import { CoefTable } from "@/components/econometrics/CoefTable";
import { Equation } from "@/components/econometrics/Equation";
import { Chapter, Panel, SourceNote, SubHead } from "@/components/ui/Chapter";
import { Disclosure } from "@/components/ui/Disclosure";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { descriptives, findings, longRun, multipliers, nardl, timeseries, wald } from "@/lib/registry";
import { fmt, fmtP } from "@/lib/format";

import { AsymmetryPanel } from "./AsymmetryPanel";

export function Ch07Asymmetry() {
  const a = nardl.asymmetry!;
  const b = nardl.bounds_test;
  const Lp = longRun(nardl, "LEXR_POS");
  const Ln = longRun(nardl, "LEXR_NEG");
  const lev = nardl.levels_equation.coefficients;
  const bp = lev.find((c) => c.term === "LEXR_POS")!;
  const bn = lev.find((c) => c.term === "LEXR_NEG")!;
  const ci = (c: { coef: number | null; se: number | null }) => [c.coef! - 1.96 * c.se!, c.coef! + 1.96 * c.se!];
  const answer = findings.answers.find((x) => x.q.startsWith("Does appreciation"))!;
  const er = descriptives.exchange_rate_months;
  const order = nardl.selection.chosen_order;

  return (
    <Chapter
      id="asymmetry"
      n={7}
      tone="graphite"
      kicker="The Asymmetry Investigation"
      title={
        <>
          When the rupee falls, prices rise. <span className="italic text-gold">What happens when it recovers?</span>
        </>
      }
      intro={
        <>
          <p>
            Shoppers say it, economists have documented it in petrol and many other markets (Bacon, 1991; Peltzman, 2000): prices go up like
            rockets and come down like feathers. If the same holds for the rupee, a recovery would not undo the damage of a depreciation.
          </p>
          <p>
            A standard ARDL cannot test this, because it forces depreciation and appreciation to have mirror-image effects. The{" "}
            <strong>nonlinear ARDL</strong> of Shin, Yu &amp; Greenwood-Nimmo (2014) relaxes that restriction.
          </p>
        </>
      }
    >
      <SubHead k="Step 1" aside={<StatusBadge status={nardl._meta.status} />}>
        Split the exchange rate in two
      </SubHead>
      <div className="grid gap-10 lg:grid-cols-[1fr_1.3fr]">
        <div>
          <Equation tex={String.raw`\ln \text{EXR}_t = \ln \text{EXR}_0 + \text{EXR}^{+}_t + \text{EXR}^{-}_t`} />
          <Equation tex={String.raw`\text{EXR}^{+}_t = \sum_{j=1}^{t} \max(\Delta \ln \text{EXR}_j,\,0), \qquad \text{EXR}^{-}_t = \sum_{j=1}^{t} \min(\Delta \ln \text{EXR}_j,\,0)`} />
          <p className="mt-4 leading-relaxed text-paper-dim">
            Because a rise in rupees per dollar is a depreciation, <span className="text-rise">EXR⁺</span> accumulates every depreciation and{" "}
            <span className="text-fall">EXR⁻</span> every appreciation. Over 2015–2025 the rupee depreciated in {er.depreciating} months (cumulative{" "}
            {fmt(er.cumulative_depreciation_log, 3)} log points) and appreciated in {er.appreciating} months ({fmt(er.cumulative_appreciation_log, 3)}).
            Appreciation episodes exist — but they are fewer and smaller, which limits how precisely their effect can be estimated.
          </p>
        </div>
        <Panel>
          <PartialSumsChart dates={timeseries.dates} exr={timeseries.series.EXR as number[]} pos={timeseries.series.LEXR_POS as number[]} neg={timeseries.series.LEXR_NEG as number[]} />
        </Panel>
      </div>

      <div className="mt-20">
        <SubHead k="Step 2">Estimate the asymmetric model</SubHead>
        <Equation
          tex={String.raw`\Delta \ln \text{FOOD}_t = c + \rho \ln \text{FOOD}_{t-1} + \theta^{+}\text{EXR}^{+}_{t-1} + \theta^{-}\text{EXR}^{-}_{t-1} + \theta_g \ln\text{GFOOD}_{t-1} + \theta_e \ln\text{ENERGY}_{t-1} + \ldots + \varepsilon_t`}
          label={`Selected by AIC (and identically by SIC and HQ): NARDL(${order.join(", ")}), ${nardl.sample.start}–${nardl.sample.end}, N = ${nardl.sample.nobs}, with monthly dummies.`}
        />
        <div className="mt-8 grid gap-8 lg:grid-cols-2">
          <Panel>
            <BoundsLine b={b} kind="F" />
          </Panel>
          <Panel>
            <BoundsLine b={b} kind="t" />
          </Panel>
        </div>
        <p className="mt-6 max-w-3xl leading-relaxed text-paper-dim">
          Here the two PSS tests disagree. The F-test rejects “no long-run relationship” (F = {fmt(b.F, 2)}), but the t-test on ρ does not (t ={" "}
          {fmt(b.t, 2)}, simulated p = {fmtP(b.p_value_t_I1_sim)}). PSS warn that this pattern can arise when the lagged levels of the regressors
          matter but food prices adjust weakly towards them. <strong>We therefore read the NARDL long-run coefficients as suggestive</strong> and lean
          on the dynamic multipliers and the linear ARDL, where both tests reject, for the existence of the equilibrium.
        </p>
        <Disclosure title="NARDL conditional error-correction output">
          <CoefTable rows={nardl.cec_equation.coefficients} highlight={["LEXR_POS**", "LEXR_NEG(-1)", "D(LEXR_NEG)"]} />
        </Disclosure>
      </div>

      <div className="mt-20">
        <SubHead k="Step 3 · Interactive" aside={<StatusBadge status={multipliers._meta.status} />}>
          The dynamic multipliers
        </SubHead>
        <p className="mb-8 max-w-3xl leading-relaxed text-paper-dim">
          The cumulative dynamic multiplier traces how food prices respond, month by month, to a permanent 1% move in the exchange rate — red for
          depreciation, green for appreciation (plotted as the response to a 1% <em>appreciation</em>, so symmetric pass-through would make the two
          lines mirror images). Switch to “Asymmetry” to see their difference and its 95% band.
        </p>
        <Panel>
          <MultiplierChart m={multipliers} />
          <SourceNote>{multipliers.band}. Computed from the levels form of NARDL({order.join(", ")}).</SourceNote>
        </Panel>
      </div>

      <div className="mt-20">
        <SubHead k="Step 4">Test for symmetry, not just compare numbers</SubHead>
        <div className="grid gap-10 lg:grid-cols-[1.2fr_1fr]">
          <Panel>
            <AsymmetryPanel
              lr={{
                dep: { coef: Lp.coef, lo: Lp.ci95_low, hi: Lp.ci95_high, p: Lp.p },
                app: { coef: Ln.coef, lo: Ln.ci95_low, hi: Ln.ci95_high, p: Ln.p },
              }}
              sr={{
                dep: { coef: bp.coef!, lo: ci(bp)[0], hi: ci(bp)[1], p: bp.p! },
                app: { coef: bn.coef!, lo: ci(bn)[0], hi: ci(bn)[1], p: bn.p! },
              }}
              lrTest={{ stat: `Wald χ²(1) = ${fmt(a.long_run.wald_chi2, 2)}`, p: a.long_run.p_chi2 }}
              srTest={{ stat: `F(1, ${a.short_run.F_impact_df[1]}) = ${fmt(a.short_run.F_impact, 2)}`, p: a.short_run.p_impact }}
            />
          </Panel>
          <div className="space-y-4">
            {wald.tests.map((t) => (
              <div key={t.id} className="border-t border-line pt-4">
                <div className="flex items-baseline justify-between gap-3">
                  <span className="font-mono text-[0.68rem] uppercase tracking-[0.14em] text-gold">{t.id.replace("_", " ")}</span>
                  <span className={`font-mono text-[0.68rem] uppercase ${t.decision?.startsWith("Reject") ? "text-gold" : "text-paper-dim"}`}>
                    {t.decision ?? "Not applicable"}
                  </span>
                </div>
                <p className="mt-2 text-sm text-paper">H₀: {t.null}</p>
                {t.value !== undefined ? (
                  <p className="num mt-1 text-sm text-paper-dim">
                    {t.statistic} = {fmt(t.value, 3)}, df = {Array.isArray(t.df) ? t.df.join(", ") : t.df}, p = {fmtP(t.p)}
                    {t.alt_value !== undefined ? ` · ${t.alt_statistic} = ${fmt(t.alt_value, 3)}, p = ${fmtP(t.alt_p)}` : ""}
                  </p>
                ) : (
                  <p className="mt-1 text-sm text-faint">{t.reason}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="mt-20 rounded-sm border border-gold/40 bg-ink p-6 sm:p-10">
        <div className="kicker">What the asymmetry investigation shows</div>
        <p className="mt-4 font-serif text-2xl leading-snug text-paper sm:text-3xl">{answer.answer.split(". ")[0]}.</p>
        <p className="mt-4 max-w-4xl leading-relaxed text-paper-dim">{answer.answer.split(". ").slice(1).join(". ")}</p>
        <p className="mt-4 max-w-4xl leading-relaxed text-paper-dim">
          In plain terms: depreciation is reliably followed by higher food prices (long-run L⁺ = {fmt(Lp.coef, 2)}, p = {fmtP(Lp.p)}). When the rupee
          recovers, prices do not come down in the same month; any reversal comes later and is too imprecisely estimated — with only{" "}
          {er.appreciating} appreciating months, mostly small — for us to say whether it eventually matches the rise. The data are consistent with
          “rockets and feathers” in the short run, but they do <em>not</em> prove a permanent long-run asymmetry.
        </p>
      </div>
    </Chapter>
  );
}
