import type { Status } from "@/lib/types";

const COPY: Record<Status, { label: string; title: string; cls: string }> = {
  verified: {
    label: "Verified in EViews",
    title: "Reproduced in EViews within tolerance (research/eviews_verification.json).",
    cls: "border-verified/50 text-verified",
  },
  computed_python_pending_eviews: {
    label: "Python estimate · EViews pending",
    title:
      "Computed reproducibly in Python (statsmodels) by scripts/03_estimate.py. The EViews programs in /eviews reproduce the same specification; confirmation in EViews is outstanding.",
    cls: "border-pending/50 text-pending",
  },
  not_available: { label: "Not available", title: "Could not be computed or the data could not be obtained.", cls: "border-line text-muted" },
  not_applicable: { label: "Not applicable", title: "Does not apply to the selected specification.", cls: "border-line text-muted" },
};

export function StatusBadge({ status, className = "" }: { status: Status; className?: string }) {
  const c = COPY[status];
  return (
    <span
      title={c.title}
      className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 font-mono text-[0.65rem] uppercase tracking-[0.12em] ${c.cls} ${className}`}
    >
      <span aria-hidden className="h-1.5 w-1.5 rounded-full bg-current" />
      {c.label}
    </span>
  );
}

export function SigBadge({ p, alpha = 0.05 }: { p: number | null | undefined; alpha?: number }) {
  if (p === null || p === undefined) return null;
  const s = p < alpha;
  return (
    <span
      className={`inline-flex rounded-sm px-1.5 py-0.5 font-mono text-[0.62rem] uppercase tracking-wider ${
        s ? "bg-paper/10 text-paper" : "bg-transparent text-faint ring-1 ring-line"
      }`}
    >
      {s ? "significant" : "not significant"}
    </span>
  );
}
