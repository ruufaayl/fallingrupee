import { CheckCircle2, CircleAlert, Info } from "lucide-react";

import { Reveal } from "@/components/animations/Reveal";
import { FitChart } from "@/components/charts/ModelCharts";
import { Chapter, Panel, SourceNote, SubHead } from "@/components/ui/Chapter";
import { regression, simple } from "@/lib/simple";

const GROUPS = [
  { key: "Data", title: "Before the regression", sub: "Look at the data and check it is safe to use" },
  { key: "Regression", title: "The regression", sub: "Estimate the equation and test the coefficients" },
  { key: "Diagnostics", title: "After the regression", sub: "Check the model’s assumptions hold" },
];

export function S7Tests() {
  let n = 0;
  return (
    <Chapter
      id="tests"
      n={7}
      tone="graphite"
      kicker="Tests We Ran"
      title={<>{simple.tests.length} standard tests, in three steps.</>}
      intro={<p>Each card says what the test checks, its H₀, our result and what it means. Green tick = the model passed.</p>}
    >
      {GROUPS.map((g) => (
        <div key={g.key} className="mb-14">
          <SubHead k={g.sub}>{g.title}</SubHead>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {simple.tests
              .filter((t) => t.group === g.key)
              .map((t) => {
                n += 1;
                return (
                  <Reveal key={t.name}>
                    <article className="flex h-full flex-col rounded-sm border border-line bg-ink p-5">
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <span className="num text-sm text-gold">{String(n).padStart(2, "0")}</span>
                          <h3 className="mt-1 font-serif text-xl leading-tight text-paper">{t.name}</h3>
                        </div>
                        {t.pass === null ? (
                          <Info className="h-5 w-5 shrink-0 text-muted" aria-label="descriptive" />
                        ) : t.pass ? (
                          <CheckCircle2 className="h-5 w-5 shrink-0 text-fall" aria-label="passed" />
                        ) : (
                          <CircleAlert className="h-5 w-5 shrink-0 text-rise" aria-label="problem found" />
                        )}
                      </div>
                      <p className="mt-3 text-sm text-paper-dim">{t.checks}</p>
                      <dl className="mt-4 space-y-1.5 border-t border-line pt-3 text-[0.82rem]">
                        {t.h0 ? (
                          <div>
                            <dt className="inline font-mono text-[0.62rem] uppercase tracking-[0.12em] text-faint">H₀ · </dt>
                            <dd className="inline text-paper-dim">{t.h0}</dd>
                          </div>
                        ) : null}
                        <div>
                          <dt className="inline font-mono text-[0.62rem] uppercase tracking-[0.12em] text-faint">Result · </dt>
                          <dd className="num inline text-paper">{t.result}</dd>
                        </div>
                        <div>
                          <dt className="inline font-mono text-[0.62rem] uppercase tracking-[0.12em] text-faint">Decision · </dt>
                          <dd className="inline text-gold">{t.decision}</dd>
                        </div>
                      </dl>
                      <p className="mt-auto pt-4 text-sm leading-relaxed text-paper">{t.meaning}</p>
                    </article>
                  </Reveal>
                );
              })}
          </div>
        </div>
      ))}

      <div className="grid gap-10 lg:grid-cols-2">
        <div>
          <SubHead k="Table 3">Stationarity: ADF unit root test</SubHead>
          <div className="overflow-x-auto">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Variable</th>
                  <th className="text-right">Level p</th>
                  <th>Level</th>
                  <th className="text-right">% change p</th>
                  <th>% change</th>
                </tr>
              </thead>
              <tbody>
                {simple.stationarity.map((u) => (
                  <tr key={u.name}>
                    <td className="text-paper">{u.name}</td>
                    <td className="n">{u.level_p.toFixed(3)}</td>
                    <td className="text-rise">{u.level_result}</td>
                    <td className="n">{u.change_p < 0.001 ? "< 0.001" : u.change_p.toFixed(3)}</td>
                    <td className="text-fall">{u.change_result}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="mt-3 text-sm text-paper-dim">
            H₀: non-stationary. Levels keep trending (p &gt; 0.05), so we use monthly % changes, which are stationary (p &lt; 0.05). Intercept included; lag
            length chosen by the Schwarz criterion.
          </p>
        </div>
        <div>
          <SubHead k="Table 4">Multicollinearity: variance inflation factor</SubHead>
          <div className="overflow-x-auto">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Independent variable</th>
                  <th className="text-right">VIF</th>
                  <th className="text-right">Tolerance</th>
                </tr>
              </thead>
              <tbody>
                {simple.vif.map((v) => (
                  <tr key={v.name}>
                    <td className="text-paper">{v.name}</td>
                    <td className="n">{v.vif.toFixed(2)}</td>
                    <td className="n">{v.tolerance.toFixed(3)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="mt-3 text-sm text-paper-dim">Rule of thumb: VIF above 10 means a problem. All our VIFs are close to 1 — no multicollinearity.</p>
        </div>
      </div>

      <div className="mt-16">
        <SubHead k="Graph 5">Actual vs predicted food inflation</SubHead>
        <Panel>
          <FitChart dates={regression.fitted.dates} actual={regression.fitted.actual} fitted={regression.fitted.fitted} yName="Food inflation, % per month" fitName="Predicted by the regression" />
          <SourceNote>
            The gap between the two lines is the error. Diagnostic tests check that these errors are random: no autocorrelation (DW ={" "}
            {regression.diagnostics.durbin_watson.toFixed(2)}), constant variance and a normal shape.
          </SourceNote>
        </Panel>
      </div>
    </Chapter>
  );
}
