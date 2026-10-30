import Link from "next/link";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { RotatingText } from "@/components/RotatingText";
import { ScoreRing } from "@/components/ScoreRing";
import { AnnotatedCv } from "@/components/AnnotatedCv";

// A sample result, shown in the hero so people see what they get.
const SAMPLE = {
  title: "Accounts Clerk",
  score: 72,
  skills: [
    { name: "Economics and accounting", pct: 86 },
    { name: "Microsoft Excel", pct: 92 },
    { name: "Customer service", pct: 0 },
  ],
};

const STEPS = [
  { t: "Upload your CV", d: "Pick your job title, South African or international, and upload a PDF or Word file." },
  { t: "See your score", d: "Find out which skills employers look for, which your CV shows, and what to add next." },
  { t: "Share your certificate", d: "Add it to LinkedIn or WhatsApp. Anyone can check it's genuine with one link." },
];

export default function HomePage() {
  return (
    <div className="min-h-screen">
      <Header />
      <main className="page-top">
        <section className="mx-auto grid max-w-5xl items-center gap-10 px-4 pb-14 sm:px-6 md:grid-cols-[1.15fr_0.85fr] md:pb-20">
          <div>
            <h1 className="font-display text-[2.6rem] font-semibold leading-[1.02] tracking-[-0.03em] text-ink sm:text-6xl">
              How <RotatingText /> are you for your next career?
            </h1>
            <p className="mt-5 max-w-md text-lg leading-relaxed text-slate">
              Upload your CV to get a readiness score for the job you want, clear next steps, and a certificate you
              can share.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link href="/analyze" className="btn-primary">
                Check my CV
              </Link>
              <a href="#how-it-works" className="glass btn-glass">
                How it works
              </a>
            </div>
            <p className="mt-6 text-sm text-slate">Free. Your CV file is never stored.</p>
          </div>

          <div className="glass-sheet mx-auto w-full max-w-sm p-6" aria-label="Example result">
            <p className="text-xs font-medium text-slate">Example result</p>
            <div className="mt-3 flex items-center gap-5">
              <ScoreRing score={SAMPLE.score} animate id="hero" />
              <div>
                <p className="font-display text-xl font-semibold leading-tight">{SAMPLE.title}</p>
                <p className="mt-1 text-sm text-slate">Career readiness</p>
              </div>
            </div>
            <ul className="mt-6 space-y-3">
              {SAMPLE.skills.map((s) => (
                <li key={s.name}>
                  <div className="flex justify-between text-sm">
                    <span>{s.name}</span>
                    <span className="text-slate">{s.pct ? `${s.pct}%` : "not found"}</span>
                  </div>
                  <div className="mt-1.5 h-1.5 rounded-full bg-ink/[0.08]">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-jacaranda to-brass-light"
                      style={{ width: `${s.pct}%` }}
                    />
                  </div>
                </li>
              ))}
            </ul>
            <p className="mt-5 rounded-2xl bg-white/60 px-3.5 py-2.5 text-sm">
              Next step: list customer service under Skills.
            </p>
          </div>
        </section>

        <section id="how-it-works" className="mx-auto max-w-5xl scroll-mt-28 px-4 sm:px-6">
          <h2 className="px-2 font-display text-2xl font-semibold tracking-tight">How it works</h2>
          <ol className="glass-sheet mt-4 grid divide-y divide-ink/[0.07] md:grid-cols-3 md:divide-x md:divide-y-0">
            {STEPS.map((s, i) => (
              <li key={s.t} className="p-6">
                <span className="flex h-8 w-8 items-center justify-center rounded-full bg-ink text-sm font-semibold text-white">
                  {i + 1}
                </span>
                <h3 className="mt-4 font-display text-lg font-semibold">{s.t}</h3>
                <p className="mt-1.5 text-sm leading-relaxed text-slate">{s.d}</p>
              </li>
            ))}
          </ol>
          <p className="mt-4 px-2 text-sm text-slate">
            Scores use skills data from O*NET, linked to South Africa&apos;s official list of job titles (OFO).
          </p>
        </section>

        <section className="mx-auto mt-20 max-w-5xl px-4 sm:px-6">
          <div className="max-w-xl px-2">
            <h2 className="font-display text-2xl font-semibold tracking-tight sm:text-3xl">
              Read line by line, the way an employer would
            </h2>
            <p className="mt-3 leading-relaxed text-slate">
              Your result looks at what each line of your CV shows: the skills your job needs, what South African
              employers ask for, and details you may not want to share.
            </p>
          </div>
          <div className="glass-sheet mt-6 p-3 sm:p-5">
            <AnnotatedCv />
          </div>
          <p className="mt-4 px-2 text-sm text-slate">A made-up example. Your own result is based only on your CV.</p>
        </section>

        <section className="mx-auto mt-20 max-w-5xl px-4 sm:px-6">
          <div className="glass-sheet flex flex-col items-start gap-5 p-6 sm:flex-row sm:items-center sm:justify-between sm:p-8">
            <div>
              <p className="font-display text-xl font-semibold tracking-tight">Free for job seekers, always.</p>
              <p className="mt-1 text-sm text-slate">Takes about a minute. Your CV file is never stored.</p>
            </div>
            <Link href="/analyze" className="btn-primary shrink-0">
              Check my CV
            </Link>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
}
