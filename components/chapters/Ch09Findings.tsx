import { FitChart, ForestChart } from "@/components/charts/ModelCharts";
import { Reveal } from "@/components/animations/Reveal";
import { Chapter, Panel, SourceNote, SubHead } from "@/components/ui/Chapter";
import { SigBadge, StatusBadge } from "@/components/ui/StatusBadge";
import { ardl, findings, longRun, nardl, ols, robustness } from "@/lib/registry";
import { fmt, fmtP, stars } from "@/lib/format";

export function Ch09Findings() {
  const Lx = longRun(ardl, "LEXR");
  const Lp = longRun(nardl, "LEXR_POS");
  const Ln = longRun(nardl, "LEXR_NEG");
  const a = nardl.asymmetry!;
  const oc = (t: string) => ols.coefficients.find((c) => c.term === t)!;
  const rc = findings.robustness_counts;

  const tiles = [
    { k: "Long-run pass-through, linear ARDL", v: fmt(Lx.coef, 2), s: `p ${fmtP(Lx.p)} · 95% CI [${fmt(Lx.ci95_low, 2)}, ${fmt(Lx.ci95_high, 2)}]`, sig: Lx.p },
    { k: "Long-run depreciation pass-through, NARDL (L⁺)", v: fmt(Lp.coef, 2), s: `p ${fmtP(Lp.p)} · 95% CI [${fmt(Lp.ci95_low, 2)}, ${fmt(Lp.ci95_high, 2)}]`, sig: Lp.p },
    { k: "Long-run appreciation coefficient, NARDL (L⁻)", v: fmt(Ln.coef, 2), s: `p ${fmtP(Ln.p)} · 95% CI [${fmt(Ln.ci95_low, 2)}, ${fmt(Ln.ci95_high, 2)}]`, sig: Ln.p },
    { k: "Speed of adjustment (ARDL ECM)", v: fmt(ardl.ecm_regression.speed_of_adjustment, 3), s: `half-life ${fmt(ardl.ecm_regression.half_life_months, 1)} months`, sig: ardl.ecm_regression.speed_p },
    { k: "Long-run symmetry (Wald χ²)", v: fmtP(a.long_run.p_chi2), s: `χ²(1) = ${fmt(a.long_run.wald_chi2, 2)} — p-value shown`, sig: null },
    { k: "Impact symmetry (F)", v: fmtP(a.short_run.p_impact), s: `F = ${fmt(a.short_run.F_impact, 2)} — p-value shown`, sig: null },
  ];

  const rows: { v: string; o?: string; a?: string; n?: string; np?: number; ap?: number; op?: number }[] = [
    { v: "Exchange rate (symmetric)", o: fmt(oc("LEXR").coef, 3), op: oc("LEXR").p!, a: fmt(Lx.coef, 3), ap: Lx.p },
    { v: "Depreciation, EXR⁺", n: fmt(Lp.coef, 3), np: Lp.p },
    { v: "Appreciation, EXR⁻", n: fmt(Ln.coef, 3), np: Ln.p },
    { v: "World food prices (FAO)", o: fmt(oc("LGFOOD").coef, 3), op: oc("LGFOOD").p!, a: fmt(longRun(ardl, "LGFOOD").coef, 3), ap: longRun(ardl, "LGFOOD").p, n: fmt(longRun(nardl, "LGFOOD").coef, 3), np: longRun(nardl, "LGFOOD").p },
    { v: "Energy: transport CPI", o: fmt(oc("LTRANSCPI").coef, 3), op: oc("LTRANSCPI").p!, a: fmt(longRun(ardl, "LTRANSCPI").coef, 3), ap: longRun(ardl, "LTRANSCPI").p, n: fmt(longRun(nardl, "LTRANSCPI").coef, 3), np: longRun(nardl, "LTRANSCPI").p },
  ];

  return (
    <Chapter
      id="findings"
      n={9}
      tone="graphite"
      kicker="The Findings"
      title={<>What the evidence supports — and what it does not.</>}
      intro={
        <p>
          The results below are read directly from the results registry. Each is labelled with its verification status; significance is judged at
          the 5% level; elasticities are percentage responses of food prices to a 1% change in the driver.
        </p>
      }
    >
      <div className="grid gap-px overflow-hidden rounded-sm border border-line bg-line sm:grid-cols-2 lg:grid-cols-3">
        {tiles.map((t) => (
          <div key={t.k} className="bg-ink p-6">
            <div className="font-mono text-[0.64rem] uppercase leading-relaxed tracking-[0.14em] text-muted">{t.k}</div>
            <div className="num mt-3 text-4xl text-paper">{t.v}</div>
            <div className="mt-2 flex flex-wrap items-center gap-2">
              <span className="num text-[0.72rem] text-faint">{t.s}</span>
              {t.sig !== null ? <SigBadge p={t.sig} /> : null}
            </div>
          </div>
        ))}
      </div>
      <div className="mt-4 flex flex-wrap gap-3">
        <StatusBadge status={ardl._meta.status} />
        <span className="font-mono text-[0.66rem] text-faint">Python/statsmodels estimates; EViews programs in /eviews reproduce each specification.</span>
      </div>

      <div className="mt-20">
        <SubHead k="Table 9.1">Long-run coefficients across models</SubHead>
        <div className="overflow-x-auto">
          <table className="data-table">
            <thead>
              <tr>
                <th>Driver</th>
                <th className="text-right">Static OLS</th>
                <th className="text-right">ARDL({ardl.selection.chosen_order.join(",")})</th>
                <th className="text-right">NARDL({nardl.selection.chosen_order.join(",")})</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.v}>
                  <td className="text-paper">{r.v}</td>
                  <td className="n">{r.o ? <>{r.o}<span className="text-gold">{stars(r.op)}</span></> : "—"}</td>
                  <td className="n">{r.a ? <>{r.a}<span className="text-gold">{stars(r.ap)}</span></> : "—"}</td>
                  <td className="n">{r.n ? <>{r.n}<span className="text-gold">{stars(r.np)}</span></> : "—"}</td>
                </tr>
              ))}
              <tr>
                <td className="text-paper-dim">Bounds test (F / t)</td>
                <td className="n">Engle-Granger p {fmtP(ols.spurious_regression_check.engle_granger.p)}</td>
                <td className="n">{fmt(ardl.bounds_test.F, 2)} / {fmt(ardl.bounds_test.t, 2)}</td>
                <td className="n">{fmt(nardl.bounds_test.F, 2)} / {fmt(nardl.bounds_test.t, 2)}</td>
              </tr>
              <tr>
                <td className="text-paper-dim">Speed of adjustment</td>
                <td className="n">—</td>
                <td className="n">{fmt(ardl.ecm_regression.speed_of_adjustment, 3)}</td>
                <td className="n">{fmt(nardl.ecm_regression.speed_of_adjustment, 3)}</td>
              </tr>
              <tr>
                <td className="text-paper-dim">Adj. R² (levels) · N</td>
                <td className="n">{fmt(ols.adj_r2, 3)} · {ols.nobs}</td>
                <td className="n">{fmt(ardl.levels_equation.adj_r2, 4)} · {ardl.sample.nobs}</td>
                <td className="n">{fmt(nardl.levels_equation.adj_r2, 4)} · {nardl.sample.nobs}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <SourceNote>Static OLS coefficients are contemporaneous and likely spurious (Chapter 06.1); they are shown only for comparison. *** p&lt;0.01, ** p&lt;0.05, * p&lt;0.10.</SourceNote>
      </div>

      <div className="mt-20">
        <SubHead k="Answers">The research questions, answered</SubHead>
        <div className="grid gap-6 lg:grid-cols-2">
          {findings.answers.map((x, i) => (
            <Reveal key={x.q} delay={i * 0.04}>
              <article className="h-full border-t border-gold-soft pt-5">
                <div className="flex flex-wrap items-baseline justify-between gap-2">
                  <h4 className="font-serif text-xl text-paper">{x.q}</h4>
                  <span className="font-mono text-[0.62rem] uppercase tracking-[0.12em] text-gold">{x.strength}</span>
                </div>
                <p className="mt-3 text-[0.95rem] leading-relaxed text-paper-dim">{x.answer}</p>
                <p className="mt-2 font-mono text-[0.62rem] text-faint">{x.model}</p>
              </article>
            </Reveal>
          ))}
        </div>
      </div>

      <div className="mt-20 grid gap-10 lg:grid-cols-[1.2fr_1fr]">
        <div>
          <SubHead k="Figure 9.2">Robustness of the long-run pass-through</SubHead>
          <Panel>
            <ForestChart rows={robustness.nardl_specifications.filter((r) => r.id !== "HEADLINE")} />
            <SourceNote>
              Filled marker: significant at 5%. Depreciation (L⁺) is positive in {rc.pos_positive}/{rc.n_specs} food-CPI specifications and significant in{" "}
              {rc.pos_significant}; appreciation (L⁻) is significant in {rc.neg_significant}.
            </SourceNote>
          </Panel>
        </div>
        <div>
          <SubHead k="Figure 9.3">How well the NARDL tracks food prices</SubHead>
          <Panel>
            <FitChart dates={nardl.fitted.dates} actual={nardl.fitted.actual} fitted={nardl.fitted.fitted} />
          </Panel>
          <div className="mt-8 grid gap-4 text-sm">
            <div className="border-l-2 border-fall pl-4 text-paper-dim">
              <strong className="text-paper">Statistically significant:</strong> long-run pass-through from depreciation; world food prices (ARDL);
              energy (NARDL); error correction; short-run impact asymmetry.
            </div>
            <div className="border-l-2 border-line-strong pl-4 text-paper-dim">
              <strong className="text-paper">Not significant:</strong> long-run appreciation effect; long-run asymmetry (baseline); energy in the
              linear ARDL.
            </div>
            <div className="border-l-2 border-gold pl-4 text-paper-dim">
              <strong className="text-paper">Interpretation, not proof:</strong> these are conditional associations in observational time series, not
              causal effects identified by an experiment or instrument.
            </div>
          </div>
        </div>
      </div>
    </Chapter>
  );
}
