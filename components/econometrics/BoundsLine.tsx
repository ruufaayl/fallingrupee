import { fmt } from "@/lib/format";
import type { BoundsTest } from "@/lib/types";

/** Number line showing the test statistic against the PSS I(0) and I(1) bounds (5%). */
export function BoundsLine({ b, kind }: { b: BoundsTest; kind: "F" | "t" }) {
  const cv = b.asymptotic["5%"];
  const lo = kind === "F" ? cv.F_I0 : cv.t_I0;
  const hi = kind === "F" ? cv.F_I1 : cv.t_I1;
  const stat = kind === "F" ? b.F : b.t;
  // map to 0..100; for t the scale is negative (reject when stat < I(1) bound)
  const min = kind === "F" ? 0 : Math.min(-6, stat - 0.5);
  const max = kind === "F" ? Math.max(10, stat + 1) : 0;
  const pos = (v: number) => ((v - min) / (max - min)) * 100;
  const reject = kind === "F" ? stat > hi : stat < hi;
  const inconclusive = kind === "F" ? stat > lo && stat <= hi : stat < lo && stat >= hi;
  const verdict = reject ? "Reject “no cointegration”" : inconclusive ? "Inconclusive" : "Cannot reject “no cointegration”";
  const [a, z] = kind === "F" ? [pos(lo), pos(hi)] : [pos(hi), pos(lo)];
  return (
    <figure className="w-full">
      <div className="mb-2 flex items-baseline justify-between gap-3">
        <span className="font-mono text-[0.68rem] uppercase tracking-[0.14em] text-muted">
          {kind === "F" ? "PSS F-statistic" : "PSS t-statistic"} · k = {b.k}
        </span>
        <span className={`font-mono text-[0.7rem] uppercase tracking-[0.1em] ${reject ? "text-fall" : inconclusive ? "text-pending" : "text-rise"}`}>{verdict}</span>
      </div>
      <svg viewBox="0 0 100 18" className="h-14 w-full overflow-visible" role="img" aria-label={`${kind} statistic ${fmt(stat, 2)} against 5% bounds ${fmt(lo, 2)} (I(0)) and ${fmt(hi, 2)} (I(1)). ${verdict}.`}>
        <rect x={0} y={7} width={100} height={4} fill="#24272c" />
        <rect x={a} y={7} width={z - a} height={4} fill="#d28e05" opacity={0.45} />
        <rect x={kind === "F" ? z : 0} y={7} width={kind === "F" ? 100 - z : a} height={4} fill="#00a888" opacity={0.45} />
        <line x1={pos(stat)} x2={pos(stat)} y1={2} y2={16} stroke="#f1ece2" strokeWidth={0.6} />
        <circle cx={pos(stat)} cy={9} r={1.6} fill="#f1ece2" />
      </svg>
      <div className="relative h-5 font-mono text-[0.65rem] text-faint">
        <span className={`absolute pr-1 ${kind === "F" ? "-translate-x-full" : ""}`} style={{ left: `${pos(lo)}%` }}>I(0) {fmt(lo, 2)}</span>
        <span className={`absolute pl-1 ${kind === "F" ? "" : "-translate-x-full"}`} style={{ left: `${pos(hi)}%` }}>I(1) {fmt(hi, 2)}</span>
      </div>
      <figcaption className="mt-1 text-sm text-paper-dim">
        Statistic <span className="num text-paper">{fmt(stat, 3)}</span>. The amber zone between the bounds is inconclusive; the green zone rejects
        the null of no long-run relationship at 5% (PSS 2001, case III asymptotic bounds).
      </figcaption>
    </figure>
  );
}
