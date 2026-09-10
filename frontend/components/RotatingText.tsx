"use client";

import { useEffect, useState } from "react";

const ROTATING_WORDS = [
  "ready",
  "prepared",
  "qualified",
  "equipped",
  "confident",
];

export function RotatingText() {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => {
      setIsAnimating(true);
      setTimeout(() => {
        setCurrentIndex((prev) => (prev + 1) % ROTATING_WORDS.length);
        setIsAnimating(false);
      }, 200);
    }, 2500);

    return () => clearInterval(interval);
  }, []);

  return (
    <span
      className={`inline-block transition-all duration-200 ${
        isAnimating ? "scale-95 opacity-0" : "scale-100 opacity-100"
      }`}
    >
      {ROTATING_WORDS[currentIndex]}
    </span>
  );
}
