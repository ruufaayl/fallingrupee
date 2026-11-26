import { Reveal } from "@/components/animations/Reveal";
import { Chapter } from "@/components/ui/Chapter";
import { simple } from "@/lib/simple";

const COLOR = ["border-s-food", "border-s-exr", "border-s-world", "border-s-energy", "border-gold"];
const TEXT = ["text-s-food", "text-s-exr", "text-s-world", "text-s-energy", "text-gold"];

export function S3Variables() {
  return (
    <Chapter
      id="variables"
      n={3}
      tone="graphite"
      kicker="Dependent & Independent Variables"
      title={<>One thing we explain. Four things that might explain it.</>}
      intro={<p>The dependent variable is what we want to explain. The independent variables are the possible causes. All are monthly % changes; the causes are taken from the previous month because prices need time to react.</p>}
    >
      <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5">
        {simple.variables.map((v, i) => (
          <Reveal key={v.name} delay={i * 0.06}>
            <article className={`h-full border-t-4 ${COLOR[i]} bg-ink p-6`}>
              <div className="font-mono text-[0.66rem] uppercase tracking-[0.14em] text-muted">{v.role}</div>
              <div className={`num mt-3 text-4xl ${TEXT[i]}`}>{v.symbol}</div>
              <h3 className="mt-2 font-serif text-2xl text-paper">{v.name}</h3>
              <p className="mt-3 text-sm leading-relaxed text-paper-dim">{v.why}</p>
              <dl className="mt-5 space-y-2 border-t border-line pt-4 text-[0.8rem]">
                <div>
                  <dt className="font-mono text-[0.62rem] uppercase tracking-[0.12em] text-faint">Measured as</dt>
                  <dd className="text-paper-dim">{v.measure}</dd>
                </div>
                <div>
                  <dt className="font-mono text-[0.62rem] uppercase tracking-[0.12em] text-faint">Source</dt>
                  <dd className="text-paper-dim">{v.source}</dd>
                </div>
              </dl>
            </article>
          </Reveal>
        ))}
      </div>
    </Chapter>
  );
}
