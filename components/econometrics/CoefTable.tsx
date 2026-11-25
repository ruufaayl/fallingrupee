import { fmt, fmtP, stars, termLabel } from "@/lib/format";
import type { Coef } from "@/lib/types";

export function CoefTable({ rows, caption, highlight = [] }: { rows: Coef[]; caption?: string; highlight?: string[] }) {
  return (
    <div className="overflow-x-auto">
      <table className="data-table">
        {caption ? <caption className="mb-3 text-left font-mono text-[0.68rem] text-faint">{caption}</caption> : null}
        <thead>
          <tr>
            <th>Term</th>
            <th className="text-right">Coef.</th>
            <th className="text-right">Std. err.</th>
            <th className="text-right">t</th>
            <th className="text-right">p</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.term} className={highlight.includes(r.term) ? "text-paper" : "text-paper-dim"}>
              <td>
                <span className="font-mono text-[0.7rem] text-faint">{r.term}</span>
                <div className={highlight.includes(r.term) ? "font-medium" : ""}>{termLabel(r.term)}</div>
              </td>
              <td className="n">
                {fmt(r.coef, 4)}
                <span className="text-gold">{stars(r.p)}</span>
              </td>
              <td className="n">{fmt(r.se, 4)}</td>
              <td className="n">{fmt(r.t, 2)}</td>
              <td className="n">{fmtP(r.p)}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <p className="mt-2 font-mono text-[0.65rem] text-faint">*** p &lt; 0.01 · ** p &lt; 0.05 · * p &lt; 0.10</p>
    </div>
  );
}
