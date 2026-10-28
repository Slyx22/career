import Link from "next/link";

export function Footer() {
  return (
    <footer className="page-bottom mx-auto mt-16 max-w-5xl px-4 print:hidden sm:px-6">
      <div className="flex flex-col gap-3 px-2 text-sm text-slate sm:flex-row sm:items-start sm:justify-between">
        <div className="max-w-xl space-y-1">
          <p>Career Readiness Analyzer is a skills-based readiness assessment, not a professional accreditation.</p>
          <p className="text-xs">
            Includes data from the{" "}
            <a
              href="https://www.onetcenter.org/database.html"
              className="underline decoration-ink/20 underline-offset-2 hover:text-ink"
              rel="noopener noreferrer"
              target="_blank"
            >
              O*NET Database
            </a>{" "}
            (USDOL/ETA), used under CC BY 4.0 and modified by us.
          </p>
        </div>
        <nav className="flex gap-1" aria-label="Legal">
          <Link href="/terms" className="focus-ring rounded-full px-3 py-1.5 hover:text-ink">
            Terms
          </Link>
          <Link href="/privacy" className="focus-ring rounded-full px-3 py-1.5 hover:text-ink">
            Privacy
          </Link>
        </nav>
      </div>
    </footer>
  );
}
