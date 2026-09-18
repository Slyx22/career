"use client";

import Link from "next/link";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { ReadinessGauge } from "@/components/ReadinessGauge";
import { RotatingText } from "@/components/RotatingText";

export default function HomePage() {
  return (
    <div className="relative min-h-screen overflow-hidden bg-white text-slate-900">
      {/* Subtle radial glow behind hero */}
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_50%_10%,rgba(184,128,31,0.08),transparent_50%)]" />

      <div className="relative z-10">
        <Header />
        <main className="flex-1">
          <section className="mx-auto max-w-5xl px-6 pt-28 pb-16 md:pt-36 md:pb-24">
            <div className="grid gap-12 md:grid-cols-5 md:items-center">
              <div className="md:col-span-3">
                <p className="mb-4 font-body text-sm text-brass">Career Readiness Analyzer</p>
                <h1 className="font-display text-4xl leading-tight text-ink md:text-6xl">
                  How <RotatingText /> are you for your next career?
                </h1>
                <p className="mt-6 max-w-md font-body text-base leading-relaxed text-slate-700">
                  Upload your CV, get an explainable readiness score, and earn a verified certificate employers trust.
                </p>
                <Link
                  href="/analyze"
                  className="mt-8 inline-flex items-center gap-2 rounded-full bg-ink px-7 py-3.5 font-body text-sm font-medium text-paper shadow-xl shadow-ink/10 transition hover:bg-ink/90 hover:shadow-2xl"
                >
                  Get Your Certificate
                  <span aria-hidden>→</span>
                </Link>
              </div>

              {/* Dotted line removed per user request */}
            </div>
          </section>

          {/* Cards section — clean, premium spacing */}
          <section className="mx-auto max-w-5xl px-6 pb-24">
            <div className="grid gap-8 md:grid-cols-3 animate-fade-in-up delay-200">
              {[
                { n: "01", t: "Analyze", d: "Upload your CV and we extract skills with explainable NLP." },
                { n: "02", t: "Score", d: "Get a 0-100 career readiness score backed by market benchmarks." },
                { n: "03", t: "Certify", d: "Download a professional certificate with your verified score." },
              ].map((c) => (
                <div
                  key={c.n}
                  className="rounded-2xl border border-line bg-white p-8 shadow-sm shadow-black/5 transition hover:border-brass hover:shadow-lg hover:-translate-y-0.5"
                >
                  <span className="inline-block rounded-full bg-brass/20 px-3 py-1 text-xs font-bold tracking-widest text-brass">{c.n}</span>
                  <h3 className="mt-5 font-display text-xl text-ink">{c.t}</h3>
                  <p className="mt-3 font-body text-sm leading-relaxed text-slate-700">{c.d}</p>
                </div>
              ))}
            </div>
          </section>
        </main>
        <Footer />
      </div>
    </div>
  );
}
