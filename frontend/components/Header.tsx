"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { AccountButton, WhenSignedIn } from "@/components/AuthSection";
import { MarkIcon } from "@/components/Icons";

const NAV = [
  { href: "/analyze", label: "Check my CV", signedInOnly: false },
  { href: "/dashboard", label: "My certificates", signedInOnly: true },
];

/**
 * Floating glass bar. On phones it holds just the logo and the account
 * button; the main navigation moves to the tab bar at the bottom.
 */
export function Header() {
  const pathname = usePathname() || "/";

  return (
    <header
      className="fixed inset-x-0 z-50 px-3 print:hidden sm:px-6"
      style={{ top: "calc(0.75rem + env(safe-area-inset-top, 0px))" }}
    >
      <div className="glass mx-auto flex h-14 max-w-5xl items-center gap-2 rounded-full pl-3 pr-2.5 sm:pl-4">
        <Link href="/" className="focus-ring flex shrink-0 items-center gap-2 rounded-full pr-2" aria-label="Home">
          <MarkIcon />
          <span className="font-display text-lg font-semibold tracking-tight text-ink">Readiness</span>
        </Link>

        <nav className="ml-auto hidden items-center gap-1 md:flex" aria-label="Main">
          {NAV.map((item) => {
            const active = pathname.startsWith(item.href);
            const link = (
              <Link
                key={item.href}
                href={item.href}
                aria-current={active ? "page" : undefined}
                className={`focus-ring rounded-full px-4 py-2 text-sm font-medium transition-colors ${
                  active ? "lens text-ink" : "text-slate hover:text-ink"
                }`}
              >
                {item.label}
              </Link>
            );
            return item.signedInOnly ? <WhenSignedIn key={item.href}>{link}</WhenSignedIn> : link;
          })}
        </nav>

        <div className="ml-auto flex items-center pl-1 md:ml-2">
          <AccountButton />
        </div>
      </div>
    </header>
  );
}
