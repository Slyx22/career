import Link from "next/link";

export function Footer() {
  return (
    <footer className="mt-20 border-t border-line">
      <div className="mx-auto flex max-w-5xl flex-col gap-2 px-6 py-8 text-sm text-slate sm:flex-row sm:items-center sm:justify-between">
        <p>Career Readiness Analyzer &mdash; a skills-based readiness assessment, not a professional accreditation.</p>
        <nav className="flex gap-4">
          <Link href="/terms" className="hover:text-ink focus-ring rounded-sm">Terms</Link>
          <Link href="/privacy" className="hover:text-ink focus-ring rounded-sm">Privacy</Link>
        </nav>
      </div>
    </footer>
  );
}
