"use client";

import { useCallback, useEffect, useRef, useState } from "react";

type Mark = "found" | "fix" | "private";

// A short, made-up South African CV and the notes a result gives on it.
// The notes use the same wording style as real results.
const LINES: { text: string; mark?: Mark; note?: string; className?: string }[] = [
  { text: "Thandi Mokoena", className: "font-display text-lg font-semibold text-ink" },
  { text: "Pretoria", className: "text-xs text-slate" },
  { text: "ID number 9X0X1X 5XXX 08X", mark: "private", note: "Employers don't need your ID number. It's a privacy risk on a CV that gets forwarded." },
  { text: "Experience", className: "mt-3 text-xs font-semibold text-slate" },
  { text: "Accounts Clerk, Mabena Trading, 2021 to 2024" },
  { text: "Responsible for creditors and debtors", mark: "fix", note: "Reads as a duty. Say what the result was, with a number." },
  { text: "Reconciled 200+ supplier accounts every month", mark: "found", note: "Economics and accounting: shown, with scale." },
  { text: "Education", className: "mt-3 text-xs font-semibold text-slate" },
  { text: "Matric, Hoërskool Pretoria, 2018", mark: "found", note: "Matric: employers for this job usually ask for it." },
  { text: "Skills", className: "mt-3 text-xs font-semibold text-slate" },
  { text: "Excel, Sage Pastel, teamwork", mark: "found", note: "Accounting software listed, as clerk adverts usually ask." },
];

const NOTE_ICON: Record<Mark, string> = { found: "✓", fix: "!", private: "!" };
const TOTAL_FOUND = LINES.filter((l) => l.mark === "found").length;
const TOTAL_CHECK = LINES.filter((l) => l.mark === "fix" || l.mark === "private").length;

// Timing, in seconds. The beam crosses the paper in SCAN; each line lights
// up when the beam reaches it, then its connector and note follow.
const START = 0.35;
const SCAN = 3.2;

/**
 * The home page's animated moment. When the sample CV scrolls into view, a
 * soft scanning beam moves down the paper; each marked line is highlighted
 * as the beam reaches it, a connector draws out to its note, and the
 * counters tick up. It resets when scrolled out of view, so it plays again
 * each time you come back to it. Reduced-motion users see the result.
 */
export function AnnotatedCv() {
  const rootRef = useRef<HTMLDivElement>(null);
  const paperRef = useRef<HTMLDivElement>(null);
  const timers = useRef<number[]>([]);
  const [phase, setPhase] = useState<"idle" | "playing" | "done">("idle");
  const [found, setFound] = useState(0);
  const [check, setCheck] = useState(0);
  const [delays, setDelays] = useState<number[]>([]);

  const clearTimers = () => {
    timers.current.forEach((t) => window.clearTimeout(t));
    timers.current = [];
  };

  // Each marked line's start time comes from where it sits on the paper, so
  // the highlight happens exactly as the beam passes it (on any screen size).
  const measure = useCallback(() => {
    const paper = paperRef.current;
    if (!paper) return [];
    const h = paper.offsetHeight || 1;
    const rows = Array.from(paper.querySelectorAll<HTMLElement>("[data-mark]"));
    return rows.map((row) => START + (row.offsetTop / h) * SCAN);
  }, []);

  const play = useCallback(() => {
    clearTimers();
    const d = measure();
    setDelays(d);
    setFound(0);
    setCheck(0);
    setPhase("idle");
    // Next frame: start, so the reset above is painted first.
    requestAnimationFrame(() =>
      requestAnimationFrame(() => {
        setPhase("playing");
        const marks = LINES.filter((l) => l.mark);
        marks.forEach((line, i) => {
          const at = ((d[i] ?? 0) + 0.45) * 1000;
          timers.current.push(
            window.setTimeout(() => {
              if (line.mark === "found") setFound((n) => n + 1);
              else setCheck((n) => n + 1);
            }, at)
          );
        });
        timers.current.push(window.setTimeout(() => setPhase("done"), (START + SCAN + 0.6) * 1000));
      })
    );
  }, [measure]);

  const reset = useCallback(() => {
    clearTimers();
    setPhase("idle");
    setFound(0);
    setCheck(0);
  }, []);

  useEffect(() => {
    const el = rootRef.current;
    if (!el) return;
    const reduced = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
    if (reduced || !("IntersectionObserver" in window)) {
      setDelays(measure());
      setFound(TOTAL_FOUND);
      setCheck(TOTAL_CHECK);
      setPhase("done");
      return;
    }
    let visible = false;
    const io = new IntersectionObserver(
      (entries) => {
        for (const e of entries) {
          // Play when a good part of it is on screen; reset only once it has
          // left the screen completely, so small scrolls don't restart it.
          if (e.intersectionRatio >= 0.35 && !visible) {
            visible = true;
            play();
          } else if (e.intersectionRatio === 0 && visible) {
            visible = false;
            reset();
          }
        }
      },
      { threshold: [0, 0.35] }
    );
    io.observe(el);
    return () => {
      io.disconnect();
      clearTimers();
    };
  }, [measure, play, reset]);

  let markIndex = 0;
  return (
    <div ref={rootRef} className={`annotated-cv is-${phase}`} style={{ ["--scan" as string]: `${SCAN}s` }}>
      <div ref={paperRef} className="annotated-paper" aria-label="Sample CV with notes from a result">
        <div className="annotated-beam" aria-hidden />
        <div className="annotated-tally" aria-hidden>
          <span className="annotated-pill pill-found">
            <b>{found}</b> found
          </span>
          <span className="annotated-pill pill-check">
            <b>{check}</b> to check
          </span>
        </div>
        {LINES.map((line) => {
          if (!line.mark) {
            return (
              <p key={line.text} className={`annotated-line ${line.className ?? "text-sm text-ink"}`}>
                {line.text}
              </p>
            );
          }
          const i = markIndex++;
          return (
            <div
              key={line.text}
              data-mark
              className={`annotated-row mark-${line.mark}`}
              style={{ ["--d" as string]: `${delays[i] ?? START + i * 0.6}s` }}
            >
              <p className="annotated-line text-sm text-ink">
                <span className="annotated-hl">
                  {line.mark === "private" ? <span className="annotated-redact">{line.text}</span> : line.text}
                </span>
              </p>
              <p className="annotated-note">
                <span className="annotated-icon" aria-hidden>
                  {NOTE_ICON[line.mark]}
                </span>
                <span>{line.note}</span>
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
