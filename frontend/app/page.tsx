import Link from "next/link";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { ReadinessGauge } from "@/components/ReadinessGauge";
import { RotatingText } from "@/components/RotatingText";

export default function HomePage() {
  return (
    <div className="relative min-h-screen overflow-hidden bg-void text-paper">
      {/* Subtle radial glow behind hero */}
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_50%_20%,rgba(184,128,31,0.15),transparent_60%)]" />

      <div className="relative z-10">
        <Header />
        <main className="flex-1">
          <section className="mx-auto max-w-5xl px-6 pt-28 pb-16 md:pt-36 md:pb-24">
            <div className="grid gap-12 md:grid-cols-5 md:items-center">
              <div className="md:col-span-3">
                <p className="mb-4 font-body text-sm text-brass">Career Readiness Analyzer</p>
                <h1 className="font-display text-4xl leading-tight text-paper md:text-6xl">
                  How <RotatingText /> are you for your next career?
                </h1>
                <p className="mt-6 max-w-md font-body text-base leading-relaxed text-paper/70">
                  Upload your CV, get an explainable readiness score, and earn a verified certificate employers trust.
                </p>
                <Link
                  href="/analyze"
                  className="mt-8 inline-flex items-center gap-2 rounded-full bg-brass px-7 py-3.5 font-body text-sm font-medium text-void shadow-lg shadow-brass/30 transition hover:bg-brass-dark hover:shadow-xl hover:shadow-brass/20"
                >
                  Get Your Certificate
                  <span aria-hidden>→</span>
                </Link>
              </div>

              {/* Dashed curved arrow pointing to CTA */}
              <div className="hidden md:col-span-2 md:block md:relative md:h-64">
                <svg viewBox="0 0 240 200" className="h-full w-full" aria-hidden="true">
                  <defs>
                    <filter id="glow">
                      <feDropShadow dx="0" dy="0" stdDeviation="2" floodColor="#b8801f" floodOpacity="0.35" />
                    </filter>
                  </defs>
                  <path
                    d="M 30 160 C 70 120, 140 60, 200 80"
                    fill="none"
                    stroke="#b8801f"
                    strokeWidth="2"
                    strokeDasharray="8 6"
                    strokeLinecap="round"
                    filter="url(#glow)"
                  />
                  {/* Animated dash offset via CSS on this group */}
                  <g>
                    <circle cx="200" cy="80" r="3.5" fill="#b8801f" />
                    <polygon points="200,80 192,72 196,78" fill="#b8801f" />
                  </g>
                </svg>
                <style>{`
                  @keyframes dash-move {
                    to { stroke-dashoffset: -28; }
                  }
                  .arrow-path { animation: dash-move 3s linear infinite; }
                `}</style>
                <path
                  className="arrow-path"
                  d="M 30 160 C 70 120, 140 60, 200 80"
                  fill="none"
                  stroke="#b8801f"
                  strokeWidth="2"
                  strokeDasharray="8 6"
                  strokeLinecap="round"
                  filter="url(#glow)"
                />
              </div>
            </div>
          </section>

          {/* Cards section — clean, premium spacing */}
          <section className="mx-auto max-w-5xl px-6 pb-24">
            <div className="grid gap-8 md:grid-cols-3">
              {[
                { n: "01", t: "Analyze", d: "Upload your CV and we extract skills with explainable NLP." },
                { n: "02", t: "Score", d: "Get a 0-100 career readiness score backed by market benchmarks." },
                { n: "03", t: "Certify", d: "Download a professional certificate with your verified score." },
              ].map((c) => (
                <div
                  key={c.n}
                  className="rounded-2xl border border-white/5 bg-white/[0.02] p-8 backdrop-blur transition hover:border-brass/30 hover:bg-white/[0.04] hover:shadow-lg hover:shadow-brass/5"
                >
                  <span className="inline-block rounded-full bg-brass/20 px-3 py-1 text-xs font-bold tracking-widest text-brass">{c.n}</span>
                  <h3 className="mt-5 font-display text-xl text-paper">{c.t}</h3>
                  <p className="mt-3 font-body text-sm leading-relaxed text-paper/60">{c.d}</p>
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
