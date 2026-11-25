import type { ReactNode } from "react";

import { Reveal } from "@/components/animations/Reveal";

export function Chapter({
  id,
  n,
  kicker,
  title,
  intro,
  children,
  tone = "ink",
}: {
  id: string;
  n: number;
  kicker: string;
  title: ReactNode;
  intro?: ReactNode;
  children: ReactNode;
  tone?: "ink" | "graphite";
}) {
  return (
    <section
      id={id}
      data-chapter={n}
      aria-labelledby={`${id}-title`}
      className={`relative scroll-mt-14 border-t border-line px-4 py-24 sm:px-8 md:py-32 ${
        tone === "graphite" ? "bg-graphite" : "bg-ink"
      }`}
    >
      <div className="mx-auto max-w-6xl">
        <Reveal>
          <div className="flex items-baseline gap-4">
            <span className="num text-sm text-gold">{String(n).padStart(2, "0")}</span>
            <span className="h-px w-10 bg-gold-soft" aria-hidden />
            <span className="kicker">{kicker}</span>
          </div>
          <h2
            id={`${id}-title`}
            className="mt-6 max-w-4xl font-display text-[2.6rem] leading-[1.02] tracking-[-0.01em] text-paper sm:text-6xl md:text-7xl"
          >
            {title}
          </h2>
          {intro ? <div className="prose-doc mt-8 max-w-2xl">{intro}</div> : null}
        </Reveal>
        <div className="mt-14 md:mt-20">{children}</div>
      </div>
    </section>
  );
}

export function SubHead({ k, children, aside }: { k?: string; children: ReactNode; aside?: ReactNode }) {
  return (
    <div className="mb-6 flex flex-wrap items-end justify-between gap-4">
      <div>
        {k ? <div className="kicker mb-2">{k}</div> : null}
        <h3 className="font-serif text-2xl leading-tight text-paper sm:text-3xl">{children}</h3>
      </div>
      {aside}
    </div>
  );
}

export function Panel({ children, className = "" }: { children: ReactNode; className?: string }) {
  return <div className={`rounded-sm border border-line bg-graphite/60 p-5 sm:p-7 ${className}`}>{children}</div>;
}

export function SourceNote({ children }: { children: ReactNode }) {
  return <p className="mt-3 font-mono text-[0.68rem] leading-relaxed text-faint">{children}</p>;
}
