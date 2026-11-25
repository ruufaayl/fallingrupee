"use client";

import { useMemo, useState } from "react";

import { Segmented } from "@/components/ui/Segmented";
import { fmt } from "@/lib/format";

type Channel = "exr" | "world" | "energy";
interface Node { id: string; x: number; y: number; w: number; label: string[]; color?: string; body: string }
interface Edge { id: string; from: string; to: string; ch: Channel[]; kind: "direct" | "indirect"; note: string }

const NODES: Node[] = [
  { id: "rupee", x: 40, y: 70, w: 200, label: ["Rupee", "depreciation"], color: "#d28e05", body: "More rupees are needed for every US dollar. Anything priced in dollars — imports, fuel, freight — becomes more expensive in rupees, even if its dollar price is unchanged." },
  { id: "world", x: 40, y: 250, w: 200, label: ["World food", "prices"], color: "#00a888", body: "The FAO index tracks dollar prices of cereals, vegetable oils, dairy, meat and sugar on world markets. A rise raises the dollar cost of what Pakistan imports and the export-parity price of what it grows." },
  { id: "energy", x: 40, y: 430, w: 200, label: ["Domestic", "energy costs"], color: "#338ced", body: "Petrol and diesel prices (captured here by the transport CPI) set the cost of tractors, tube-wells, trucks and cold storage. Pakistan imports most of its crude oil, so the exchange rate also feeds domestic fuel prices." },
  { id: "imports", x: 330, y: 120, w: 220, label: ["Imported food", "& farm inputs"], body: "Edible oil, pulses, tea, and in some years wheat and sugar, are imported directly; fertiliser components, seed and machinery parts enter as inputs. Their rupee cost moves with both the exchange rate and world prices." },
  { id: "costs", x: 330, y: 380, w: 220, label: ["Production &", "transport costs"], body: "Farm and distribution costs rise with inputs and energy. Producers and traders pass these on over weeks and months rather than instantly — one reason the models need lags." },
  { id: "wholesale", x: 620, y: 250, w: 170, label: ["Wholesale", "markets"], body: "Mandis and wholesalers reprice stocks. Expectations matter: a falling rupee can trigger precautionary hoarding and faster repricing; a recovering rupee gives less reason to cut prices quickly." },
  { id: "retail", x: 830, y: 250, w: 150, label: ["Consumer", "food prices"], color: "#e5484d", body: "What households pay — the food group of the national CPI, the dependent variable of this study." },
];

const EDGES: Edge[] = [
  { id: "e1", from: "rupee", to: "imports", ch: ["exr"], kind: "direct", note: "Direct: the rupee price of dollar-priced imports rises one-for-one at the border." },
  { id: "e2", from: "world", to: "imports", ch: ["world"], kind: "direct", note: "Direct: higher dollar prices of imported food raise their rupee cost." },
  { id: "e3", from: "imports", to: "retail", ch: ["exr", "world"], kind: "direct", note: "Direct: imported finished foods (edible oil, pulses, tea) reach shelves with little processing." },
  { id: "e4", from: "imports", to: "costs", ch: ["exr", "world"], kind: "indirect", note: "Indirect: imported inputs raise the cost of producing food domestically." },
  { id: "e5", from: "rupee", to: "energy", ch: ["exr"], kind: "indirect", note: "Indirect: imported crude oil and LNG cost more rupees, feeding domestic fuel prices." },
  { id: "e6", from: "energy", to: "costs", ch: ["energy", "exr"], kind: "indirect", note: "Indirect: diesel, electricity and freight costs enter every stage of the food chain." },
  { id: "e7", from: "costs", to: "wholesale", ch: ["exr", "world", "energy"], kind: "indirect", note: "Indirect: producers and transporters reprice to wholesalers." },
  { id: "e8", from: "imports", to: "wholesale", ch: ["exr", "world"], kind: "indirect", note: "Indirect: imported commodities are traded and repriced through wholesale markets." },
  { id: "e9", from: "wholesale", to: "retail", ch: ["exr", "world", "energy"], kind: "indirect", note: "Indirect: retailers adjust shelf prices — usually faster upward than downward (the asymmetry tested in Chapter 07)." },
];

const H = 64;
const nodeById = (id: string) => NODES.find((n) => n.id === id)!;

function edgePath(e: Edge) {
  const a = nodeById(e.from);
  const b = nodeById(e.to);
  const x1 = a.x + a.w;
  const y1 = a.y + H / 2;
  const x2 = b.x;
  const y2 = b.y + H / 2;
  if (e.from === "rupee" && e.to === "energy") {
    const x = a.x + a.w / 2;
    return `M${x},${a.y + H} C${x - 30},${a.y + 200} ${x - 30},${b.y - 140} ${x},${b.y}`;
  }
  const mx = (x1 + x2) / 2;
  return `M${x1},${y1} C${mx},${y1} ${mx},${y2} ${x2},${y2}`;
}

export function TransmissionDiagram({ elasticity, lo, hi, depElasticity }: { elasticity: number; lo: number; hi: number; depElasticity: number }) {
  const [ch, setCh] = useState<"all" | Channel>("all");
  const [kind, setKind] = useState<"all" | "direct" | "indirect">("all");
  const [sel, setSel] = useState<string>("rupee");
  const [shock, setShock] = useState(10);

  const active = (e: Edge) => (ch === "all" || e.ch.includes(ch)) && (kind === "all" || e.kind === kind);
  const selNode = NODES.find((n) => n.id === sel);
  const selEdge = EDGES.find((e) => e.id === sel);

  const sim = useMemo(() => {
    const d = Math.log(1 + shock / 100);
    const toPct = (L: number) => (Math.exp(L * d) - 1) * 100;
    return { mid: toPct(elasticity), lo: toPct(lo), hi: toPct(hi), nardl: toPct(depElasticity) };
  }, [shock, elasticity, lo, hi, depElasticity]);

  return (
    <div>
      <div className="mb-5 flex flex-wrap gap-3">
        <Segmented label="Channel" value={ch} onChange={setCh} options={[
          { value: "all", label: "All channels" },
          { value: "exr", label: "Exchange rate" },
          { value: "world", label: "World food" },
          { value: "energy", label: "Energy" },
        ]} />
        <Segmented label="Transmission type" value={kind} onChange={setKind} options={[
          { value: "all", label: "All" },
          { value: "direct", label: "Direct" },
          { value: "indirect", label: "Indirect" },
        ]} />
      </div>

      <div className="grid gap-8 lg:grid-cols-[1fr_320px]">
        <div className="overflow-x-auto rounded-sm border border-line bg-surface p-3">
          <svg viewBox="0 0 1000 520" className="min-w-[680px]" role="group" aria-label="Transmission mechanism diagram. Select a box or arrow to read its explanation.">
            <defs>
              <marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
                <path d="M0,0 L10,5 L0,10 z" fill="#c9a24a" />
              </marker>
              <marker id="arrDim" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
                <path d="M0,0 L10,5 L0,10 z" fill="#3a3f46" />
              </marker>
            </defs>
            {EDGES.map((e) => {
              const on = active(e);
              return (
                <g key={e.id}>
                  <path d={edgePath(e)} fill="none" stroke={on ? "#c9a24a" : "#2a2e34"} strokeWidth={on ? 2 : 1.2} strokeDasharray={e.kind === "indirect" ? "6 6" : undefined} markerEnd={on ? "url(#arr)" : "url(#arrDim)"} className={on ? "flow" : ""} />
                  <path
                    d={edgePath(e)}
                    fill="none"
                    stroke="transparent"
                    strokeWidth={18}
                    className="cursor-pointer"
                    tabIndex={0}
                    role="button"
                    aria-label={e.note}
                    onClick={() => setSel(e.id)}
                    onKeyDown={(ev) => (ev.key === "Enter" || ev.key === " ") && setSel(e.id)}
                  />
                </g>
              );
            })}
            {NODES.map((n) => {
              const isSel = sel === n.id;
              return (
                <g
                  key={n.id}
                  tabIndex={0}
                  role="button"
                  aria-pressed={isSel}
                  aria-label={`${n.label.join(" ")}: ${n.body}`}
                  onClick={() => setSel(n.id)}
                  onKeyDown={(ev) => (ev.key === "Enter" || ev.key === " ") && setSel(n.id)}
                  className="cursor-pointer outline-none"
                >
                  <rect x={n.x} y={n.y} width={n.w} height={H} rx={2} fill={isSel ? "#1d2024" : "#15171a"} stroke={isSel ? "#c9a24a" : n.color ?? "#3a3f46"} strokeWidth={isSel ? 2 : 1.2} />
                  {n.color ? <rect x={n.x} y={n.y} width={4} height={H} fill={n.color} /> : null}
                  {n.label.map((l, i) => (
                    <text key={l} x={n.x + 18} y={n.y + 27 + i * 20} fill="#f1ece2" fontSize={16} fontFamily="Inter Variable, sans-serif">
                      {l}
                    </text>
                  ))}
                </g>
              );
            })}
          </svg>
          <p className="px-2 pb-1 pt-2 font-mono text-[0.64rem] text-faint">Solid arrows: direct channels · dashed arrows: indirect channels · select any box or arrow.</p>
        </div>

        <aside className="rounded-sm border border-line bg-graphite p-6" aria-live="polite">
          <div className="kicker">{selNode ? "Stage" : selEdge?.kind === "direct" ? "Direct channel" : "Indirect channel"}</div>
          <h4 className="mt-2 font-serif text-2xl text-paper">
            {selNode ? selNode.label.join(" ") : `${nodeById(selEdge!.from).label.join(" ")} → ${nodeById(selEdge!.to).label.join(" ")}`}
          </h4>
          <p className="mt-3 leading-relaxed text-paper-dim">{selNode ? selNode.body : selEdge!.note}</p>
        </aside>
      </div>

      <style>{`
        .flow { animation: flow 1.6s linear infinite; }
        @keyframes flow { to { stroke-dashoffset: -24; } }
        path.flow:not([stroke-dasharray]) { stroke-dasharray: 10 4; }
      `}</style>

      <div className="mt-12 grid gap-8 rounded-sm border border-line bg-graphite p-6 sm:p-8 lg:grid-cols-[1fr_1.2fr]">
        <div>
          <div className="kicker">Try it · model-implied, not a forecast</div>
          <h4 className="mt-2 font-serif text-2xl text-paper">If the rupee depreciates by…</h4>
          <input type="range" min={1} max={50} value={shock} onChange={(e) => setShock(Number(e.target.value))} className="mt-6 w-full accent-[#c9a24a]" aria-label="Size of a permanent depreciation, percent" />
          <div className="num mt-2 text-5xl text-s-exr">{shock}%</div>
          <p className="mt-3 text-sm text-paper-dim">a permanent rise of {shock}% in rupees per US dollar, all else equal.</p>
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="border-l-2 border-s-food pl-4">
            <div className="font-mono text-[0.66rem] uppercase tracking-[0.12em] text-muted">Long-run food CPI · linear ARDL</div>
            <div className="num mt-1 text-4xl text-paper">+{fmt(sim.mid, 1)}%</div>
            <div className="num mt-1 text-xs text-faint">95% CI {fmt(sim.lo, 1)}% to {fmt(sim.hi, 1)}%</div>
          </div>
          <div className="border-l-2 border-s-exr pl-4">
            <div className="font-mono text-[0.66rem] uppercase tracking-[0.12em] text-muted">Long-run food CPI · NARDL, depreciation</div>
            <div className="num mt-1 text-4xl text-paper">+{fmt(sim.nardl, 1)}%</div>
            <div className="num mt-1 text-xs text-faint">elasticity {fmt(depElasticity, 3)}</div>
          </div>
          <p className="text-sm leading-relaxed text-paper-dim sm:col-span-2">
            Computed as (1 + shock)<sup>L</sup> − 1 with the estimated long-run elasticity L (ARDL: {fmt(elasticity, 3)}). The full effect builds up
            over months; Chapter 07 shows how fast. These are associations conditional on the model, not causal forecasts.
          </p>
        </div>
      </div>
    </div>
  );
}
