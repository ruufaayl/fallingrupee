import { CheckCircle2, CircleAlert, Info } from "lucide-react";

import { Reveal } from "@/components/animations/Reveal";
import { StabilityChart } from "@/components/charts/ModelCharts";
import { BoundsLine } from "@/components/econometrics/BoundsLine";
import { Chapter, Panel, SubHead } from "@/components/ui/Chapter";
import { ardl } from "@/lib/registry";
import { simple } from "@/lib/simple";

export function S7Tests() {
  return (
    <Chapter
      id="tests"
      n={7}
      tone="graphite"
      kicker="Tests We Ran"
      title={<>Eleven checks, in the order we ran them.</>}
      intro={<p>Each card says what the test checks, its H₀, the result and what it means. Green = the model passed; red = a problem was found.</p>}
    >
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {simple.tests.map((t, i) => (
          <Reveal key={t.name} delay={(i % 3) * 0.05}>
            <article className="flex h-full flex-col rounded-sm border border-line bg-ink p-5">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <span className="num text-sm text-gold">{String(i + 1).padStart(2, "0")}</span>
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
        ))}
      </div>

      <div className="mt-16 grid gap-10 lg:grid-cols-2">
        <div>
          <SubHead k="Table 3">ADF unit root test (p-values)</SubHead>
          <div className="overflow-x-auto">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Variable</th>
                  <th className="text-right">Level</th>
                  <th className="text-right">1st difference</th>
                  <th>Result</th>
                </tr>
              </thead>
              <tbody>
                {simple.unit_roots.map((u) => (
                  <tr key={u.name}>
                    <td className="text-paper">{u.name}</td>
                    <td className="n">{u.level_p.toFixed(3)}</td>
                    <td className="n">{u.diff_p < 0.001 ? "< 0.001" : u.diff_p.toFixed(3)}</td>
                    <td className="font-mono text-[0.78rem] text-gold">{u.order}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="mt-3 text-sm text-paper-dim">
            Level p &gt; 0.05 → not stationary. After taking the monthly change, p &lt; 0.05 → stationary. So every variable is I(1), which is exactly what the
            ARDL method allows.
          </p>
        </div>
        <div>
          <SubHead k="Graph 5">Bounds test: is there a long-run relationship?</SubHead>
          <Panel>
            <BoundsLine b={ardl.bounds_test} kind="F" />
          </Panel>
        </div>
      </div>

      <div className="mt-16">
        <SubHead k="Graph 6">Stability test (CUSUM)</SubHead>
        <Panel>
          <StabilityChart st={ardl.stability} label="ARDL model" />
          <p className="mt-3 text-sm text-paper-dim">The line stays between the red bands → the relationship did not break down between 2015 and 2025.</p>
        </Panel>
      </div>
    </Chapter>
  );
}
