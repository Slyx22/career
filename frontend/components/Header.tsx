import Link from "next/link";
import { AuthSection } from "@/components/AuthSection";

export function Header() {
  return (
    <header className="border-b border-line bg-paper/95 backdrop-blur">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-5">
        <Link href="/" className="flex items-baseline gap-2">
          <span className="font-display text-xl italic text-ink">
            Readiness
          </span>
          <span className="font-body text-sm text-slate">
            Career Readiness Analyzer
          </span>
        </Link>
        <nav className="flex items-center gap-5 font-body text-sm text-slate">
          <Link href="/analyze" className="hover:text-ink focus-ring rounded-sm">
            Check my readiness
          </Link>
          <AuthSection />
        </nav>
      </div>
    </header>
  );
}
