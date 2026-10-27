import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { ReadinessGauge } from "@/components/ReadinessGauge";
import { SkillBar } from "@/components/SkillBar";
import { GenerateCertificateButton } from "@/components/GenerateCertificateButton";
import { FeatureInterestSurvey } from "@/components/FeatureInterestSurvey";
import { fetchAnalysis } from "@/lib/serverApi";
import { SkillBreakdownItem } from "@/lib/types";

function groupByCategory(items: SkillBreakdownItem[]) {
  const groups = new Map<string, SkillBreakdownItem[]>();
  for (const item of items) {
    const list = groups.get(item.category) ?? [];
    list.push(item);
    groups.set(item.category, list);
  }
  return Array.from(groups.entries());
}

export default async function ResultsPage({
  params,
}: {
  params: { analysisId: string };
}) {
  const analysis = await fetchAnalysis(params.analysisId);

  if (!analysis) {
    return (
      <div className="flex min-h-screen flex-col">
        <Header />
        <main className="flex-1 bg-paper">
          <section className="mx-auto max-w-xl px-6 py-24 text-center">
            <h1 className="font-display text-2xl text-ink">
              Analysis not found
            </h1>
            <p className="mt-3 font-body text-sm text-slate-600">
              This analysis may have expired or the link is incorrect. Please
              run a new analysis.
            </p>
          </section>
        </main>
        <Footer />
      </div>
    );
  }

  const grouped = groupByCategory(analysis.skill_breakdown);

  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1 bg-paper">
        <section className="mx-auto max-w-3xl px-6 py-16">
          <div className="flex flex-col items-center border border-line bg-panel px-8 py-10 text-center">
            <ReadinessGauge score={analysis.score} />
            <p className="mt-4 font-display text-xl text-ink">
              {analysis.career}
            </p>
            <p className="mt-1 font-body text-xs text-slate-600">
              Career Readiness
            </p>
            {analysis.onet_career && analysis.onet_career !== analysis.career && (
              <p className="mt-3 max-w-md font-body text-xs text-slate-500">
                Skills compared with the international occupation &ldquo;{analysis.onet_career}&rdquo;
                (O*NET), the closest match to this South African job title.
              </p>
            )}
          </div>

          {analysis.sa_requirements && analysis.sa_requirements.length > 0 && (
            <div className="mt-10 border border-line bg-panel px-6 py-6">
              <h2 className="font-display text-xl text-ink">Required in South Africa</h2>
              <p className="mt-1 font-body text-xs text-slate-600">
                Employers in South Africa usually check these for this job. They don&apos;t change your
                score, but if you have them, make sure your CV says so clearly.
              </p>
              <ul className="mt-4 space-y-3">
                {analysis.sa_requirements.map((r) => (
                  <li key={r.key} className="font-body text-sm text-ink">
                    <span className={r.found_in_cv ? "text-brass-dark" : "text-slate-500"}>
                      {r.found_in_cv ? "\u2713" : "\u25cb"}
                    </span>{" "}
                    <strong>{r.label}</strong>
                    <span className="text-slate-600">
                      {" "}
                      &mdash; {r.found_in_cv ? "mentioned in your CV." : "not found in your CV."}
                    </span>
                    <span className="mt-0.5 block text-xs text-slate-600">{r.detail}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="tick-rule mt-12" />

          <div className="mt-10 grid grid-cols-1 gap-10 md:grid-cols-2">
            <div>
              <h2 className="font-display text-xl text-ink">Strengths</h2>
              <ul className="mt-4 space-y-2">
                {analysis.strengths.length === 0 && (
                  <li className="font-body text-sm text-slate-600">
                    No strong evidence found yet for this career&apos;s core skills.
                  </li>
                )}
                {analysis.strengths.map((s) => (
                  <li key={s} className="font-body text-sm text-ink">
                    <span className="text-brass-dark">&#10003;</span> {s}
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h2 className="font-display text-xl text-ink">Biggest gaps</h2>
              <ul className="mt-4 space-y-2">
                {analysis.gaps.length === 0 && (
                  <li className="font-body text-sm text-slate-600">
                    No major gaps identified.
                  </li>
                )}
                {analysis.gaps.map((g) => (
                  <li key={g} className="font-body text-sm text-ink">
                    <span className="text-brass-dark">&#9888;</span> {g}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="mt-14">
            <h2 className="font-display text-xl text-ink">Skill breakdown</h2>
            <div className="mt-6 space-y-8">
              {grouped.map(([category, items]) => (
                <div key={category}>
                  <h3 className="font-body text-xs uppercase tracking-normal text-slate-600">
                    {category}
                  </h3>
                  <div className="mt-1 divide-y divide-line">
                    {items.map((item) => (
                      <SkillBar key={item.slug} item={item} />
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-14">
            <h2 className="font-display text-xl text-ink">
              Recommended next steps
            </h2>
            <ol className="mt-4 space-y-3">
              {analysis.recommendations.map((rec, i) => (
                <li key={i} className="font-body text-sm text-ink">
                  {i + 1}. {rec}
                </li>
              ))}
            </ol>
          </div>

          <div className="mt-14">
            <FeatureInterestSurvey analysisId={analysis.analysis_id} />
          </div>

          <p className="mt-10 font-body text-xs text-slate-600">
            {analysis.benchmark_disclaimer}
          </p>

          <div className="mt-10">
            <GenerateCertificateButton
              analysisId={analysis.analysis_id}
              firstName={analysis.first_name}
              surname={analysis.surname}
            />
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
}
