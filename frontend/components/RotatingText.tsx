"use client";

import { useEffect, useState } from "react";

const ROTATING_WORDS = ["ready", "prepared", "qualified", "equipped", "confident"];

/** Cycles through words; sits at its natural width so there are no gaps. */
export function RotatingText() {
  const [i, setI] = useState(0);
  const [fading, setFading] = useState(false);

  useEffect(() => {
    if (window.matchMedia?.("(prefers-reduced-motion: reduce)").matches) return;
    const id = setInterval(() => {
      setFading(true);
      setTimeout(() => {
        setI((n) => (n + 1) % ROTATING_WORDS.length);
        setFading(false);
      }, 220);
    }, 2600);
    return () => clearInterval(id);
  }, []);

  return (
    <span className={`inline-block transition-opacity duration-200 ${fading ? "opacity-0" : "opacity-100"}`} aria-live="off">
      {ROTATING_WORDS[i]}
    </span>
  );
}
