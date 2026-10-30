"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import Link from "next/link";
import { Career, SaTitle } from "@/lib/types";
import { CareerChoice, CareerPicker } from "@/components/CareerPicker";
import { MINIMUM_AGE } from "@/lib/site";
import { failureReason, fileKind, track } from "@/lib/track";

// Extensions AND MIME types: phone file pickers (Android especially) filter
// by MIME type and grey out Word files when only extensions are listed.
// The engine works out the real type from the file's content, so a file
// with the wrong extension or none (e.g. a WhatsApp download) still works.
const ACCEPTED_FORMATS = [
  ".pdf", ".docx", ".doc", ".odt", ".rtf", ".txt",
  "application/pdf",
  "application/msword",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "application/vnd.oasis.opendocument.text",
  "application/rtf", "text/rtf", "text/plain",
].join(",");
const MAX_FILE_BYTES = 10 * 1024 * 1024;

export default function AnalyzePage() {
  const router = useRouter();
  const [careers, setCareers] = useState<Career[]>([]);
  const [firstName, setFirstName] = useState("");
  const [surname, setSurname] = useState("");
  const [saTitles, setSaTitles] = useState<SaTitle[]>([]);
  const [career, setCareer] = useState<CareerChoice | null>(null);
  const [file, setFile] = useState<File | null>(null);
  const [consent, setConsent] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    track("analyze_view");
  }, []);

  // The job title the person actually sees: the SA title they picked, or
  // the international career name.
  function careerLabel(choice: CareerChoice | null): string | null {
    if (!choice) return null;
    return choice.title || careers.find((c) => c.slug === choice.slug)?.name || choice.slug;
  }

  function chooseCareer(choice: CareerChoice | null) {
    setCareer(choice);
    if (choice) track("career_selected", { career: choice.slug, careerLabel: careerLabel(choice) });
  }

  function chooseFile(chosen: File | null) {
    setError(null);
    if (chosen && chosen.size > MAX_FILE_BYTES) {
      setFile(null);
      setError("That file is bigger than 10 MB. Please upload a smaller copy of your CV.");
      return;
    }
    setFile(chosen);
    if (chosen) track("file_chosen", { detail: fileKind(chosen.name) });
  }

  useEffect(() => {
    let cancelled = false;
    fetch("/api/careers")
      .then((r) => r.json())
      .then((data) => {
        if (cancelled) return;
        if (Array.isArray(data.careers) && data.careers.length > 0) {
          setCareers(data.careers);
          if (Array.isArray(data.sa_titles)) setSaTitles(data.sa_titles);
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
    if (!career) {
      setError("Please choose your target career from the list.");
      return;
    }
    if (!file) {
      setError("Please upload your CV as a PDF or Word file.");
      return;
    }

    if (!consent) {
      setError("Please tick the box to agree before uploading your CV.");
      return;
    }

    const formData = new FormData();
    formData.append("first_name", firstName.trim());
    formData.append("surname", surname.trim());
    formData.append("career", career.slug);
    if (career.title) formData.append("career_title", career.title);
    formData.append("file", file);
    formData.append("consent", "yes");

    const tracked = { career: career.slug, careerLabel: careerLabel(career) };
    const kind = fileKind(file.name);
    track("check_submitted", { ...tracked, detail: kind });
    setSubmitting(true);
    try {
      const res = await fetch("/api/analyze", { method: "POST", body: formData });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        track("check_failed", { ...tracked, detail: `${failureReason(res.status, data.error)}:${kind}` });
        setError(data.error || "Analysis failed. Please try again.");
        setSubmitting(false);
        return;
      }
      track("check_completed", { ...tracked, detail: kind });
      router.push(`/results/${data.analysis_id}`);
    } catch {
      track("check_failed", { ...tracked, detail: `network:${kind}` });
      setError("Something went wrong reaching the analysis engine. Please try again.");
      setSubmitting(false);
    }
  }

  return (
    <div className="min-h-screen">
      <Header />
      <main className="page-top mx-auto max-w-2xl px-4 sm:px-6">
        <h1 className="px-1 font-display text-3xl font-semibold tracking-tight sm:text-4xl">Check my CV</h1>
        <p className="mt-2 px-1 text-slate">
          Takes about a minute. Your certificate uses the name you type here, not the name in your CV.
        </p>

        <form onSubmit={handleSubmit} className="glass-sheet mt-6 space-y-6 p-5 sm:p-7" noValidate>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <label htmlFor="firstName" className="text-sm font-medium">
                First name
              </label>
              <input
                id="firstName"
                type="text"
                required
                autoComplete="given-name"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                className="glass-field mt-1.5 px-4 py-3 text-base placeholder:text-slate-light"
                placeholder="Thandi"
              />
            </div>
            <div>
              <label htmlFor="surname" className="text-sm font-medium">
                Surname
              </label>
              <input
                id="surname"
                type="text"
                required
                autoComplete="family-name"
                value={surname}
                onChange={(e) => setSurname(e.target.value)}
                className="glass-field mt-1.5 px-4 py-3 text-base placeholder:text-slate-light"
                placeholder="Mokoena"
              />
            </div>
          </div>

          <div>
            <label htmlFor="career" className="text-sm font-medium">
              The job you want
            </label>
            <CareerPicker
              id="career"
              careers={careers}
              saTitles={saTitles}
              value={career}
              onChange={chooseCareer}
              loading={careers.length === 0 && !error}
            />
            <p className="mt-1.5 text-xs text-slate">
              Search South African or international job titles, or tap the arrow to scroll the list.
            </p>
          </div>

          <div>
            <span className="text-sm font-medium" id="cv-label">
              Your CV
            </span>
            <label
              htmlFor="cv"
              className={`mt-1.5 flex cursor-pointer flex-col items-center justify-center gap-1 rounded-[20px] border-2 border-dashed px-4 py-7 text-center transition-colors focus-within:border-jacaranda focus-within:bg-white/70 ${
                file ? "border-jacaranda/60 bg-white/70" : "border-ink/15 bg-white/40 hover:border-jacaranda/50"
              }`}
              onDragOver={(e) => e.preventDefault()}
              onDrop={(e) => {
                e.preventDefault();
                const dropped = e.dataTransfer.files?.[0];
                if (dropped) chooseFile(dropped);
              }}
            >
              <span className="font-medium">{file ? file.name : "Choose a PDF or Word file"}</span>
              <span className="text-xs text-slate">
                {file ? "Tap to choose a different file" : "Word, PDF, OpenDocument, RTF or text · up to 10 MB"}
              </span>
              <input
                id="cv"
                type="file"
                required
                aria-labelledby="cv-label"
                accept={ACCEPTED_FORMATS}
                onChange={(e) => chooseFile(e.target.files?.[0] ?? null)}
                className="sr-only"
              />
            </label>
          </div>

          <div className="flex items-start gap-3 rounded-2xl bg-white/50 p-4">
            <input
              id="consent"
              type="checkbox"
              checked={consent}
              onChange={(e) => setConsent(e.target.checked)}
              className="focus-ring mt-0.5 h-5 w-5 shrink-0 rounded accent-jacaranda-dark"
            />
            <label htmlFor="consent" className="text-sm leading-relaxed text-slate">
              I agree to the{" "}
              <Link href="/terms" target="_blank" className="font-medium text-ink underline underline-offset-2">
                Terms
              </Link>{" "}
              and{" "}
              <Link href="/privacy" target="_blank" className="font-medium text-ink underline underline-offset-2">
                Privacy Policy
              </Link>
              , and consent to my CV being processed to calculate my score. My CV file is not stored. I am{" "}
              {MINIMUM_AGE} or older, or have a parent or guardian&apos;s permission, and this is my own CV or I have
              permission to upload it.
            </label>
          </div>

          {error && (
            <p className="rounded-2xl border border-brass/40 bg-brass/10 px-4 py-3 text-sm text-brass-dark" role="alert">
              {error}
            </p>
          )}

          <button type="submit" disabled={submitting || !consent} className="btn-primary w-full">
            {submitting ? "Checking your CV…" : "Check my CV"}
          </button>
          {submitting && (
            <p className="text-center text-xs text-slate" role="status">
              The first check after a quiet spell can take up to a minute while our engine wakes up.
            </p>
          )}
        </form>
      </main>
      <Footer />
    </div>
  );
}
