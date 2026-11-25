import type { ReactNode } from "react";

import { Reveal } from "@/components/animations/Reveal";

export function MethodStep({
  n,
  title,
  what,
  why,
  nullH,
  read,
  children,
  aside,
}: {
  n: string;
  title: string;
  what: ReactNode;
  why: ReactNode;
  nullH?: ReactNode;
  read: ReactNode;
  children: ReactNode;
  aside?: ReactNode;
}) {
  return (
    <article className="border-t border-line py-14 first:border-t-0 first:pt-0">
      <Reveal>
        <div className="flex flex-wrap items-baseline justify-between gap-3">
          <div className="flex items-baseline gap-4">
            <span className="num text-gold">{n}</span>
            <h3 className="font-serif text-3xl text-paper sm:text-4xl">{title}</h3>
          </div>
          {aside}
        </div>
        <dl className="mt-8 grid gap-6 md:grid-cols-2 xl:grid-cols-4">
          {[
            { k: "What it does", v: what },
            { k: "Why we use it", v: why },
            { k: "Null hypothesis", v: nullH ?? <span className="text-faint">Not a hypothesis test.</span> },
            { k: "How to read it", v: read },
          ].map((x) => (
            <div key={x.k} className="border-l border-gold-soft/60 pl-4">
              <dt className="font-mono text-[0.64rem] uppercase tracking-[0.16em] text-gold">{x.k}</dt>
              <dd className="mt-2 text-[0.92rem] leading-relaxed text-paper-dim">{x.v}</dd>
            </div>
          ))}
        </dl>
      </Reveal>
      <div className="mt-10">{children}</div>
    </article>
  );
}

export function Result({ children }: { children: ReactNode }) {
  return (
    <div className="mt-6 border-l-2 border-gold bg-gold/5 px-5 py-4">
      <div className="font-mono text-[0.64rem] uppercase tracking-[0.16em] text-gold">Our result</div>
      <div className="mt-2 leading-relaxed text-paper">{children}</div>
    </div>
  );
}
