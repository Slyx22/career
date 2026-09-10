import Link from "next/link";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { ReadinessGauge } from "@/components/ReadinessGauge";
import { RotatingText } from "@/components/RotatingText";

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col">
      <Header />

      <main className="flex-1">
        <section className="mx-auto grid max-w-5xl grid-cols-1 items-center gap-12 px-6 py-20 md:grid-cols-5">
          <div className="md:col-span-3">
            <p className="mb-4 font-body text-sm text-brass-dark">
              Career Readiness Analyzer
            </p>
            <h1 className="font-display text-4xl leading-tight text-ink md:text-5xl">
              How <RotatingText /> are you for your next career?
            </h1>
            <p className="mt-6 max-w-md font-body text-base leading-relaxed text-slate">
              Upload your CV, get your readiness score, and earn a verified
              certificate to showcase your career preparedness to employers.
            </p>
            <Link
              href="/analyze"
              className="focus-ring mt-8 inline-block rounded-lg bg-ink px-6 py-3 font-body text-sm font-medium text-paper shadow-sm transition-all hover:scale-[1.02] hover:bg-brass-dark hover:shadow-md"
            >
              Get Your Certificate →
            </Link>
          </div>

          <div className="md:col-span-2">
            <div className="rounded-xl border border-line bg-gradient-to-br from-panel to-paper p-8 shadow-sm">
              <ReadinessGauge score={73} size={220} />
              <p className="mt-2 text-center font-body text-xs text-slate">
                Example readiness score
              </p>
            </div>
          </div>
        </section>

        <div className="tick-rule" />

        <section className="mx-auto max-w-5xl px-6 py-16">
          <h2 className="font-display text-2xl text-ink">How it works</h2>
          <ol className="mt-8 grid grid-cols-1 gap-6 md:grid-cols-3">
            <li className="group rounded-xl border border-line bg-panel p-6 transition-all hover:border-brass/50 hover:shadow-md">
              <div className="mb-3 inline-flex h-10 w-10 items-center justify-center rounded-lg bg-brass/10">
                <p className="font-display text-lg font-semibold text-brass-dark">1</p>
              </div>
              <h3 className="mt-2 font-body text-base font-semibold text-ink">
                Upload your CV
              </h3>
              <p className="mt-2 font-body text-sm leading-relaxed text-slate">
                Tell us your name and choose a target career, then upload a
                PDF or DOCX CV.
              </p>
            </li>
            <li className="group rounded-xl border border-line bg-panel p-6 transition-all hover:border-brass/50 hover:shadow-md">
              <div className="mb-3 inline-flex h-10 w-10 items-center justify-center rounded-lg bg-brass/10">
                <p className="font-display text-lg font-semibold text-brass-dark">2</p>
              </div>
              <h3 className="mt-2 font-body text-base font-semibold text-ink">
                Get an evidence-based score
              </h3>
              <p className="mt-2 font-body text-sm leading-relaxed text-slate">
                Our engine reads what you&apos;ve actually done, not just
                which words appear, to score your readiness out of 100.
              </p>
            </li>
            <li className="group rounded-xl border border-line bg-panel p-6 transition-all hover:border-brass/50 hover:shadow-md">
              <div className="mb-3 inline-flex h-10 w-10 items-center justify-center rounded-lg bg-brass/10">
                <p className="font-display text-lg font-semibold text-brass-dark">3</p>
              </div>
              <h3 className="mt-2 font-body text-base font-semibold text-ink">
                Get your certificate
              </h3>
              <p className="mt-2 font-body text-sm leading-relaxed text-slate">
                Generate a shareable Career Readiness Certificate with a
                public verification link.
              </p>
            </li>
          </ol>
        </section>
      </main>

      <Footer />
    </div>
  );
}
