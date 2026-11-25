"use client";

import type { EChartsOption } from "echarts";
import { useReducedMotion } from "framer-motion";
import { useEffect, useRef, useState } from "react";

type EC = typeof import("echarts/core");

let echartsPromise: Promise<EC> | null = null;

/** Load only the ECharts pieces the site uses (tree-shaken), once. */
function loadECharts(): Promise<EC> {
  if (!echartsPromise) {
    echartsPromise = Promise.all([
      import("echarts/core"),
      import("echarts/charts"),
      import("echarts/components"),
      import("echarts/renderers"),
    ]).then(([core, charts, comps, renderers]) => {
      core.use([
        charts.LineChart,
        charts.BarChart,
        charts.ScatterChart,
        charts.HeatmapChart,
        charts.CustomChart,
        comps.GridComponent,
        comps.TooltipComponent,
        comps.LegendComponent,
        comps.MarkLineComponent,
        comps.MarkAreaComponent,
        comps.MarkPointComponent,
        comps.VisualMapComponent,
        comps.DataZoomComponent,
        comps.AriaComponent,
        renderers.CanvasRenderer,
      ]);
      return core;
    });
  }
  return echartsPromise;
}

/**
 * Generic ECharts host. Charts draw progressively when they first enter the viewport
 * (the "progressive chart drawing" motion), and redraw instantly on later option changes.
 */
export function EChart({
  option,
  height = 380,
  ariaLabel,
  className = "",
}: {
  option: EChartsOption;
  height?: number | string;
  ariaLabel: string;
  className?: string;
}) {
  const el = useRef<HTMLDivElement>(null);
  const chart = useRef<ReturnType<EC["init"]> | null>(null);
  const [visible, setVisible] = useState(false);
  const reduce = useReducedMotion();

  useEffect(() => {
    const node = el.current;
    if (!node) return;
    const io = new IntersectionObserver(
      (es) => {
        if (es.some((e) => e.isIntersecting)) {
          setVisible(true);
          io.disconnect();
        }
      },
      { rootMargin: "120px" },
    );
    io.observe(node);
    return () => io.disconnect();
  }, []);

  useEffect(() => {
    if (!visible || !el.current) return;
    let disposed = false;
    let ro: ResizeObserver | null = null;
    loadECharts().then((ec) => {
      if (disposed || !el.current) return;
      chart.current = ec.init(el.current, undefined, { renderer: "canvas" });
      chart.current.setOption({
        animation: !reduce,
        animationDuration: 1400,
        animationEasing: "cubicOut",
        aria: { enabled: true, label: { description: ariaLabel } },
        textStyle: { fontFamily: "Inter Variable, ui-sans-serif, system-ui, sans-serif" },
        ...option,
      });
      ro = new ResizeObserver(() => chart.current?.resize());
      ro.observe(el.current);
    });
    return () => {
      disposed = true;
      ro?.disconnect();
      chart.current?.dispose();
      chart.current = null;
    };
    // initial mount only; option updates are handled below
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [visible]);

  useEffect(() => {
    if (!chart.current) return;
    chart.current.setOption(
      { animation: !reduce, animationDurationUpdate: 500, aria: { enabled: true, label: { description: ariaLabel } }, ...option },
      { notMerge: true },
    );
  }, [option, ariaLabel, reduce]);

  return (
    <div
      ref={el}
      role="img"
      aria-label={ariaLabel}
      className={`w-full ${className}`}
      style={{ height }}
    />
  );
}
