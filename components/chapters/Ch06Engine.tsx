import { EcmDecay } from "@/components/charts/ModelCharts";
import { BoundsLine } from "@/components/econometrics/BoundsLine";
import { CoefTable } from "@/components/econometrics/CoefTable";
import { Equation } from "@/components/econometrics/Equation";
import { MethodStep, Result } from "@/components/econometrics/MethodStep";
import { Chapter, Panel, SourceNote } from "@/components/ui/Chapter";
import { Disclosure } from "@/components/ui/Disclosure";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { ardl, longRun, ols, stationarity } from "@/lib/registry";
import { fmt, fmtP, VAR_LABEL } from "@/lib/format";

const UR_VARS = ["LFOODCPI", "LEXR", "LGFOOD", "LTRANSCPI", "LEXR_POS", "LEXR_NEG"];

function ur(variable: string, form: string, test: string, det = "c", rule?: string) {
  return stationarity.tests.find(
    (t) => t.variable === variable && t.form === form && t.test === test && t.deterministic === det && (!rule || t.lag_rule === rule),
  );
}

export function Ch06Engine() {
  const eg = ols.spurious_regression_check.engle_granger;
  const b = ardl.bounds_test;
  const ecm = ardl.ecm_regression;
  const Lx = longRun(ardl, "LEXR");
  const Lg = longRun(ardl, "LGFOOD");
  const Lt = longRun(ardl, "LTRANSCPI");
  const order = ardl.selection.chosen_order;
  const st = ardl._meta.status;
  const cointOK = b.decision_F_5pct_asymptotic === "reject" && b.decision_t_5pct_asymptotic === "reject";
  const allI1 = UR_VARS.every((v) => stationarity.summary[v].integration_order === "I(1)");

  return (
    <Chapter
      id="engine"
      n={6}
      kicker="The Econometric Engine"
      title={<>Six steps from correlation to equilibrium.</>}
      intro={
        <>
          <p>
            The chart in Chapter 02 shows co-movement. Turning that into evidence requires care, because prices, the exchange rate and world food
            prices all trend upward — and trending series can appear related when they are not. Each step below exists to rule out a specific way
            of fooling ourselves.
          </p>
          <p className="font-mono text-[0.72rem] text-faint">
            Estimation: {ardl._meta.engine.software}, statsmodels {ardl._meta.engine.packages.statsmodels}. EViews programs reproducing every step are
            in /eviews.
          </p>
        </>
      }
    >
      {/* 1 ── OLS */}
      <MethodStep
        n="6.1"
        title="Baseline OLS"
        aside={<StatusBadge status={ols._meta.status} />}
        what="Fits a straight-line relationship between the log of food prices and the logs of the three drivers, all measured in the same month."
        why="It is the natural first look and gives interpretable elasticities. It is also the benchmark the dynamic models must beat."
        nullH="Each coefficient is zero (t-test); all slopes are jointly zero (F-test)."
        read="A coefficient of 0.3 on ln EXR means a 1% higher exchange rate is associated with 0.3% higher food prices in the same month."
      >
        <Equation tex={String.raw`\ln \text{FOOD}_t = \beta_0 + \beta_1 \ln \text{EXR}_t + \beta_2 \ln \text{GFOOD}_t + \beta_3 \ln \text{ENERGY}_t + u_t`} />
        <div className="mt-6 grid gap-8 lg:grid-cols-[1.4fr_1fr]">
          <Panel>
            <CoefTable rows={ols.coefficients} highlight={["LEXR", "LGFOOD", "LTRANSCPI"]} caption={`OLS, N = ${ols.nobs}`} />
          </Panel>
          <dl className="grid grid-cols-2 content-start gap-px overflow-hidden rounded-sm border border-line bg-line">
            {[
              ["R²", fmt(ols.r2, 3)],
              ["Adj. R²", fmt(ols.adj_r2, 3)],
              ["F-statistic", fmt(ols.F, 1)],
              ["Prob(F)", fmtP(ols.F_p)],
              ["Durbin-Watson", fmt(ols.dw, 3)],
              ["Engle-Granger τ", `${fmt(eg.stat, 2)} (p ${fmtP(eg.p)})`],
            ].map(([k, v]) => (
              <div key={k} className="bg-graphite p-4">
                <dt className="font-mono text-[0.62rem] uppercase tracking-[0.14em] text-muted">{k}</dt>
                <dd className="num mt-1 text-lg text-paper">{v}</dd>
              </div>
            ))}
          </dl>
        </div>
        <Result>
          The fit looks spectacular (R² = {fmt(ols.r2, 3)}) — and that is the warning. The Durbin-Watson statistic is only {fmt(ols.dw, 2)}, far below
          R², the textbook signature of a <strong>possibly spurious regression</strong> (Granger &amp; Newbold, 1974), and the Engle-Granger test
          cannot reject that the residuals have a unit root (p = {fmtP(eg.p)}). Static OLS ignores dynamics and trending data; we need to test
          stationarity and model the adjustment explicitly.
        </Result>
      </MethodStep>

      {/* 2 ── Stationarity */}
      <MethodStep
        n="6.2"
        title="Stationarity: ADF, PP and KPSS"
        aside={<StatusBadge status={stationarity._meta.status} />}
        what="Asks whether each series wanders without a fixed mean (a unit root, I(1)) or keeps returning to a stable level (stationary, I(0))."
        why="Regressions on unit-root series can be spurious; and the ARDL bounds test is valid for I(0) or I(1) regressors but breaks down if any series is I(2)."
        nullH={<>ADF &amp; PP: the series has a unit root. KPSS (reverse): the series is stationary.</>}
        read="Reject the unit-root null (p < 0.05) ⇒ stationary. If the level is non-stationary but the first difference is stationary, the series is I(1)."
      >
        <div className="overflow-x-auto">
          <table className="data-table">
            <thead>
              <tr>
                <th>Variable</th>
                <th className="text-right">ADF level (c)</th>
                <th className="text-right">ADF level (c+t)</th>
                <th className="text-right">PP level</th>
                <th className="text-right">KPSS level</th>
                <th className="text-right">ADF Δ</th>
                <th className="text-right">PP Δ</th>
                <th className="text-right">ADF Δ²</th>
                <th>Order</th>
              </tr>
            </thead>
            <tbody>
              {UR_VARS.map((v) => {
                const cell = (r?: { stat: number; p: number }) => (r ? `${fmt(r.stat, 2)} (${fmtP(r.p)})` : "—");
                return (
                  <tr key={v}>
                    <td className="text-paper">{VAR_LABEL[v] ?? v}</td>
                    <td className="n">{cell(ur(v, "level", "ADF", "c", "AIC"))}</td>
                    <td className="n">{cell(ur(v, "level", "ADF", "ct", "AIC"))}</td>
                    <td className="n">{cell(ur(v, "level", "PP"))}</td>
                    <td className="n">{cell(ur(v, "level", "KPSS"))}</td>
                    <td className="n">{cell(ur(v, "first_difference", "ADF", "c", "BIC"))}</td>
                    <td className="n">{cell(ur(v, "first_difference", "PP"))}</td>
                    <td className="n">{cell(ur(v, "second_difference", "ADF", "c", "AIC"))}</td>
                    <td className="font-mono text-[0.78rem] text-gold">{stationarity.summary[v].integration_order}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
        <SourceNote>
          Statistic (p-value). ADF lag length by AIC (levels) and SIC (differences), max 12; PP with Newey-West bandwidth; KPSS p-values are
          bounded to [0.01, 0.10]. {stationarity.rule}
        </SourceNote>
        <Disclosure title={`Full unit-root battery (${stationarity.tests.length} tests)`}>
          <div className="max-h-[420px] overflow-auto">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Variable</th>
                  <th>Form</th>
                  <th>Test</th>
                  <th>Det.</th>
                  <th>Lags</th>
                  <th className="text-right">Stat</th>
                  <th className="text-right">p</th>
                  <th className="text-right">5% crit.</th>
                  <th>Reject H₀ (5%)</th>
                </tr>
              </thead>
              <tbody>
                {stationarity.tests.map((t, i) => (
                  <tr key={i}>
                    <td>{t.variable}</td>
                    <td>{t.form.replace("_", " ")}</td>
                    <td>{t.test}</td>
                    <td>{t.deterministic}</td>
                    <td className="n">{t.lags} {t.lag_rule === "AIC" || t.lag_rule === "BIC" ? `(${t.lag_rule})` : ""}</td>
                    <td className="n">{fmt(t.stat, 3)}</td>
                    <td className="n">{fmtP(t.p)}</td>
                    <td className="n">{fmt(t.crit["5%"], 3)}</td>
                    <td>{t.reject_5pct ? "yes" : "no"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Disclosure>
        <Result>
          {allI1 ? (
            <>
              Every variable is <strong>I(1)</strong>: non-stationary in levels, stationary after one difference
            </>
          ) : (
            <>Integration orders are mixed (see table)</>
          )}
          , and none is I(2) — so the ARDL bounds approach is admissible ({stationarity.bounds_admissible ? "check passed" : "check failed"}). For the exchange rate the ADF test on the
          first difference with AIC-chosen lags is borderline, but ADF with SIC lags and Phillips-Perron both reject the unit root decisively; the
          bounds test is robust to either verdict because it accepts a mix of I(0) and I(1) regressors.
        </Result>
      </MethodStep>

      {/* 3 ── Lag selection */}
      <MethodStep
        n="6.3"
        title="Lag selection"
        aside={<StatusBadge status={st} />}
        what={`Estimates every combination of up to ${ardl.selection.max_lags} monthly lags of food prices and each driver (${ardl.selection.models_evaluated} models) on a common sample and ranks them.`}
        why="Too few lags leave autocorrelation and omit slow pass-through; too many waste degrees of freedom. Information criteria balance fit against complexity."
        read="Lower is better. AIC favours richer dynamics; SIC (BIC) penalises extra parameters more heavily; HQ sits between."
      >
        <div className="overflow-x-auto">
          <table className="data-table">
            <thead>
              <tr>
                <th>Rank</th>
                <th>ARDL(p, q_EXR, q_GFOOD, q_ENERGY)</th>
                <th className="text-right">AIC</th>
                <th className="text-right">SIC</th>
                <th className="text-right">HQ</th>
                <th className="text-right">Adj. R²</th>
              </tr>
            </thead>
            <tbody>
              {ardl.selection.top_models.slice(0, 8).map((m, i) => (
                <tr key={m.order.join()} className={i === 0 ? "text-paper" : "text-paper-dim"}>
                  <td className="num">{i + 1}</td>
                  <td className="num">({m.order.join(", ")}){i === 0 ? " ← selected" : ""}</td>
                  <td className="n">{fmt(m.aic, 4)}</td>
                  <td className="n">{fmt(m.sic, 4)}</td>
                  <td className="n">{fmt(m.hq, 4)}</td>
                  <td className="n">{fmt(m.adj_r2, 4)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <Result>
          AIC selects <strong>ARDL({order.join(", ")})</strong>: {order[0]} lags of food prices, {order[1]} of the exchange rate, {order[2]} of world
          food prices and {order[3]} of energy. Eleven monthly seasonal dummies are included as fixed regressors; they are jointly significant
          (F = {fmt(ardl.levels_equation.seasonal_dummies_joint_F, 2)}, p = {fmtP(ardl.levels_equation.seasonal_dummies_joint_p)}).
        </Result>
      </MethodStep>

      {/* 4 ── ARDL & bounds */}
      <MethodStep
        n="6.4"
        title="ARDL and the bounds test"
        aside={<StatusBadge status={st} />}
        what="Rewrites the ARDL as an error-correction model and asks whether the lagged levels of food prices and its drivers matter jointly — that is, whether a long-run equilibrium exists."
        why="Pesaran, Shin & Smith (2001) show the test is valid whether regressors are I(0) or I(1), and it works well in samples of our size."
        nullH="No long-run level relationship: ρ = θ_EXR = θ_GFOOD = θ_ENERGY = 0."
        read="Above the I(1) bound ⇒ cointegration. Below the I(0) bound ⇒ none. Between ⇒ inconclusive. The t-test on ρ must also clear its bound."
      >
        <Equation
          tex={String.raw`\Delta \ln \text{FOOD}_t = c + \rho\,\ln \text{FOOD}_{t-1} + \sum_j \theta_j\, x_{j,t-1} + \sum_{i=1}^{p-1}\alpha_i\,\Delta \ln \text{FOOD}_{t-i} + \sum_j\sum_{l=0}^{q_j-1}\pi_{jl}\,\Delta x_{j,t-l} + \gamma' S_t + \varepsilon_t`}
          label="Conditional error-correction form (PSS case III: unrestricted intercept, no trend); Sₜ = monthly dummies."
        />
        <div className="mt-8 grid gap-8 lg:grid-cols-2">
          <Panel>
            <BoundsLine b={b} kind="F" />
          </Panel>
          <Panel>
            <BoundsLine b={b} kind="t" />
          </Panel>
        </div>
        {b.finite_sample ? (
          <SourceNote>
            Finite-sample 5% bounds from {b.finite_sample_nsim?.toLocaleString("en-GB")} Monte Carlo draws at n = {b.finite_sample_nobs}: F{" "}
            {fmt(b.finite_sample["5%"].F_I0, 2)} / {fmt(b.finite_sample["5%"].F_I1, 2)}, t {fmt(b.finite_sample["5%"].t_I0, 2)} /{" "}
            {fmt(b.finite_sample["5%"].t_I1, 2)}. Simulated p-value of F against the I(1) bound: {fmtP(b.p_value_F_I1_sim)}.
          </SourceNote>
        ) : null}
        <Result>
          F = {fmt(b.F, 2)} ({b.decision_F_5pct_asymptotic} at 5%, asymptotic; {b.decision_F_5pct_finite ?? "n/a"} with finite-sample bounds) and t ={" "}
          {fmt(b.t, 2)} ({b.decision_t_5pct_asymptotic}; {b.decision_t_5pct_finite ?? "n/a"}).{" "}
          {cointOK ? (
            <strong>Food prices, the exchange rate, world food prices and energy costs share a long-run equilibrium.</strong>
          ) : (
            <strong>The evidence for a long-run equilibrium is not conclusive on both tests.</strong>
          )}
        </Result>
      </MethodStep>

      {/* 5 ── Long run vs short run */}
      <MethodStep
        n="6.5"
        title="Long run versus short run"
        aside={<StatusBadge status={st} />}
        what="The long-run coefficients describe where food prices settle once all adjustment is complete (L = −θ/ρ). The short-run coefficients describe how prices move in the months along the way."
        why="Pass-through is gradual. A shock can have a small immediate effect and a large eventual one, or the reverse."
        nullH="Each long-run coefficient is zero (t-test with delta-method standard errors)."
        read={`Long-run L = ${fmt(Lx.coef, 2)} on ln EXR: a permanent 1% depreciation is associated with food prices ${fmt(Lx.coef, 2)}% higher once adjustment is complete.`}
      >
        <Equation tex={String.raw`\ln \text{FOOD}^{*} = L_c + L_{\text{EXR}}\ln \text{EXR} + L_{\text{GFOOD}}\ln \text{GFOOD} + L_{\text{ENERGY}}\ln \text{ENERGY},\qquad L_j = -\theta_j/\rho`} />
        <div className="mt-6 grid gap-8 lg:grid-cols-2">
          <div>
            <div className="kicker mb-3">Long-run (levels) equation</div>
            <div className="overflow-x-auto">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Variable</th>
                  <th className="text-right">L</th>
                  <th className="text-right">s.e.</th>
                  <th className="text-right">p</th>
                  <th className="text-right">95% CI</th>
                </tr>
              </thead>
              <tbody>
                {ardl.long_run.map((l) => (
                  <tr key={l.variable}>
                    <td className="text-paper">{VAR_LABEL[`${l.variable}`] ?? l.variable}</td>
                    <td className="n">{fmt(l.coef, 3)}</td>
                    <td className="n">{fmt(l.se, 3)}</td>
                    <td className="n">{fmtP(l.p)}</td>
                    <td className="n">
                      [{fmt(l.ci95_low, 2)}, {fmt(l.ci95_high, 2)}]
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            </div>
          </div>
          <div>
            <div className="kicker mb-3">Short-run dynamics (conditional EC form)</div>
            <CoefTable rows={ardl.cec_equation.coefficients.filter((c) => c.term.startsWith("D("))} />
          </div>
        </div>
        <Result>
          In the long run, a 1% higher exchange rate is associated with <strong>{fmt(Lx.coef, 2)}% higher food prices</strong> (p = {fmtP(Lx.p)}) and
          1% higher world food prices with <strong>{fmt(Lg.coef, 2)}%</strong> (p = {fmtP(Lg.p)}). The energy proxy is positive ({fmt(Lt.coef, 2)}) but not
          statistically significant (p = {fmtP(Lt.p)}). Pass-through is incomplete: well under one-for-one.
        </Result>
      </MethodStep>

      {/* 6 ── ECM */}
      <MethodStep
        n="6.6"
        title="The error-correction mechanism"
        aside={<StatusBadge status={st} />}
        what="Measures how quickly food prices close the gap when they are away from their long-run equilibrium."
        why="It turns 'cointegration exists' into an economically meaningful speed — and a valid ECM coefficient (negative, between −1 and 0) confirms the equilibrium is stable."
        nullH="No error correction: the coefficient on ECTₜ₋₁ is zero."
        read={`λ = ${fmt(ecm.speed_of_adjustment, 2)} means about ${fmt(-100 * ecm.speed_of_adjustment, 0)}% of last month’s disequilibrium is corrected this month.`}
      >
        <Equation tex={String.raw`\Delta \ln \text{FOOD}_t = \text{short-run terms} + \lambda\, \text{ECT}_{t-1} + \varepsilon_t,\qquad \text{ECT}_{t-1} = \ln \text{FOOD}_{t-1} - \ln \text{FOOD}^{*}_{t-1}`} />
        <div className="mt-6 grid gap-8 lg:grid-cols-[1fr_1.3fr]">
          <dl className="grid grid-cols-2 content-start gap-px overflow-hidden rounded-sm border border-line bg-line">
            {[
              ["Speed of adjustment λ", fmt(ecm.speed_of_adjustment, 4)],
              ["p-value", fmtP(ecm.speed_p)],
              ["Half-life (months)", fmt(ecm.half_life_months, 1)],
              ["ECM adj. R²", fmt(ecm.adj_r2, 3)],
            ].map(([k, v]) => (
              <div key={k} className="bg-graphite p-5">
                <dt className="font-mono text-[0.62rem] uppercase tracking-[0.14em] text-muted">{k}</dt>
                <dd className="num mt-1 text-2xl text-paper">{v}</dd>
              </div>
            ))}
          </dl>
          <Panel>
            <EcmDecay rho={ecm.speed_of_adjustment} label="Linear ARDL" />
          </Panel>
        </div>
        <Disclosure title="ECM regression output">
          <CoefTable rows={ecm.coefficients} highlight={["CointEq(-1)"]} />
        </Disclosure>
        <Result>
          λ = {fmt(ecm.speed_of_adjustment, 3)} is negative, highly significant and well inside (−1, 0): about {fmt(-100 * ecm.speed_of_adjustment, 0)}% of
          any gap closes each month, so half of a shock’s deviation from equilibrium is gone after roughly {fmt(ecm.half_life_months, 1)} months. Note
          that the p-value of λ follows a non-standard distribution; the PSS t-bound in step 6.4 is the proper test.
        </Result>
      </MethodStep>
    </Chapter>
  );
}
