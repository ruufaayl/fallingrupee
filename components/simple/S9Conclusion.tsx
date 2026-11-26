import { Reveal } from "@/components/animations/Reveal";
import { Chapter, SubHead } from "@/components/ui/Chapter";
import { Disclosure } from "@/components/ui/Disclosure";
import { REFERENCES } from "@/lib/references";
import { simple } from "@/lib/simple";

export function S9Conclusion() {
  const refs = REFERENCES.filter((r) => ["PSS2001", "SYG2014", "DF1979", "Breusch1978", "BP1979", "JB1980", "Ramsey1969", "BDE1975", "CK2002", "Peltzman2000", "PBS", "IMFCPI", "WBGEM", "FAO"].includes(r.key));
  return (
    <Chapter id="conclusion" n={9} tone="graphite" kicker="Conclusion" title={<>What we found.</>}>
      <ol className="space-y-6">
        {simple.answer.map((a, i) => (
          <Reveal key={a} delay={i * 0.05}>
            <li className="flex gap-6 border-t border-line pt-5">
              <span className="num text-2xl text-gold">{i + 1}</span>
              <p className="font-serif text-xl leading-snug text-paper sm:text-2xl">{a}</p>
            </li>
          </Reveal>
        ))}
      </ol>

      <div className="mt-16 grid gap-10 md:grid-cols-2">
        <div>
          <SubHead k="So what?">What it means for Pakistan</SubHead>
          <ul className="space-y-3 text-paper-dim">
            <li className="border-l-2 border-gold pl-4">A stable rupee protects family food budgets.</li>
            <li className="border-l-2 border-gold pl-4">Don’t wait for the rupee to recover to bring food prices down — help poor families directly.</li>
            <li className="border-l-2 border-gold pl-4">Import food and inputs from more sources to be less exposed to world price jumps.</li>
          </ul>
        </div>
        <div>
          <SubHead k="Limits">What we cannot claim</SubHead>
          <ul className="space-y-3 text-paper-dim">
            <li className="border-l-2 border-line-strong pl-4">The model shows strong links, not proof of cause and effect.</li>
            <li className="border-l-2 border-line-strong pl-4">Pakistan changed its price-index base year in 2019.</li>
            <li className="border-l-2 border-line-strong pl-4">There were few months of a strong rupee, so the “recovery” effect is uncertain.</li>
          </ul>
        </div>
      </div>

      <Reveal>
        <blockquote className="mx-auto my-24 max-w-4xl text-center">
          <p className="font-display text-4xl leading-tight text-paper sm:text-6xl">
            A currency can recover in a season. <span className="italic text-gold">The price of bread remembers.</span>
          </p>
        </blockquote>
      </Reveal>

      <Disclosure title="References">
        <ul className="space-y-2 text-sm leading-relaxed text-paper-dim">
          {refs.map((r) => (
            <li key={r.key} className="pl-6 -indent-6">
              {r.text}
            </li>
          ))}
        </ul>
      </Disclosure>
    </Chapter>
  );
}
