import katex from "katex";

/** Server-rendered KaTeX: no client JS, crisp at any zoom. */
export function Equation({ tex, display = true, label }: { tex: string; display?: boolean; label?: string }) {
  const html = katex.renderToString(tex, { displayMode: display, throwOnError: false, strict: "ignore" });
  return display ? (
    <figure className="my-2" aria-label={label}>
      <div className="overflow-x-auto" dangerouslySetInnerHTML={{ __html: html }} />
      {label ? <figcaption className="mt-2 font-mono text-[0.68rem] text-faint">{label}</figcaption> : null}
    </figure>
  ) : (
    <span dangerouslySetInnerHTML={{ __html: html }} />
  );
}
