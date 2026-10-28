"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { BadgeIcon, HomeIcon, ScanIcon } from "@/components/Icons";

const TABS = [
  { href: "/", label: "Home", Icon: HomeIcon, match: (p: string) => p === "/" },
  { href: "/analyze", label: "Check my CV", Icon: ScanIcon, match: (p: string) => p.startsWith("/analyze") || p.startsWith("/results") },
  {
    href: "/dashboard",
    label: "Certificates",
    Icon: BadgeIcon,
    match: (p: string) => p.startsWith("/dashboard") || p.startsWith("/certificate") || p.startsWith("/verify"),
  },
];

/** iOS-style floating glass tab bar, phones and small tablets only. */
export function MobileTabBar() {
  const pathname = usePathname() || "/";
  return (
    <nav
      aria-label="Main"
      className="fixed inset-x-0 z-50 flex justify-center px-4 print:hidden md:hidden"
      style={{ bottom: "calc(0.75rem + env(safe-area-inset-bottom, 0px))" }}
    >
      <div className="glass flex w-full max-w-sm items-stretch gap-1 rounded-full p-1.5">
        {TABS.map(({ href, label, Icon, match }) => {
          const active = match(pathname);
          return (
            <Link
              key={href}
              href={href}
              aria-current={active ? "page" : undefined}
              className={`focus-ring flex min-h-[52px] flex-1 flex-col items-center justify-center gap-0.5 rounded-full text-[11px] font-medium transition-colors ${
                active ? "lens text-jacaranda-dark" : "text-slate"
              }`}
            >
              <Icon />
              {label}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
