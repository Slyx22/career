import Link from "next/link";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { UsageStats } from "@/lib/adminStats";

const GOAL = 500;

export const RANGES = [
  { key: "7", label: "7 days", days: 7 },
  { key: "30", label: "30 days", days: 30 },
  { key: "all", label: "All time", days: null },
] as const;

// The steps a person goes through, in order. Each one's rate is measured
// against the step before it, so drop-off points stand out.
const FUNNEL: { event: string; label: string }[] = [
  { event: "analyze_view", label: "Opened the check page" },
  { event: "career_selected", label: "Picked a career" },
  { event: "file_chosen", label: "Chose a CV file" },
  { event: "check_submitted", label: "Pressed “Check my CV”" },
  { event: "check_completed", label: "Got a score" },
  { event: "certificate_clicked", label: "Clicked “Get my certificate”" },
  { event: "share_clicked", label: "Shared or downloaded it" },
];

const REASONS: Record<string, string> = {
  photo: "Photo of a CV",
  password: "Password-protected",
  too_large: "File too large",
  file_type: "File type not readable",
  no_text: "No readable text",
  damaged: "Damaged file",
  engine_down: "Engine asleep or down",
  network: "Connection dropped",
  other: "Other",
};

const CHANNELS: Record<string, string> = {
  linkedin_profile: "LinkedIn profile",
  linkedin_post: "LinkedIn post",
  whatsapp: "WhatsApp",
  facebook: "Facebook",
  x: "X",
  copy_link: "Copied link",
  native_share: "Phone share menu",
  download_pdf: "Downloaded PDF",
  download_square: "Downloaded square image",
  download_wide: "Downloaded wide image",
};

const FEATURES: Record<string, string> = {
  personalized_roadmap: "Personal roadmap",
  employer_insights: "Employer insights",
  score_increase_tips: "Tips to raise my score",
  cv_improvement: "CV improvement",
  profile_integration: "Profile integration",
  download_certificate: "Download certificate",
};

const nf = new Intl.NumberFormat("en-ZA");
const n = (v: number | null | undefined) => nf.format(v ?? 0);

function pct(part: number, whole: number): string {
  if (!whole) return "–";
  return `${Math.round((part / whole) * 100)}%`;
}

function Tile({ label, value, note }: { label: string; value: string; note?: string }) {
  return (
    <div className="rounded-2xl bg-white/60 p-4">
      <p className="text-xs font-medium text-slate">{label}</p>
      <p className="mt-1 font-display text-2xl font-semibold tabular-nums tracking-tight">{value}</p>
      {note && <p className="mt-0.5 text-xs text-slate">{note}</p>}
    </div>
  );
}

function Panel({ title, sub, children }: { title: string; sub?: string; children: React.ReactNode }) {
  return (
    <section className="glass-sheet p-5 sm:p-7">
      <h2 className="font-display text-lg font-semibold tracking-tight">{title}</h2>
      {sub && <p className="mt-0.5 text-sm text-slate">{sub}</p>}
      <div className="mt-4">{children}</div>
    </section>
  );
}

function BarList({ rows }: { rows: { label: string; value: number }[] }) {
  if (rows.length === 0) return <p className="text-sm text-slate">Nothing yet.</p>;
  const max = Math.max(...rows.map((r) => r.value), 1);
  return (
    <ul className="space-y-2.5">
      {rows.map((r) => (
        <li key={r.label}>
          <div className="flex justify-between gap-3 text-sm">
            <span className="truncate">{r.label}</span>
            <span className="tabular-nums text-slate">{n(r.value)}</span>
          </div>
          <div className="mt-1 h-2 rounded-full bg-ink/[0.06]">
            <div className="h-2 rounded-full bg-jacaranda" style={{ width: `${(r.value / max) * 100}%` }} />
          </div>
        </li>
      ))}
    </ul>
  );
}

function DailyChart({ daily }: { daily: UsageStats["daily"] }) {
  const max = Math.max(...daily.map((d) => Math.max(d.visitors, d.checks)), 1);
  const w = 100 / Math.max(daily.length, 1);
  const label = (d: string) => new Date(d).toLocaleDateString("en-ZA", { day: "numeric", month: "short" });
  return (
    <div>
      <svg viewBox="0 0 100 40" preserveAspectRatio="none" className="h-40 w-full" role="img"
        aria-label="Visitors and completed checks per day">
        {daily.map((d, i) => {
          const vh = (d.visitors / max) * 38;
          const ch = (d.checks / max) * 38;
          return (
            <g key={d.day}>
              <title>{`${label(d.day)}: ${d.visitors} visitors, ${d.checks} checks`}</title>
              <rect x={i * w + w * 0.12} y={40 - vh} width={w * 0.76} height={vh} rx={0.4} className="fill-jacaranda-light/70" />
              <rect x={i * w + w * 0.3} y={40 - ch} width={w * 0.4} height={ch} rx={0.3} className="fill-ink" />
            </g>
          );
        })}
      </svg>
      <div className="mt-2 flex justify-between text-xs text-slate">
        <span>{daily[0] ? label(daily[0].day) : ""}</span>
        <span className="flex gap-4">
          <span className="flex items-center gap-1.5"><span className="h-2.5 w-2.5 rounded-sm bg-jacaranda-light" /> Visitors</span>
          <span className="flex items-center gap-1.5"><span className="h-2.5 w-2.5 rounded-sm bg-ink" /> Checks</span>
        </span>
        <span>{daily.length ? label(daily[daily.length - 1].day) : ""}</span>
      </div>
    </div>
  );
}


export function AdminDashboard({
  stats,
  error,
  signUps,
  rangeKey,
}: {
  stats: UsageStats | null;
  error: string | null;
  signUps: number | null;
  rangeKey: string;
}) {
  const range = RANGES.find((r) => r.key === rangeKey) ?? RANGES[1];
  const step = (e: string) => stats?.steps[e] ?? { clicks: 0, people: 0 };
  const goalValue = signUps ?? 0;
  const goalPct = Math.min(100, (goalValue / GOAL) * 100);

  return (
    <div className="min-h-screen">
      <Header />
      <main className="page-top mx-auto max-w-5xl space-y-5 px-4 pb-24 sm:px-6">
        <div className="flex flex-col gap-3 px-1 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <h1 className="font-display text-3xl font-semibold tracking-tight">Founder dashboard</h1>
            <p className="mt-1 text-sm text-slate">Anonymous usage. Only you can see this page.</p>
          </div>
          <nav className="flex gap-1 rounded-full bg-white/60 p-1" aria-label="Date range">
            {RANGES.map((r) => (
              <Link
                key={r.key}
                href={`/admin?range=${r.key}`}
                aria-current={r.key === range.key ? "page" : undefined}
                className={`rounded-full px-3.5 py-1.5 text-sm font-medium ${
                  r.key === range.key ? "bg-ink text-white" : "text-slate hover:text-ink"
                }`}
              >
                {r.label}
              </Link>
            ))}
          </nav>
        </div>

        <section className="glass-sheet p-5 sm:p-7">
          <div className="flex flex-wrap items-baseline justify-between gap-2">
            <h2 className="font-display text-lg font-semibold tracking-tight">Road to {GOAL} sign-ups</h2>
            <p className="text-sm text-slate">
              {signUps === null ? "Couldn't reach Clerk" : `${n(goalValue)} of ${GOAL} · ${Math.round(goalPct)}%`}
            </p>
          </div>
          <div className="mt-3 h-3 rounded-full bg-ink/[0.07]">
            <div className="h-3 rounded-full bg-jacaranda" style={{ width: `${goalPct}%` }} />
          </div>
          <p className="mt-3 text-sm text-slate">
            Accounts created (all time). At {GOAL}, start approaching accredited course providers for the most common
            gaps. Alongside: {n(step("check_completed").people)} people got a score in this period, and{" "}
            {n(stats?.checks_all_time)} checks have been done since launch.
          </p>
        </section>

        {error && (
          <p className="rounded-2xl border border-brass/40 bg-brass/10 px-4 py-3 text-sm text-brass-dark" role="alert">
            {error}
          </p>
        )}

        {stats && (
          <>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
              <Tile label="Visitors" value={n(stats.unique_visitors)} note="unique browsers" />
              <Tile label="Picked a career" value={n(step("career_selected").people)} note={`${n(step("career_selected").clicks)} picks`} />
              <Tile label="Checks done" value={n(stats.checks_in_period)} note={`${pct(step("check_completed").people, step("analyze_view").people)} of visitors`} />
              <Tile label="Certificates" value={n(stats.certificates_in_period)} note={`${n(step("certificate_clicked").clicks)} button clicks`} />
              <Tile label="Shares & downloads" value={n(step("share_clicked").clicks)} note={`${n(step("share_clicked").people)} people`} />
            </div>

            <Panel title="Click-through, step by step" sub="Unique people at each step. The rate is against the step before, so the lowest one is your biggest drop-off.">
              <ol className="space-y-3">
                {FUNNEL.map((f, i) => {
                  const s = step(f.event);
                  const prev = i === 0 ? s.people : step(FUNNEL[i - 1].event).people;
                  const top = step(FUNNEL[0].event).people || 1;
                  return (
                    <li key={f.event} className="grid grid-cols-[1fr_auto] items-center gap-x-4 gap-y-1 sm:grid-cols-[14rem_1fr_7rem]">
                      <span className="text-sm">{f.label}</span>
                      <div className="order-3 col-span-2 h-2.5 rounded-full bg-ink/[0.06] sm:order-none sm:col-span-1">
                        <div className="h-2.5 rounded-full bg-jacaranda" style={{ width: `${Math.min(100, (s.people / top) * 100)}%` }} />
                      </div>
                      <span className="text-right text-sm tabular-nums">
                        {n(s.people)}
                        {i > 0 && <span className="ml-2 text-slate">{pct(s.people, prev)}</span>}
                      </span>
                    </li>
                  );
                })}
              </ol>
            </Panel>

            <Panel title="Per day" sub={range.days ? undefined : "Last 30 days"}>
              <DailyChart daily={stats.daily} />
            </Panel>

            <Panel
              title="By career"
              sub="What people pick, and how far they get. Checks and scores come from saved results, so they include checks made before tracking started."
            >
              {stats.per_career.length === 0 ? (
                <p className="text-sm text-slate">No careers picked yet.</p>
              ) : (
                <div className="-mx-2 overflow-x-auto">
                  <table className="w-full min-w-[640px] text-left text-sm">
                    <thead className="text-xs text-slate">
                      <tr className="border-b border-ink/[0.08]">
                        <th className="px-2 py-2 font-medium">Career</th>
                        <th className="px-2 py-2 text-right font-medium">Picked</th>
                        <th className="px-2 py-2 text-right font-medium">People</th>
                        <th className="px-2 py-2 text-right font-medium">Checks</th>
                        <th className="px-2 py-2 text-right font-medium">Pick → score</th>
                        <th className="px-2 py-2 text-right font-medium">Failed</th>
                        <th className="px-2 py-2 text-right font-medium">Avg score</th>
                        <th className="px-2 py-2 text-right font-medium">70+</th>
                        <th className="px-2 py-2 text-right font-medium">Cert clicks</th>
                        <th className="px-2 py-2 text-right font-medium">Shares</th>
                      </tr>
                    </thead>
                    <tbody className="tabular-nums">
                      {stats.per_career.slice(0, 50).map((c) => (
                        <tr key={c.career} className="border-b border-ink/[0.05] last:border-0">
                          <td className="max-w-[16rem] truncate px-2 py-2.5 font-medium" title={c.career}>{c.career}</td>
                          <td className="px-2 py-2.5 text-right">{n(c.selections)}</td>
                          <td className="px-2 py-2.5 text-right">{n(c.selected_by)}</td>
                          <td className="px-2 py-2.5 text-right">{n(c.checks)}</td>
                          <td className="px-2 py-2.5 text-right">{pct(c.completed, c.selected_by)}</td>
                          <td className="px-2 py-2.5 text-right">{c.failed ? n(c.failed) : "–"}</td>
                          <td className="px-2 py-2.5 text-right">{c.avg_score ?? "–"}</td>
                          <td className="px-2 py-2.5 text-right">{n(c.scored_70_plus)}</td>
                          <td className="px-2 py-2.5 text-right">{n(c.certificate_clicks)}</td>
                          <td className="px-2 py-2.5 text-right">{n(c.shares)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </Panel>

            <div className="grid grid-cols-1 gap-5 md:grid-cols-3">
              <Panel title="Why checks failed" sub="Reason and file type">
                <BarList
                  rows={stats.failures.map((f) => {
                    const [reason, kind] = f.reason.split(":");
                    return { label: `${REASONS[reason] ?? reason}${kind ? ` (.${kind})` : ""}`, value: f.times };
                  })}
                />
              </Panel>
              <Panel title="Where people share">
                <BarList rows={stats.shares_by_channel.map((s) => ({ label: CHANNELS[s.channel] ?? s.channel, value: s.clicks }))} />
              </Panel>
              <Panel title="Features people want">
                <BarList rows={stats.feature_interest.map((f) => ({ label: FEATURES[f.feature] ?? f.feature, value: f.votes }))} />
              </Panel>
            </div>

            <p className="px-1 text-xs text-slate">
              {stats.tracking_started
                ? `Click tracking started ${new Date(stats.tracking_started).toLocaleDateString("en-ZA", { day: "numeric", month: "long", year: "numeric" })}.`
                : "No clicks tracked yet. Numbers appear as soon as people use the site."}{" "}
              {n(stats.signed_in_checkers)} signed-in people have done a check. Updated{" "}
              {new Date(stats.generated_at).toLocaleTimeString("en-ZA", { hour: "2-digit", minute: "2-digit", timeZone: "Africa/Johannesburg" })}.
            </p>
          </>
        )}
      </main>
      <Footer />
    </div>
  );
}
