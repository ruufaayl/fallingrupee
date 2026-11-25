import { Chapter, SubHead } from "@/components/ui/Chapter";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { ardl, longRun, nardl } from "@/lib/registry";

import { TransmissionDiagram } from "./TransmissionDiagram";

export function Ch03Mechanism() {
  const L = longRun(ardl, "LEXR");
  const Lp = longRun(nardl, "LEXR_POS");
  return (
    <Chapter
      id="mechanism"
      n={3}
      tone="graphite"
      kicker="The Transmission Mechanism"
      title={<>From the currency market to the kitchen table.</>}
      intro={
        <>
          <p>
            Economists call it <strong>exchange-rate pass-through</strong>: the share of a currency movement that ends up in domestic prices. It is
            rarely complete and rarely instant (Campa &amp; Goldberg, 2005; Taylor, 2000). Food prices sit at the end of a chain, and each link can
            absorb, delay or amplify the shock.
          </p>
          <p>
            Three forces enter the chain: the <strong>exchange rate</strong>, <strong>world food prices</strong> and <strong>domestic energy
            costs</strong>. These are exactly the three regressors of the models in Chapters 06–07.
          </p>
        </>
      }
    >
      <SubHead k="Interactive 3.1" aside={<StatusBadge status={ardl._meta.status} />}>
        How a weaker rupee reaches the plate
      </SubHead>
      <TransmissionDiagram elasticity={L.coef} lo={L.ci95_low} hi={L.ci95_high} depElasticity={Lp.coef} />
    </Chapter>
  );
}
