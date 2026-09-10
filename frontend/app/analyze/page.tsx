"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { Career } from "@/lib/types";

const ACCEPTED_FORMATS = ".pdf,.docx";

export default function AnalyzePage() {
  const router = useRouter();
  const [careers, setCareers] = useState<Career[]>([]);
  const [firstName, setFirstName] = useState("");
  const [surname, setSurname] = useState("");
  const [career, setCareer] = useState("ml-engineer");
  const [file, setFile] = useState<File | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/careers")
      .then((r) => r.json())
      .then((data) => {
        if (Array.isArray(data.careers) && data.careers.length > 0) {
          setCareers(data.careers);
          setCareer(data.careers[0].slug);
        }
      })
      .catch(() => {
        // Non-fatal: the form still works with the default "ml-engineer" slug.
      });
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

    const formData = new FormData();
    formData.append("first_name", firstName.trim());
    formData.append("surname", surname.trim());
    formData.append("career", career);
    formData.append("file", file);

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
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1">
        <section className="mx-auto max-w-xl px-6 py-16">
          <h1 className="font-display text-3xl text-ink">
            Tell us about you
          </h1>
          <p className="mt-3 font-body text-sm text-slate">
            We use the name you enter here on your certificate &mdash; not
            whatever name appears inside your CV.
          </p>

          <form onSubmit={handleSubmit} className="mt-10 space-y-6" noValidate>
            <div className="grid grid-cols-2 gap-4">
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
                  className="focus-ring mt-1.5 w-full rounded border border-line bg-panel px-3 py-2 font-body text-sm text-ink"
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
                  className="focus-ring mt-1.5 w-full rounded border border-line bg-panel px-3 py-2 font-body text-sm text-ink"
                  placeholder="Smith"
                />
              </div>
            </div>

            <div>
              <label htmlFor="career" className="font-body text-sm text-ink">
                Target career *
              </label>
              <select
                id="career"
                value={career}
                onChange={(e) => setCareer(e.target.value)}
                className="focus-ring mt-1.5 w-full rounded border border-line bg-panel px-3 py-2 font-body text-sm text-ink max-h-60 overflow-y-auto"
              >
                {(careers.length > 0
                  ? careers
                  : [{ slug: "ml-engineer", name: "ML Engineer", description: "" }]
                ).map((c) => (
                  <option key={c.slug} value={c.slug}>
                    {c.name}
                  </option>
                ))}
              </select>
              <p className="mt-1.5 font-body text-xs text-slate">
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
                className="focus-ring mt-1.5 w-full rounded border border-line bg-panel px-3 py-2 font-body text-sm text-ink file:mr-3 file:rounded file:border-0 file:bg-ink file:px-3 file:py-1.5 file:font-body file:text-xs file:text-paper"
              />
              <p className="mt-1.5 font-body text-xs text-slate">
                Accepted formats: PDF, DOCX. Max 10MB.
              </p>
            </div>

            {error && (
              <p className="rounded border border-brass bg-brass/10 px-3 py-2 font-body text-sm text-brass-dark" role="alert">
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={submitting}
              className="focus-ring w-full rounded bg-ink px-6 py-3 font-body text-sm font-medium text-paper transition-colors hover:bg-brass-dark disabled:cursor-not-allowed disabled:opacity-60"
            >
              {submitting ? "Analyzing your CV\u2026" : "Analyze"}
            </button>
          </form>
        </section>
      </main>
      <Footer />
    </div>
  );
}
