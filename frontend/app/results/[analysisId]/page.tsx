import Link from "next/link";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { ScoreRing } from "@/components/ScoreRing";
import { SkillBar } from "@/components/SkillBar";
import { GenerateCertificateButton } from "@/components/GenerateCertificateButton";
import { FeatureInterestSurvey } from "@/components/FeatureInterestSurvey";
import { TrackView } from "@/components/TrackView";
import { fetchAnalysis } from "@/lib/serverApi";
import { SkillBreakdownItem } from "@/lib/types";

// Job-specific groups first, broad skills after, tools last.
const CATEGORY_ORDER = ["Knowledge", "Technical skills", "Management", "Core skills", "People skills"];

function groupByCategory(items: SkillBreakdownItem[]) {
  const groups = new Map<string, SkillBreakdownItem[]>();
  for (const item of items) {
    const key = item.is_tool ? "Tools and software" : item.category;
    const list = groups.get(key) ?? [];
    list.push(item);
    groups.set(key, list);
  }
  const rank = (k: string) => {
    if (k === "Tools and software") return 99;
    const i = CATEGORY_ORDER.indexOf(k);
    return i === -1 ? 50 : i;
  };
  return Array.from(groups.entries()).sort((a, b) => rank(a[0]) - rank(b[0]));
}

export default async function ResultsPage({
  params,
}: {
  params: { analysisId: string };
}) {
  const analysis = await fetchAnalysis(params.analysisId);

  if (!analysis) {
    return (
      <div className="min-h-screen">
        <Header />
        <main className="page-top mx-auto max-w-xl px-4">
          <section className="glass-sheet p-8 text-center">
            <h1 className="font-display text-2xl text-ink">
              Analysis not found
            </h1>
            <p className="mt-3 text-sm text-slate">
              This analysis may have been removed or the link is incorrect. Check your CV again to get a new result.
            </p>
            <Link href="/analyze" className="btn-primary mt-6">
              Check my CV
            </Link>
          </section>
        </main>
        <Footer />
      </div>
    );
  }

  const grouped = groupByCategory(analysis.skill_breakdown);

  const reqs = analysis.sa_requirements ?? [];

  return (
    <div className="min-h-screen">
      <Header />
      <main className="page-top mx-auto max-w-3xl space-y-5 px-4 sm:px-6">
        <TrackView
          event="results_view"
          career={analysis.career_slug}
          careerLabel={analysis.career}
          detail={analysis.score >= 70 ? "score_70_plus" : "score_below_70"}
        />
        <section className="glass-sheet p-6 sm:p-8">
          <div className="flex flex-col items-center gap-6 text-center sm:flex-row sm:text-left">
            <ScoreRing score={analysis.score} size={148} animate id="result" />
            <div className="min-w-0">
              <p className="text-sm text-slate">Career readiness for</p>
              <h1 className="mt-1 font-display text-2xl font-semibold leading-tight tracking-tight sm:text-3xl">
                {analysis.career}
              </h1>
              {analysis.onet_career && analysis.onet_career !== analysis.career && (
                <p className="mt-2 text-xs leading-relaxed text-slate">
                  Skills compared with the international occupation &ldquo;{analysis.onet_career}&rdquo; (O*NET),
                  the closest match to this South African job title.
                </p>
              )}
            </div>
          </div>
          <div className="mt-6 border-t border-ink/[0.07] pt-6">
            <GenerateCertificateButton
              analysisId={analysis.analysis_id}
              firstName={analysis.first_name}
              surname={analysis.surname}
              careerSlug={analysis.career_slug}
              careerLabel={analysis.career}
            />
          </div>
        </section>

        <section className="glass-sheet p-6 sm:p-8">
          <h2 className="font-display text-xl font-semibold tracking-tight">Your next steps</h2>
          <p className="mt-1 text-sm text-slate">Most valuable first. Each one adds clear evidence to your CV.</p>
          <ol className="mt-5 space-y-3">
            {analysis.recommendations.map((rec, i) => (
              <li key={i} className="flex gap-3 rounded-2xl bg-white/55 p-3.5 text-sm leading-relaxed">
                <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-ink text-xs font-semibold text-white">
                  {i + 1}
                </span>
                <span>{rec}</span>
              </li>
            ))}
          </ol>
        </section>

        <section className="glass-sheet grid grid-cols-1 gap-8 p-6 sm:p-8 md:grid-cols-2">
          <div>
            <h2 className="font-display text-xl font-semibold tracking-tight">Strengths</h2>
            <ul className="mt-4 space-y-2.5">
              {analysis.strengths.length === 0 && (
                <li className="text-sm text-slate">No strong evidence found yet for this job&apos;s core skills.</li>
              )}
              {analysis.strengths.map((s) => (
                <li key={s} className="flex items-center gap-2.5 text-sm">
                  <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-jacaranda/15 text-[11px] text-jacaranda-dark">
                    &#10003;
                  </span>
                  {s}
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h2 className="font-display text-xl font-semibold tracking-tight">Biggest gaps</h2>
            <ul className="mt-4 space-y-2.5">
              {analysis.gaps.length === 0 && <li className="text-sm text-slate">No major gaps found.</li>}
              {analysis.gaps.map((g) => (
                <li key={g} className="flex items-center gap-2.5 text-sm">
                  <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-brass/15 text-[11px] font-semibold text-brass-dark">
                    !
                  </span>
                  {g}
                </li>
              ))}
            </ul>
          </div>
        </section>

        {reqs.length > 0 && (
          <section className="glass-sheet p-6 sm:p-8">
            <h2 className="font-display text-xl font-semibold tracking-tight">Required in South Africa</h2>
            <p className="mt-1 text-sm text-slate">
              Employers usually check these for this job. They don&apos;t change your score, but if you have them,
              make sure your CV says so clearly.
            </p>
            <ul className="mt-4 space-y-3">
              {reqs.map((r) => (
                <li key={r.key} className="rounded-2xl bg-white/55 p-3.5">
                  <div className="flex flex-wrap items-center gap-2">
                    <strong className="text-sm">{r.label}</strong>
                    <span
                      className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${
                        r.found_in_cv ? "bg-jacaranda/15 text-jacaranda-dark" : "bg-ink/[0.06] text-slate"
                      }`}
                    >
                      {r.found_in_cv ? "Mentioned in your CV" : "Not found in your CV"}
                    </span>
                  </div>
                  <p className="mt-1 text-xs leading-relaxed text-slate">{r.detail}</p>
                </li>
              ))}
            </ul>
          </section>
        )}

        <section className="glass-sheet p-6 sm:p-8">
          <h2 className="font-display text-xl font-semibold tracking-tight">Skill breakdown</h2>
          <p className="mt-1 text-sm text-slate">
            How strongly your CV shows each skill. Essential and Important skills count most. Missing skills come
            with a tip on how to show them.
          </p>
          <div className="mt-6 space-y-7">
            {grouped.map(([category, items]) => (
              <div key={category}>
                <h3 className="text-sm font-semibold text-slate">
                  {category}
                  {category === "Tools and software" && (
                    <span className="ml-1 font-normal">
                      ({items.filter((i) => i.present).length} of {items.length} found, any 3 give full credit)
                    </span>
                  )}
                </h3>
                <div className="mt-1 divide-y divide-ink/[0.06]">
                  {items.map((item) => (
                    <SkillBar key={item.slug} item={item} />
                  ))}
                </div>
              </div>
            ))}
          </div>
        </section>

        <FeatureInterestSurvey analysisId={analysis.analysis_id} />

        <p className="px-2 text-xs leading-relaxed text-slate">{analysis.benchmark_disclaimer}</p>
      </main>
      <Footer />
    </div>
  );
}
