import { CheckCircle2, ExternalLink } from "lucide-react";

import { SeriesExplorer } from "@/components/charts/TimeCharts";
import { Chapter, Panel, SourceNote, SubHead } from "@/components/ui/Chapter";
import { Disclosure } from "@/components/ui/Disclosure";
import validation from "@/data/metadata/validation_report.json";
import { manifest, sources, timeseries, variables } from "@/lib/registry";

export function Ch04Data() {
  const core = variables.variables.filter((v) => ["FOODCPI", "EXR", "GFOOD", "TRANSCPI", "LEXR_POS", "LEXR_NEG"].includes(v.code));
  const robust = variables.variables.filter((v) => !core.includes(v));
  const facts = [
    { k: "Sample", v: `${manifest.estimation_sample.start} – ${manifest.estimation_sample.end}` },
    { k: "Frequency", v: "Monthly" },
    { k: "Observations", v: String(manifest.estimation_sample.nobs) },
    { k: "Missing values", v: "0" },
    { k: "Validation checks", v: `${validation.checks.filter((c) => c.passed).length} / ${validation.checks.length} passed` },
  ];
  return (
    <Chapter
      id="data"
      n={4}
      kicker="The Data Room"
      title={<>Every number has an address.</>}
      intro={
        <>
          <p>
            All series come from official statistical agencies. Raw files are stored untouched with their download time and SHA-256 fingerprint;
            a single script rebuilds the dataset and refuses to run if any cross-source check fails.
          </p>
          <p>
            <strong>One comparability issue matters.</strong> PBS switched to a new national CPI (base 2015-16) in July 2019. From 2019M07 our food
            index is that official series; earlier months are the IMF’s back-linked version of the previous CPI. We do not splice anything
            ourselves, and we test whether the switch matters (2019M07 dummy; post-2019 sub-sample).
          </p>
        </>
      }
    >
      <dl className="grid grid-cols-2 gap-px overflow-hidden rounded-sm border border-line bg-line md:grid-cols-5">
        {facts.map((f) => (
          <div key={f.k} className="bg-graphite p-5">
            <dt className="font-mono text-[0.64rem] uppercase tracking-[0.14em] text-muted">{f.k}</dt>
            <dd className="num mt-2 text-lg text-paper">{f.v}</dd>
          </div>
        ))}
      </dl>

      <div className="mt-16">
        <SubHead k="Table 4.1">Variables in the models</SubHead>
        <div className="overflow-x-auto">
          <table className="data-table">
            <thead>
              <tr>
                <th>Variable</th>
                <th>Role</th>
                <th>Definition</th>
                <th>Unit</th>
                <th>Source · series</th>
                <th>Transformation</th>
              </tr>
            </thead>
            <tbody>
              {core.map((v) => (
                <tr key={v.code}>
                  <td>
                    <div className="text-paper">{v.name}</div>
                    <div className="font-mono text-[0.7rem] text-gold">{v.log_code}</div>
                  </td>
                  <td className="text-paper-dim">{v.role}</td>
                  <td className="min-w-[16rem] text-paper-dim">{v.definition}</td>
                  <td className="whitespace-nowrap text-paper-dim">{v.unit}</td>
                  <td className="min-w-[12rem] font-mono text-[0.72rem] text-paper-dim">{v.series_id}</td>
                  <td className="min-w-[10rem] text-paper-dim">{v.transform}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="mt-6">
          <Disclosure title={`Robustness and context variables (${robust.length})`}>
            <ul className="grid gap-3 md:grid-cols-2">
              {robust.map((v) => (
                <li key={v.code} className="border-l border-line pl-4 text-sm text-paper-dim">
                  <span className="text-paper">{v.name}</span> <span className="font-mono text-[0.7rem] text-gold">{v.log_code}</span> — {v.definition}{" "}
                  ({v.unit}). <span className="font-mono text-[0.7rem] text-faint">{v.series_id}</span>
                </li>
              ))}
            </ul>
          </Disclosure>
          <Disclosure title="Considered but excluded — and why">
            <ul className="space-y-3">
              {variables.considered_but_excluded.map((c) => (
                <li key={c.variable} className="text-sm text-paper-dim">
                  <span className="text-paper">{c.variable}</span> · <span className="font-mono text-[0.7rem] uppercase text-gold">{c.decision}</span> — {c.reason}
                </li>
              ))}
            </ul>
          </Disclosure>
          <Disclosure title="Base-year and comparability notes">
            <ul className="space-y-3">
              {variables.variables.filter((v) => v.rebasing && v.rebasing !== "—" && v.rebasing !== "None" && !v.rebasing.startsWith("As ")).map((v) => (
                <li key={v.code} className="text-sm leading-relaxed text-paper-dim">
                  <span className="text-paper">{v.name}:</span> {v.rebasing}
                </li>
              ))}
            </ul>
          </Disclosure>
        </div>
      </div>

      <div className="mt-16">
        <SubHead k="Interactive 4.2">Time-series explorer</SubHead>
        <Panel>
          <SeriesExplorer dates={timeseries.dates} s={timeseries.series} rebased={timeseries.rebased_2015m01} />
          <SourceNote>Sources: PBS; IMF CPI (via DBnomics); World Bank GEM and Pink Sheet; FAO. Monthly, January 2015 – December 2025.</SourceNote>
        </Panel>
      </div>

      <div className="mt-16 grid gap-10 lg:grid-cols-2">
        <div>
          <SubHead k="Register 4.3">Data sources</SubHead>
          <ul className="space-y-5">
            {sources.map((s) => (
              <li key={s.id} className="border-t border-line pt-4">
                <a href={s.url} target="_blank" rel="noreferrer" className="group inline-flex items-start gap-2 text-paper hover:text-gold">
                  <span>{s.institution}</span>
                  <ExternalLink className="mt-1 h-3.5 w-3.5 shrink-0 opacity-60 group-hover:opacity-100" aria-hidden />
                </a>
                <p className="mt-1 text-sm text-paper-dim">{s.title}</p>
                <p className="mt-1 font-mono text-[0.66rem] text-faint">
                  Used for: {s.used_for} · {s.downloads.length} file{s.downloads.length === 1 ? "" : "s"}, downloaded{" "}
                  {s.downloads[0]?.downloaded_utc.slice(0, 10)}
                </p>
              </li>
            ))}
          </ul>
        </div>
        <div>
          <SubHead k="Audit 4.4">Automated validation</SubHead>
          <ul className="space-y-3">
            {validation.checks.map((c) => (
              <li key={c.check} className="flex gap-3 text-sm">
                <CheckCircle2 className={`mt-0.5 h-4 w-4 shrink-0 ${c.passed ? "text-fall" : "text-rise"}`} aria-label={c.passed ? "passed" : "failed"} />
                <div>
                  <div className="text-paper">{c.check}</div>
                  <div className="font-mono text-[0.68rem] text-faint">{c.detail}</div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </Chapter>
  );
}
