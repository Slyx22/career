"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import Link from "next/link";
import { Career } from "@/lib/types";
import { MINIMUM_AGE } from "@/lib/site";

const ACCEPTED_FORMATS = ".pdf,.docx";

export default function AnalyzePage() {
  const router = useRouter();
  const [careers, setCareers] = useState<Career[]>([]);
  const [firstName, setFirstName] = useState("");
  const [surname, setSurname] = useState("");
  const [career, setCareer] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [consent, setConsent] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetch("/api/careers")
      .then((r) => r.json())
      .then((data) => {
        if (cancelled) return;
        if (Array.isArray(data.careers) && data.careers.length > 0) {
          setCareers(data.careers);
          setCareer((prev) => prev || data.careers[0].slug);
        } else {
          setError("No careers are available.");
        }
      })
      .catch(() => {
        if (cancelled) return;
        setError("Could not load career list.");
      });
    return () => { cancelled = true; };
  }, []);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    if (!firstName.trim()) {
      setError("Please enter your first name.");
      return;
    }
    if (!surname.trim()) {
      setError("Please enter your surname.");
      return;
    }
    if (!file) {
      setError("Please upload your CV as a PDF or DOCX file.");
      return;
    }

    if (!consent) {
      setError("Please tick the box to agree before uploading your CV.");
      return;
    }

    const formData = new FormData();
    formData.append("first_name", firstName.trim());
    formData.append("surname", surname.trim());
    formData.append("career", career);
    formData.append("file", file);
    formData.append("consent", "yes");

    setSubmitting(true);
    try {
      const res = await fetch("/api/analyze", { method: "POST", body: formData });
      const data = await res.json();
      if (!res.ok) {
        setError(data.error || "Analysis failed. Please try again.");
        setSubmitting(false);
        return;
      }
      router.push(`/results/${data.analysis_id}`);
    } catch {
      setError("Something went wrong reaching the analysis engine. Please try again.");
      setSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen flex-col bg-white">
      <Header />
      <main className="flex-1">
        <section className="mx-auto max-w-5xl px-6 py-16">
          <h1 className="font-display text-3xl text-ink">
            Tell us about you
          </h1>
          <p className="mt-3 font-body text-sm text-slate-700">
            We use the name you enter here on your certificate &mdash; not
            whatever name appears inside your CV.
          </p>

          <form onSubmit={handleSubmit} className="mt-10 space-y-6" noValidate>
            <div className="grid grid-cols-2 gap-8 justify-between">
              <div>
                <label htmlFor="firstName" className="font-body text-sm text-ink">
                  First name *
                </label>
                <input
                  id="firstName"
                  type="text"
                  required
                  value={firstName}
                  onChange={(e) => setFirstName(e.target.value)}
                  className="focus-ring mt-1.5 w-full rounded border border-line bg-white px-3 py-2 font-body text-sm text-ink shadow-sm placeholder:text-slate-400"
                  placeholder="John"
                />
              </div>
              <div>
                <label htmlFor="surname" className="font-body text-sm text-ink">
                  Surname *
                </label>
                <input
                  id="surname"
                  type="text"
                  required
                  value={surname}
                  onChange={(e) => setSurname(e.target.value)}
                  className="focus-ring mt-1.5 w-full rounded border border-line bg-white px-3 py-2 font-body text-sm text-ink shadow-sm placeholder:text-slate-400"
                  placeholder="Smith"
                />
              </div>
            </div>

            <style>{`select option{background:#ffffff!important;color:#141A2E!important;}`}</style>
            <div>
              <label htmlFor="career" className="font-body text-sm text-ink">
                Target career *
              </label>
              <select
                id="career"
                value={career}
                onChange={(e) => setCareer(e.target.value)}
                className="focus-ring mt-1.5 w-full rounded-xl border border-line bg-white px-4 py-3 font-body text-sm text-ink shadow-sm appearance-none cursor-pointer transition hover:border-brass"
                disabled={careers.length === 0}
              >
                {careers.length > 0 ? (
                  careers.map((c) => (
                    <option key={c.slug} value={c.slug} style={{backgroundColor:"#ffffff",color:"#141A2E"}}>{c.name}</option>
                  ))
                ) : (
                  <option value="">Loading careers…</option>
                )}
              </select>
              <p className="mt-1.5 font-body text-xs text-slate-500">
                More careers will be added over time.
              </p>
            </div>

            <div>
              <label htmlFor="cv" className="font-body text-sm text-ink">
                Upload CV *
              </label>
              <input
                id="cv"
                type="file"
                required
                accept={ACCEPTED_FORMATS}
                onChange={(e) => setFile(e.target.files?.[0] ?? null)}
                className="focus-ring mt-1.5 w-full rounded border border-line bg-white px-3 py-2 font-body text-sm text-ink shadow-sm file:mr-3 file:rounded file:border-0 file:bg-ink file:px-3 file:py-1.5 file:font-body file:text-xs file:text-paper"
              />
              <p className="mt-1.5 font-body text-xs text-slate-500">
                Accepted formats: PDF, DOCX. Max 10MB.
              </p>
            </div>

            <div className="flex items-start gap-3">
              <input
                id="consent"
                type="checkbox"
                checked={consent}
                onChange={(e) => setConsent(e.target.checked)}
                className="focus-ring mt-0.5 h-4 w-4 shrink-0 rounded border-line accent-ink"
              />
              <label htmlFor="consent" className="font-body text-xs leading-relaxed text-slate-700">
                I agree to the{" "}
                <Link href="/terms" target="_blank" className="underline hover:text-ink">
                  Terms of Service
                </Link>{" "}
                and{" "}
                <Link href="/privacy" target="_blank" className="underline hover:text-ink">
                  Privacy Policy
                </Link>
                , and consent to my CV being processed to calculate my score. My CV
                file is not stored. I am {MINIMUM_AGE} or older, or have a parent or
                guardian&apos;s permission, and this is my own CV or I have permission
                to upload it.
              </label>
            </div>

            {error && (
              <p className="rounded border border-brass bg-brass/20 px-3 py-2 font-body text-sm text-brass" role="alert">
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={submitting || !consent}
              className="focus-ring w-full rounded bg-ink px-6 py-3 font-body text-sm font-medium text-paper transition-colors hover:bg-brass-dark disabled:cursor-not-allowed disabled:opacity-60"
            >
              {submitting ? "Analyzing your CV…" : "Analyze"}
            </button>
          </form>
        </section>
      </main>
      <Footer />
    </div>
  );
}