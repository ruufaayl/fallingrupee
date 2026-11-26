"use client";

import { AnimatePresence, motion } from "framer-motion";
import { Keyboard, Menu, MonitorPlay, X } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

import { CHAPTERS } from "@/lib/chapters";

/**
 * Fixed top bar: scroll progress, current chapter, chapter menu and presentation mode.
 * Keyboard: → / PageDown / j = next chapter, ← / PageUp / k = previous, p = presentation mode,
 * 1–9 jump to sections 1–9, Esc closes the menu or leaves presentation mode.
 */
export function ChapterNav() {
  const [progress, setProgress] = useState(0);
  const [current, setCurrent] = useState(0);
  const [open, setOpen] = useState(false);
  const [present, setPresent] = useState(false);
  const [help, setHelp] = useState(false);

  useEffect(() => {
    let raf = 0;
    const onScroll = () => {
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(() => {
        const h = document.documentElement;
        setProgress(h.scrollTop / Math.max(1, h.scrollHeight - h.clientHeight));
        const mid = window.innerHeight * 0.35;
        let idx = 0;
        CHAPTERS.forEach((c, i) => {
          const el = document.getElementById(c.id);
          if (el && el.getBoundingClientRect().top <= mid) idx = i;
        });
        setCurrent(idx);
      });
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const go = useCallback((i: number) => {
    const c = CHAPTERS[Math.max(0, Math.min(CHAPTERS.length - 1, i))];
    document.getElementById(c.id)?.scrollIntoView({ behavior: "smooth", block: "start" });
    setOpen(false);
  }, []);

  const togglePresent = useCallback(() => {
    setPresent((p) => {
      const next = !p;
      document.documentElement.dataset.present = String(next);
      if (next && document.fullscreenEnabled && !document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(() => undefined);
      } else if (!next && document.fullscreenElement) {
        document.exitFullscreen().catch(() => undefined);
      }
      return next;
    });
  }, []);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const t = e.target as HTMLElement;
      if (t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.tagName === "SELECT" || t.isContentEditable)) return;
      if (e.metaKey || e.ctrlKey || e.altKey) return;
      const k = e.key;
      if (k === "ArrowRight" || k === "PageDown" || k === "j") {
        e.preventDefault();
        go(current + 1);
      } else if (k === "ArrowLeft" || k === "PageUp" || k === "k") {
        e.preventDefault();
        go(current - 1);
      } else if (k === "p" || k === "P") {
        togglePresent();
      } else if (k === "?") {
        setHelp((h) => !h);
      } else if (k === "Escape") {
        setOpen(false);
        setHelp(false);
        if (present) togglePresent();
      } else if (/^[0-9]$/.test(k)) {
        go(k === "0" ? 9 : Number(k) - 1);
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [current, go, present, togglePresent]);

  useEffect(() => {
    const onFs = () => {
      if (!document.fullscreenElement && present) {
        setPresent(false);
        document.documentElement.dataset.present = "false";
      }
    };
    document.addEventListener("fullscreenchange", onFs);
    return () => document.removeEventListener("fullscreenchange", onFs);
  }, [present]);

  const c = CHAPTERS[current];
  return (
    <>
      <header className="site-chrome fixed inset-x-0 top-0 z-50 border-b border-line/70 bg-ink/80 backdrop-blur-md transition-opacity duration-300">
        <div className="mx-auto flex h-14 max-w-7xl items-center justify-between gap-3 px-4 sm:px-8">
          <a href="#opening" className="min-w-0 truncate font-display text-lg leading-none text-paper">
            The Price of a Falling Rupee
          </a>
          <div className="hidden items-center gap-3 font-mono text-[0.68rem] uppercase tracking-[0.14em] text-muted md:flex">
            <span className="text-gold">{String(c.n).padStart(2, "0")}</span>
            <span>{c.short}</span>
          </div>
          <nav className="flex items-center gap-1" aria-label="Site">
            <button
              type="button"
              onClick={() => setHelp((h) => !h)}
              className="hidden rounded-sm p-2 text-muted hover:bg-graphite-2 hover:text-paper sm:inline-flex"
              aria-label="Keyboard shortcuts"
            >
              <Keyboard className="h-4 w-4" />
            </button>
            <button
              type="button"
              onClick={togglePresent}
              className="inline-flex items-center gap-2 rounded-sm px-2.5 py-2 font-mono text-[0.68rem] uppercase tracking-[0.12em] text-muted hover:bg-graphite-2 hover:text-paper"
              aria-pressed={present}
            >
              <MonitorPlay className="h-4 w-4" />
              <span className="hidden sm:inline">Present</span>
            </button>
            <button
              type="button"
              onClick={() => setOpen((o) => !o)}
              className="inline-flex items-center gap-2 rounded-sm px-2.5 py-2 font-mono text-[0.68rem] uppercase tracking-[0.12em] text-paper hover:bg-graphite-2"
              aria-expanded={open}
              aria-controls="chapter-menu"
            >
              {open ? <X className="h-4 w-4" /> : <Menu className="h-4 w-4" />}
              <span className="hidden sm:inline">Chapters</span>
            </button>
          </nav>
        </div>
        <div className="h-px w-full bg-line">
          <div className="h-px origin-left bg-gold" style={{ transform: `scaleX(${progress})` }} />
        </div>
      </header>

      <AnimatePresence>
        {open ? (
          <motion.div
            id="chapter-menu"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="fixed inset-0 z-40 overflow-y-auto bg-ink/95 px-4 pt-24 backdrop-blur-sm sm:px-8"
          >
            <ol className="mx-auto max-w-4xl">
              {CHAPTERS.map((ch, i) => (
                <motion.li
                  key={ch.id}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.03 }}
                  className="border-b border-line"
                >
                  <button
                    type="button"
                    onClick={() => go(i)}
                    className={`flex w-full items-baseline gap-6 py-4 text-left transition-colors hover:text-paper ${
                      i === current ? "text-paper" : "text-paper-dim"
                    }`}
                  >
                    <span className="num w-8 text-sm text-gold">{String(ch.n).padStart(2, "0")}</span>
                    <span className="font-display text-3xl sm:text-4xl">{ch.short}</span>
                  </button>
                </motion.li>
              ))}
            </ol>
          </motion.div>
        ) : null}
      </AnimatePresence>

      {/* chapter dots (desktop) */}
      <nav aria-label="Chapter progress" className="site-chrome fixed right-5 top-1/2 z-30 hidden -translate-y-1/2 flex-col gap-3 xl:flex">
        {CHAPTERS.map((ch, i) => (
          <button
            key={ch.id}
            type="button"
            onClick={() => go(i)}
            className="group flex items-center justify-end gap-3"
            aria-label={`Chapter ${ch.n}: ${ch.short}`}
            aria-current={i === current ? "step" : undefined}
          >
            <span className="pointer-events-none font-mono text-[0.62rem] uppercase tracking-[0.14em] text-muted opacity-0 transition-opacity group-hover:opacity-100">
              {ch.short}
            </span>
            <span
              className={`block h-[2px] transition-all ${i === current ? "w-8 bg-gold" : "w-4 bg-line-strong group-hover:bg-paper-dim"}`}
            />
          </button>
        ))}
      </nav>

      {present ? (
        <div className="fixed bottom-4 left-1/2 z-50 -translate-x-1/2 rounded-full border border-line bg-ink/90 px-4 py-2 font-mono text-[0.65rem] uppercase tracking-[0.14em] text-muted">
          {String(c.n).padStart(2, "0")} / {String(CHAPTERS.length).padStart(2, "0")} · ← → to move · Esc to exit
        </div>
      ) : null}

      <AnimatePresence>
        {help ? (
          <motion.div
            role="dialog"
            aria-label="Keyboard shortcuts"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 8 }}
            className="fixed bottom-6 right-6 z-50 w-72 rounded-sm border border-line bg-graphite p-5 text-sm text-paper-dim shadow-2xl"
          >
            <div className="kicker mb-3">Keyboard</div>
            <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-2 font-mono text-[0.72rem]">
              <dt className="text-paper">→ / j</dt>
              <dd>Next chapter</dd>
              <dt className="text-paper">← / k</dt>
              <dd>Previous chapter</dd>
              <dt className="text-paper">1 … 9</dt>
              <dd>Jump to a section</dd>
              <dt className="text-paper">p</dt>
              <dd>Presentation mode</dd>
              <dt className="text-paper">Esc</dt>
              <dd>Close / exit</dd>
            </dl>
          </motion.div>
        ) : null}
      </AnimatePresence>
    </>
  );
}
