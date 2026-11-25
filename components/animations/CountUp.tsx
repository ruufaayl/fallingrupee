"use client";

import { animate, useInView, useReducedMotion } from "framer-motion";
import { useEffect, useRef, useState } from "react";

/** Animated number that counts up when scrolled into view. The final value is the registry value. */
export function CountUp({
  value,
  decimals = 0,
  prefix = "",
  suffix = "",
  duration = 1.6,
  className = "",
}: {
  value: number;
  decimals?: number;
  prefix?: string;
  suffix?: string;
  duration?: number;
  className?: string;
}) {
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true, margin: "-10% 0px" });
  const reduce = useReducedMotion();
  const [v, setV] = useState(reduce ? value : 0);

  useEffect(() => {
    if (!inView) return;
    if (reduce) {
      setV(value);
      return;
    }
    const c = animate(0, value, { duration, ease: [0.16, 1, 0.3, 1], onUpdate: setV });
    return () => c.stop();
  }, [inView, value, duration, reduce]);

  const txt = v.toLocaleString("en-GB", { minimumFractionDigits: decimals, maximumFractionDigits: decimals }).replace("-", "−");
  return (
    <span ref={ref} className={`num ${className}`} aria-label={`${prefix}${value.toFixed(decimals)}${suffix}`}>
      {prefix}
      {txt}
      {suffix}
    </span>
  );
}
