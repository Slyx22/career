"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { AuthSection } from "@/components/AuthSection";

export function Header() {
  const [visible, setVisible] = useState(false);
  const [lastY, setLastY] = useState(0);

  useEffect(() => {
    const onScroll = () => {
      const y = window.scrollY;
      if (y < 40) {
        setVisible(false);
        setLastY(y);
        return;
      }
      if (y > lastY) {
        // scrolling down → hide
        setVisible(false);
      } else {
        // scrolling up → show
        setVisible(true);
      }
      setLastY(y);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, [lastY]);

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 mx-auto max-w-full bg-white/80 backdrop-blur-2xl border-b border-black/5 shadow-[0_1px_0_rgba(0,0,0,0.02)] transition-transform duration-500 ease-[cubic-bezier(0.22,1,0.36,1)] ${
        visible ? "translate-y-0" : "-translate-y-full"
      }`}
    >
      <div className="mx-auto max-w-6xl px-6 py-4 flex items-center justify-between gap-8">
        <Link href="/" className="shrink-0 flex items-baseline gap-3">
          <span className="font-display text-2xl italic text-ink tracking-tight">Readiness</span>
          <span className="font-body text-sm text-slate hidden sm:inline">Career Readiness Analyzer</span>
        </Link>
        <nav className="flex items-center gap-8 font-body text-sm text-ink ml-auto">
          <Link href="/analyze" className="hover:text-brass transition-colors whitespace-nowrap">Check my readiness</Link>
          <div className="shrink-0"><AuthSection /></div>
        </nav>
      </div>
    </header>
  );
}