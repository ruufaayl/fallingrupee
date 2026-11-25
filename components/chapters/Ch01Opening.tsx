"use client";

import { gsap } from "gsap";
import { ArrowDown } from "lucide-react";
import Image from "next/image";
import { useEffect, useMemo, useRef } from "react";

import { fmt } from "@/lib/format";

interface Props {
  exr: number[];
  food: number[];
  world: number[];
  headline: { food: number; exr: number; world: number; peak: number; peakDate: string };
  photo?: { src: string; alt: string; credit: string } | null;
}

function pathFrom(values: number[], w: number, h: number, min: number, max: number) {
  return values
    .map((v, i) => {
      const x = (i / (values.length - 1)) * w;
      const y = h - ((v - min) / (max - min)) * h;
      return `${i ? "L" : "M"}${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");
}

export function Ch01Opening({ exr, food, world, headline, photo }: Props) {
  const root = useRef<HTMLElement>(null);
  const W = 1600;
  const H = 700;
  const all = [...exr, ...food, ...world];
  const [mn, mx] = [Math.min(...all) * 0.9, Math.max(...all) * 1.04];
  const paths = useMemo(
    () => ({ exr: pathFrom(exr, W, H, mn, mx), food: pathFrom(food, W, H, mn, mx), world: pathFrom(world, W, H, mn, mx) }),
    [exr, food, world, mn, mx],
  );

  useEffect(() => {
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const ctx = gsap.context(() => {
      if (reduce) {
        gsap.set("[data-o]", { opacity: 1, y: 0 });
        return;
      }
      const lines = gsap.utils.toArray<SVGPathElement>("[data-line]");
      lines.forEach((l) => {
        const len = l.getTotalLength();
        gsap.set(l, { strokeDasharray: len, strokeDashoffset: len });
      });
      const tl = gsap.timeline({ defaults: { ease: "power3.out" } });
      if (root.current?.querySelector("[data-o='photo']")) tl.to("[data-o='photo']", { opacity: 1, duration: 2.4 }, 0);
      tl.to("[data-o='kicker']", { opacity: 1, y: 0, duration: 0.9 }, 0.2)
        .to("[data-o='word']", { opacity: 1, y: 0, duration: 1.1, stagger: 0.09 }, 0.45)
        .to(lines, { strokeDashoffset: 0, duration: 3.2, ease: "power2.inOut", stagger: 0.25 }, 0.6)
        .to("[data-o='sub']", { opacity: 1, y: 0, duration: 1 }, 1.4)
        .to("[data-o='stat']", { opacity: 1, y: 0, duration: 0.9, stagger: 0.18 }, 2.0)
        .to("[data-o='cta']", { opacity: 1, y: 0, duration: 0.8 }, 2.8);
    }, root);
    return () => ctx.revert();
  }, []);

  const words1 = ["The", "Price", "of", "a"];
  const words2 = ["Falling", "Rupee"];

  return (
    <section
      ref={root}
      id="opening"
      data-chapter={1}
      aria-label="Opening"
      className="grain relative flex min-h-[100svh] flex-col justify-end overflow-hidden bg-ink px-4 pb-14 pt-28 sm:px-8 md:pb-20"
    >
      {photo ? (
        <div data-o="photo" className="absolute inset-0 opacity-0">
          <Image src={photo.src} alt={photo.alt} fill priority sizes="100vw" className="object-cover opacity-40 grayscale-[35%]" />
          <div className="absolute inset-0 bg-gradient-to-t from-ink via-ink/75 to-ink/40" />
        </div>
      ) : null}

      <svg
        viewBox={`0 0 ${W} ${H}`}
        preserveAspectRatio="none"
        className="hero-lines pointer-events-none absolute inset-x-0 top-[14%] h-[52%] w-full"
        aria-hidden
      >
        <path data-line d={paths.world} fill="none" stroke="#00a888" strokeOpacity={0.45} strokeWidth={2} vectorEffect="non-scaling-stroke" />
        <path data-line d={paths.exr} fill="none" stroke="#d28e05" strokeOpacity={0.6} strokeWidth={2} vectorEffect="non-scaling-stroke" />
        <path data-line d={paths.food} fill="none" stroke="#e5484d" strokeOpacity={0.85} strokeWidth={2.5} vectorEffect="non-scaling-stroke" />
      </svg>

      <div className="relative mx-auto w-full max-w-7xl">
        <p data-o="kicker" className="kicker translate-y-3 opacity-0">
          An econometric investigation · Pakistan · January 2015 – December 2025
        </p>

        <h1 className="mt-6 font-display uppercase leading-[0.86] tracking-[-0.02em] text-paper">
          <span className="block text-[13vw] sm:text-[10vw] lg:text-[8.6rem]">
            {words1.map((w) => (
              <span key={w} data-o="word" className="mr-[0.22em] inline-block translate-y-8 opacity-0">
                {w}
              </span>
            ))}
          </span>
          <span className="block text-[15vw] italic text-paper sm:text-[12vw] lg:text-[10.5rem]">
            {words2.map((w) => (
              <span key={w} data-o="word" className="mr-[0.2em] inline-block translate-y-8 opacity-0">
                {w}
              </span>
            ))}
          </span>
        </h1>

        <p data-o="sub" className="mt-8 max-w-2xl translate-y-4 font-serif text-xl leading-snug text-paper-dim opacity-0 sm:text-2xl">
          Why do food prices rise when the rupee falls — and why don&rsquo;t they fall when it recovers?
        </p>

        <dl className="mt-12 grid max-w-4xl grid-cols-1 gap-6 border-t border-line pt-6 sm:grid-cols-3">
          {[
            { k: "Food prices in Pakistan", v: headline.food, c: "text-s-food" },
            { k: "Rupees per US dollar", v: headline.exr, c: "text-s-exr" },
            { k: "World food prices (FAO)", v: headline.world, c: "text-s-world" },
          ].map((s) => (
            <div key={s.k} data-o="stat" className="translate-y-4 opacity-0">
              <dt className="font-mono text-[0.68rem] uppercase tracking-[0.14em] text-muted">{s.k}</dt>
              <dd className={`num mt-1 text-4xl sm:text-5xl ${s.c}`}>+{fmt(s.v, 0)}%</dd>
            </div>
          ))}
        </dl>
        <p data-o="stat" className="mt-3 translate-y-4 font-mono text-[0.66rem] text-faint opacity-0">
          Change from January 2015 to December 2025. Food CPI: PBS national CPI (via IMF CPI dataset and PBS monthly reviews);
          PKR/USD: World Bank GEM; FAO Food Price Index. Food inflation peaked at {fmt(headline.peak, 1)}% year on year in{" "}
          {headline.peakDate}.
          {photo ? ` Photograph: ${photo.credit}.` : ""}
        </p>

        <a
          href="#problem"
          data-o="cta"
          className="group mt-10 inline-flex translate-y-3 items-center gap-4 border border-gold/60 px-6 py-4 font-mono text-[0.72rem] uppercase tracking-[0.2em] text-paper opacity-0 transition-colors hover:bg-gold hover:text-ink"
        >
          Enter the investigation
          <ArrowDown className="h-4 w-4 transition-transform group-hover:translate-y-1" aria-hidden />
        </a>
      </div>
    </section>
  );
}
