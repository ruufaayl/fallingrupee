"use client";

/** Accessible segmented control (radio group semantics). */
export function Segmented<T extends string>({
  value,
  options,
  onChange,
  label,
}: {
  value: T;
  options: { value: T; label: string }[];
  onChange: (v: T) => void;
  label: string;
}) {
  return (
    <div role="radiogroup" aria-label={label} className="inline-flex flex-wrap gap-1 rounded-sm border border-line bg-ink/60 p-1">
      {options.map((o) => {
        const active = o.value === value;
        return (
          <button
            key={o.value}
            type="button"
            role="radio"
            aria-checked={active}
            onClick={() => onChange(o.value)}
            className={`rounded-[2px] px-3 py-1.5 font-mono text-[0.68rem] uppercase tracking-[0.1em] transition-colors ${
              active ? "bg-paper text-ink" : "text-paper-dim hover:bg-graphite-2 hover:text-paper"
            }`}
          >
            {o.label}
          </button>
        );
      })}
    </div>
  );
}
