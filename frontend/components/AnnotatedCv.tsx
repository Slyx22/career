"use client";

import { useEffect, useRef, useState } from "react";

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

/**
 * The home page's one animated moment: when it scrolls into view, a
 * highlighter runs over each marked line of a sample CV and its note
 * appears, in the same easing as the score ring. Plays once. People who
 * ask for reduced motion see the finished state straight away.
 */
export function AnnotatedCv() {
  const ref = useRef<HTMLDivElement>(null);
  const [playing, setPlaying] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (window.matchMedia?.("(prefers-reduced-motion: reduce)").matches || !("IntersectionObserver" in window)) {
      setPlaying(true);
      return;
    }
    const io = new IntersectionObserver(
      (entries) => {
        if (entries.some((e) => e.isIntersecting)) {
          setPlaying(true);
          io.disconnect();
        }
      },
      { threshold: 0.35 }
    );
    io.observe(el);
    return () => io.disconnect();
  }, []);

  let markIndex = 0;
  return (
    <div ref={ref} className={`annotated-cv ${playing ? "is-playing" : ""}`}>
      <div className="annotated-paper" aria-label="Sample CV with notes from a result">
        {LINES.map((line) => {
          if (!line.mark) {
            return (
              <p key={line.text} className={`annotated-line ${line.className ?? "text-sm text-ink"}`}>
                {line.text}
              </p>
            );
          }
          const order = markIndex++;
          return (
            <div
              key={line.text}
              className={`annotated-row mark-${line.mark}`}
              style={{ ["--i" as string]: order }}
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
