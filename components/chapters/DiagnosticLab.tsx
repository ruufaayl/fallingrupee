"use client";

import { CheckCircle2, CircleAlert, Info } from "lucide-react";
import { useState } from "react";

import { StabilityChart } from "@/components/charts/ModelCharts";
import { Segmented } from "@/components/ui/Segmented";
import { fmt, fmtP } from "@/lib/format";
import type { DiagTest, Stability } from "@/lib/types";

type ModelKey = "OLS_LEVELS" | "ARDL_MAIN" | "NARDL_MAIN";
type Group = "Multicollinearity" | "Serial correlation" | "Heteroskedasticity" | "Normality" | "Functional form" | "Stability";

const MEANING: Record<string, [string, string]> = {
  // [if H0 not rejected, if rejected]
  "Breusch-Godfrey": ["Residuals show no leftover autocorrelation: the lag structure captures the dynamics, so standard errors are trustworthy.", "Residuals are autocorrelated: dynamics are missing and OLS standard errors are unreliable — add lags or use HAC errors."],
  "Breusch-Pagan-Godfrey": ["Residual variance does not depend on the regressors.", "Residual variance changes with the regressors: use heteroskedasticity-robust standard errors."],
  White: ["No evidence of general heteroskedasticity.", "General heteroskedasticity detected: coefficients stay unbiased but standard errors need correcting."],
  "ARCH LM": ["No volatility clustering in the residuals.", "Volatile months cluster together (ARCH): inference should use robust errors."],
  "Jarque-Bera": ["Residuals are consistent with a normal distribution.", "Residuals are not normal — driven by a few extreme months. With N > 100, t- and F-tests remain approximately valid; the May-2024 impulse dummy (robustness) restores normality."],
  "Ramsey RESET": ["No sign of omitted non-linearity: the log-linear form is adequate.", "Functional form may be misspecified."],
  "Durbin-Watson": ["", ""],
};

function meaning(t: DiagTest) {
  const key = Object.keys(MEANING).find((k) => t.test.startsWith(k));
  if (!key || key === "Durbin-Watson") return t.note ?? "";
  return MEANING[key][t.reject_5pct ? 1 : 0];
}

export function DiagnosticLab({
  diag,
  stability,
  vif,
  labels,
}: {
  diag: Record<ModelKey, DiagTest[]>;
  stability: Partial<Record<ModelKey, Stability>>;
  vif: { levels: { variable: string; vif: number; tolerance: number }[]; diffs: { variable: string; vif: number; tolerance: number }[]; nardl: { variable: string; vif: number; tolerance: number }[] };
  labels: Record<ModelKey, string>;
}) {
  const [model, setModel] = useState<ModelKey>("NARDL_MAIN");
  const [group, setGroup] = useState<Group>("Serial correlation");
  const tests = diag[model].filter((t) => t.group === group);
  const st = stability[model];

  const groups: Group[] = ["Multicollinearity", "Serial correlation", "Heteroskedasticity", "Normality", "Functional form", "Stability"];
  const score = (m: ModelKey) => {
    const ts = diag[m].filter((t) => t.reject_5pct !== undefined);
    return `${ts.filter((t) => !t.reject_5pct).length}/${ts.length}`;
  };

  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-4">
        <Segmented
          label="Model"
          value={model}
          onChange={setModel}
          options={(Object.keys(labels) as ModelKey[]).map((k) => ({ value: k, label: labels[k] }))}
        />
        <span className="font-mono text-[0.7rem] uppercase tracking-[0.12em] text-muted">
          Tests passed at 5%: <span className="text-paper">{score(model)}</span>
        </span>
      </div>

      <div className="mt-6 flex flex-wrap gap-2 border-b border-line" role="tablist" aria-label="Diagnostic group">
        {groups.map((g) => (
          <button
            key={g}
            role="tab"
            type="button"
            aria-selected={group === g}
            onClick={() => setGroup(g)}
            className={`-mb-px border-b-2 px-3 py-2.5 font-mono text-[0.68rem] uppercase tracking-[0.12em] transition-colors ${
              group === g ? "border-gold text-paper" : "border-transparent text-faint hover:text-paper-dim"
            }`}
          >
            {g}
          </button>
        ))}
      </div>

      <div className="mt-8" role="tabpanel">
        {group === "Multicollinearity" ? (
          <div className="grid gap-8 lg:grid-cols-3">
            {[
              { t: "Static OLS, log levels", rows: vif.levels },
              { t: "NARDL regressors, levels", rows: vif.nardl },
              { t: "First differences", rows: vif.diffs },
            ].map((b) => (
              <div key={b.t}>
                <div className="kicker mb-3">{b.t}</div>
                <div className="overflow-x-auto">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Regressor</th>
                      <th className="text-right">VIF</th>
                      <th className="text-right">Tolerance</th>
                    </tr>
                  </thead>
                  <tbody>
                    {b.rows.map((r) => (
                      <tr key={r.variable}>
                        <td>{r.variable}</td>
                        <td className={`n ${r.vif > 10 ? "text-rise" : ""}`}>{fmt(r.vif, 2)}</td>
                        <td className="n">{fmt(r.tolerance, 3)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                </div>
              </div>
            ))}
            <p className="text-sm leading-relaxed text-paper-dim lg:col-span-3">
              VIF above 10 (red) in levels reflects the shared upward trend of prices and the exchange rate, not a data error. It inflates standard
              errors in a static regression but does not bias the coefficients. We keep every variable because theory requires it; in differences
              — the scale of the short-run terms — all VIFs are below 2.
            </p>
          </div>
        ) : group === "Stability" ? (
          st ? (
            <div>
              <StabilityChart st={st} label={labels[model]} />
              <p className="mt-4 text-sm leading-relaxed text-paper-dim">
                CUSUM tracks the cumulative sum of recursive residuals: a drift outside the bands signals that coefficients changed during the sample.
                CUSUM of squares does the same for the residual variance.{" "}
                {st.cusumsq_within_bounds
                  ? "Both stay inside the 5% bands: no evidence of structural instability."
                  : `CUSUM of squares leaves the band (largest deviation ${fmt(st.cusumsq_max_dev, 3)} vs bound ${fmt(st.cusumsq_c0, 3)}, around ${st.cusumsq_max_dev_date}): the residual variance is not constant — calm early years, turbulent later ones — so the NARDL's standard errors and tests deserve caution.`}
              </p>
              <p className="mt-2 font-mono text-[0.64rem] text-faint">{st.method}</p>
            </div>
          ) : (
            <p className="text-paper-dim">Recursive stability tests are reported for the dynamic models (ARDL and NARDL).</p>
          )
        ) : tests.length === 0 ? (
          <p className="text-paper-dim">No tests in this group for this model.</p>
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            {tests.map((t) => {
              const isDW = t.test.startsWith("Durbin");
              const pass = isDW ? null : !t.reject_5pct;
              return (
                <article key={t.test} className="rounded-sm border border-line bg-ink/60 p-5">
                  <div className="flex items-start justify-between gap-3">
                    <h4 className="font-serif text-xl text-paper">{t.test}</h4>
                    {pass === null ? (
                      <Info className="h-5 w-5 shrink-0 text-muted" aria-label="indicative" />
                    ) : pass ? (
                      <CheckCircle2 className="h-5 w-5 shrink-0 text-fall" aria-label="passed" />
                    ) : (
                      <CircleAlert className="h-5 w-5 shrink-0 text-rise" aria-label="failed" />
                    )}
                  </div>
                  <dl className="mt-4 grid grid-cols-[auto_1fr] gap-x-4 gap-y-1.5 text-sm">
                    <dt className="font-mono text-[0.66rem] uppercase tracking-[0.12em] text-muted">H₀</dt>
                    <dd className="text-paper-dim">{t.null}</dd>
                    <dt className="font-mono text-[0.66rem] uppercase tracking-[0.12em] text-muted">H₁</dt>
                    <dd className="text-paper-dim">H₀ is false</dd>
                    <dt className="font-mono text-[0.66rem] uppercase tracking-[0.12em] text-muted">Statistic</dt>
                    <dd className="num text-paper">
                      {t.stat_name} = {fmt(t.stat, 3)}
                      {t.df !== undefined ? <span className="text-faint"> · df {Array.isArray(t.df) ? t.df.join(", ") : t.df}</span> : null}
                    </dd>
                    <dt className="font-mono text-[0.66rem] uppercase tracking-[0.12em] text-muted">p-value</dt>
                    <dd className="num text-paper">{t.p === null ? "—" : fmtP(t.p)}</dd>
                    <dt className="font-mono text-[0.66rem] uppercase tracking-[0.12em] text-muted">Decision</dt>
                    <dd className={pass === null ? "text-paper-dim" : pass ? "text-fall" : "text-rise"}>
                      {pass === null ? "Indicative only" : pass ? "Do not reject H₀ at 5%" : "Reject H₀ at 5%"}
                    </dd>
                  </dl>
                  <p className="mt-4 border-t border-line pt-3 text-sm leading-relaxed text-paper-dim">{meaning(t)}</p>
                </article>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
