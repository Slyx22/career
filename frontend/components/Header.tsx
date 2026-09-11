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
        scrolled
          ? "mt-4 rounded-full border border-white/10 bg-void/70 backdrop-blur-xl shadow-2xl shadow-black/40"
          : "bg-transparent"
      }`}
    >
      <div className="flex items-center justify-between">
        <Link href="/" className="flex items-baseline gap-2">
          <span className="font-display text-xl italic text-paper">Readiness</span>
          <span className="font-body text-sm text-slate">Career Readiness Analyzer</span>
        </Link>
        <nav className="flex items-center gap-6 font-body text-sm text-paper/90">
          <Link href="/analyze" className="hover:text-brass transition-colors">Check my readiness</Link>
          <AuthSection />
        </nav>
      </div>
    </header>
  );
}
