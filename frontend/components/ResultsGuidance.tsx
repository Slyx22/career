import { CvBasic, PrivacyWarning, SaRequirement } from "@/lib/types";

const card = "glass-sheet p-6 sm:p-8";
const h2 = "font-display text-xl font-semibold tracking-tight";

function Status({ ok, yes, no }: { ok: boolean; yes: string; no: string }) {
  return (
    <span
      className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${
        ok ? "bg-jacaranda/15 text-jacaranda-dark" : "bg-ink/[0.06] text-slate"
      }`}
    >
      {ok ? yes : no}
    </span>
  );
}

function ReqList({ items }: { items: SaRequirement[] }) {
  return (
    <ul className="mt-4 space-y-3">
      {items.map((r) => (
        <li key={r.key} className="rounded-2xl bg-white/55 p-3.5">
          <div className="flex flex-wrap items-center gap-2">
            <strong className="text-sm">{r.label}</strong>
            <Status ok={r.found_in_cv} yes="Mentioned in your CV" no="Not found in your CV" />
          </div>
          <p className="mt-1 text-xs leading-relaxed text-slate">{r.detail}</p>
        </li>
      ))}
    </ul>
  );
}

/** Legal requirements and usual employer asks, shown separately so an ask is never mistaken for a law. */
export function SaChecklist({ reqs }: { reqs: SaRequirement[] }) {
  const required = reqs.filter((r) => (r.kind ?? "required") === "required");
  const usual = reqs.filter((r) => r.kind === "usual");
  return (
    <>
      {required.length > 0 && (
        <section className={card}>
          <h2 className={h2}>Required in South Africa</h2>
          <p className="mt-1 text-sm text-slate">
            Registrations or licences this job needs here. They don&apos;t change your score, but if you have them,
            make sure your CV says so clearly.
          </p>
          <ReqList items={required} />
        </section>
      )}
      {usual.length > 0 && (
        <section className={card}>
          <h2 className={h2}>Employers usually ask for</h2>
          <p className="mt-1 text-sm text-slate">
            Not a legal requirement, but common in South African adverts for this job. If you have them, make them
            easy to spot on your CV.
          </p>
          <ReqList items={usual} />
        </section>
      )}
    </>
  );
}

/** Personal details found in the CV. Only the kind of detail is shown, never the value. */
export function PrivacyNotice({ warnings, advice }: { warnings: PrivacyWarning[]; advice?: string | null }) {
  if (warnings.length === 0) return null;
  return (
    <section className="rounded-[28px] border border-brass/40 bg-brass/10 p-6 sm:p-8">
      <h2 className={`${h2} text-brass-dark`}>Personal details you could remove</h2>
      <p className="mt-1 text-sm leading-relaxed text-ink">Your CV includes your:</p>
      <ul className="mt-3 flex flex-wrap gap-2">
        {warnings.map((w) => (
          <li key={w.key} className="rounded-full bg-white/70 px-3 py-1 text-sm font-medium text-brass-dark">
            {w.label}
          </li>
        ))}
      </ul>
      {advice && <p className="mt-4 text-sm leading-relaxed text-ink">{advice}</p>}
    </section>
  );
}

/** Structure checks only: we never ask for personal details. */
export function CvBasicsCard({ basics }: { basics: CvBasic[] }) {
  if (basics.length === 0) return null;
  const missing = basics.filter((b) => !b.ok);
  return (
    <section className={card}>
      <h2 className={h2}>CV basics</h2>
      <p className="mt-1 text-sm text-slate">
        {missing.length === 0
          ? "Your CV has the parts employers look for first."
          : "The parts employers look for first. Fix the ones that are missing."}
      </p>
      <ul className="mt-4 space-y-2.5">
        {basics.map((b) => (
          <li key={b.key} className="rounded-2xl bg-white/55 p-3.5">
            <div className="flex flex-wrap items-center gap-2">
              <span
                aria-hidden
                className={`flex h-5 w-5 shrink-0 items-center justify-center rounded-full text-[11px] font-semibold ${
                  b.ok ? "bg-jacaranda/15 text-jacaranda-dark" : "bg-brass/15 text-brass-dark"
                }`}
              >
                {b.ok ? "✓" : "!"}
              </span>
              <strong className="text-sm">{b.label}</strong>
              <span className="sr-only">{b.ok ? "present" : "missing"}</span>
            </div>
            {!b.ok && <p className="mt-1 pl-7 text-xs leading-relaxed text-slate">{b.fix}</p>}
          </li>
        ))}
      </ul>
    </section>
  );
}
