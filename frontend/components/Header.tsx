"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { AuthSection } from "@/components/AuthSection";

export function Header() {
  const [scrolled, setScrolled] = useState(false);
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 40);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);
  return (
    <header
      className={`sticky top-0 z-50 mx-auto max-w-6xl px-6 py-4 transition-all duration-300 ${
        true
          ? "mt-4 rounded-full border border-white/10 bg-void/70 backdrop-blur-xl shadow-2xl shadow-black/40"
          : "rounded-full border border-white/10 bg-void/70 backdrop-blur-xl shadow-xl shadow-black/20"
      }`}
    >
      <div className="flex items-center justify-between gap-8">
        <Link href="/" className="shrink-0 flex items-baseline gap-3">
          <span className="font-display text-2xl italic text-paper tracking-tight">Readiness</span>
          <span className="font-body text-sm text-slate-700 hidden sm:inline">Career Readiness Analyzer</span>
        </Link>
        <nav className="flex items-center gap-8 font-body text-sm text-paper/90 ml-auto">
          <Link href="/analyze" className="hover:text-brass transition-colors whitespace-nowrap">Check my readiness</Link>
          <div className="shrink-0"><AuthSection /></div>
        </nav>
      </div>
    </header>
  );
}
