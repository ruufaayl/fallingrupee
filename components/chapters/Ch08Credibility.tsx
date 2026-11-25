import { Chapter, Panel, SourceNote, SubHead } from "@/components/ui/Chapter";
import { Disclosure } from "@/components/ui/Disclosure";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { ardl, correlations, nardl, ols, robustness } from "@/lib/registry";
import { fmt, fmtP } from "@/lib/format";
import type { RobustRow } from "@/lib/types";

import { DiagnosticLab } from "./DiagnosticLab";

function RobTable({ rows, nardlCols }: { rows: RobustRow[]; nardlCols: boolean }) {
  return (
    <div className="overflow-x-auto">
      <table className="data-table">
        <thead>
          <tr>
            <th>Specification</th>
            <th>Order</th>
            <th className="text-right">N</th>
            <th className="text-right">Bounds F</th>
            <th className="text-right">t</th>
            <th className="text-right">ECT</th>
            <th className="text-right">{nardlCols ? "L⁺ (p)" : "L EXR (p)"}</th>
            {nardlCols ? <th className="text-right">L⁻ (p)</th> : null}
            {nardlCols ? <th className="text-right">LR sym. p</th> : null}
            {nardlCols ? <th className="text-right">Impact sym. p</th> : null}
            <th className="text-right">BG(2) p</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => {
            const k1 = nardlCols ? "LEXR_POS" : "LEXR";
            const l1 = r.long_run?.[k1];
            const l2 = r.long_run?.LEXR_NEG;
            return (
              <tr key={r.id}>
                <td className="min-w-[16rem]">
                  <div className="text-paper">{r.label}</div>
                  <div className="font-mono text-[0.66rem] text-faint">{r.id} · {r.sample}</div>
                </td>
                <td className="num whitespace-nowrap text-[0.78rem]">({r.order?.join(",")})</td>
                <td className="n">{r.nobs}</td>
                <td className={`n ${r.F_decision_5pct === "reject" ? "text-paper" : "text-faint"}`}>{fmt(r.bounds_F, 2)}</td>
                <td className={`n ${r.t_decision_5pct === "reject" ? "text-paper" : "text-faint"}`}>{fmt(r.bounds_t, 2)}</td>
                <td className="n">{fmt(r.ect, 3)}</td>
                <td className={`n ${l1 && l1.p < 0.05 ? "text-rise" : ""}`}>{l1 ? `${fmt(l1.coef, 2)} (${fmtP(l1.p)})` : "—"}</td>
                {nardlCols ? <td className={`n ${l2 && l2.p < 0.05 ? "text-fall" : ""}`}>{l2 ? `${fmt(l2.coef, 2)} (${fmtP(l2.p)})` : "—"}</td> : null}
                {nardlCols ? <td className={`n ${r.lr_sym_p !== undefined && r.lr_sym_p < 0.05 ? "text-gold" : ""}`}>{fmtP(r.lr_sym_p)}</td> : null}
                {nardlCols ? <td className={`n ${r.impact_sym_p !== undefined && r.impact_sym_p < 0.05 ? "text-gold" : ""}`}>{fmtP(r.impact_sym_p)}</td> : null}
                <td className="n">{fmtP(r.bg2_p)}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

export function Ch08Credibility() {
  return (
    <Chapter
      id="credibility"
      n={8}
      kicker="The Model’s Credibility"
      title={<>Trying to break our own model.</>}
      intro={
        <p>
          A coefficient is only as good as the assumptions behind it. This laboratory runs the standard battery of diagnostic tests on each model,
          then re-estimates the asymmetric model under thirteen alternative specifications. Failures are shown, not hidden.
        </p>
      }
    >
      <SubHead k="Laboratory 8.1" aside={<StatusBadge status={nardl._meta.status} />}>
        Diagnostic tests
      </SubHead>
      <Panel>
        <DiagnosticLab
          diag={{ OLS_LEVELS: ols.diagnostics, ARDL_MAIN: ardl.diagnostics, NARDL_MAIN: nardl.diagnostics }}
          stability={{ ARDL_MAIN: ardl.stability, NARDL_MAIN: nardl.stability }}
          vif={{ levels: correlations.vif_levels, diffs: correlations.vif_differences, nardl: correlations.vif_nardl_levels }}
          labels={{ OLS_LEVELS: "Static OLS", ARDL_MAIN: `ARDL(${ardl.selection.chosen_order.join(",")})`, NARDL_MAIN: `NARDL(${nardl.selection.chosen_order.join(",")})` }}
        />
      </Panel>
      <p className="mt-6 max-w-3xl text-sm leading-relaxed text-paper-dim">
        <strong className="text-paper">When a test fails.</strong> Serial correlation would call for more lags or HAC errors; heteroskedasticity for
        robust errors; non-normality — present here because of a few extreme months — matters little for inference with N &gt; 100 and is cured by an
        impulse dummy for May 2024; a failed RESET would call for a different functional form; instability would call for sub-sample analysis or
        break dummies. Each remedy is applied in the robustness table below.
      </p>

      <div className="mt-20">
        <SubHead k="Table 8.2" aside={<StatusBadge status={robustness._meta.status} />}>
          Robustness: thirteen ways to re-estimate the NARDL
        </SubHead>
        <RobTable rows={robustness.nardl_specifications.filter((r) => r.long_run)} nardlCols />
        <SourceNote>{robustness.critical_values_note} Highlighted: L⁺ significant (red), L⁻ significant (green), symmetry rejected at 5% (gold). HEADLINE uses headline CPI as the dependent variable and is an extension, not a robustness check.</SourceNote>
        <Disclosure title="Linear ARDL robustness (5 specifications)">
          <RobTable rows={robustness.ardl_specifications} nardlCols={false} />
        </Disclosure>
      </div>
    </Chapter>
  );
}
