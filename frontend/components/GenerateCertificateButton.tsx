"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { SignInButton, SignUpButton } from "@clerk/nextjs";
import { isClerkConfigured } from "@/lib/clerk";
import { track } from "@/lib/track";

export function GenerateCertificateButton({
  analysisId,
  firstName,
  surname,
  careerSlug,
  careerLabel,
}: {
  analysisId: string;
  firstName: string;
  surname: string;
  careerSlug?: string;
  careerLabel?: string;
}) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [needsSignUp, setNeedsSignUp] = useState(false);

  async function handleClick() {
    track("certificate_clicked", { career: careerSlug, careerLabel });
    setError(null);
    setNeedsSignUp(false);
    setLoading(true);
    try {
      const res = await fetch("/api/certificate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          analysis_id: analysisId,
          first_name: firstName,
          surname: surname,
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        if (res.status === 401 && data.error === "signup_required") {
          setNeedsSignUp(true);
          setLoading(false);
          return;
        }
        setError(data.error || data.message || "Could not generate your certificate.");
        setLoading(false);
        return;
      }
      router.push(`/certificate/${data.certificate_id}`);
    } catch {
      setError("Something went wrong reaching the certificate service.");
      setLoading(false);
    }
  }

  if (needsSignUp && isClerkConfigured) {
    return (
      <div>
        <p className="text-sm text-slate">
          Certificates are free, but generating one needs a free account
          (so you can find it again later on your dashboard).
        </p>
        <div className="mt-3 flex flex-wrap items-center gap-3">
          <SignUpButton mode="modal">
            <button className="btn-primary">Sign up free</button>
          </SignUpButton>
          <SignInButton mode="modal">
            <button className="glass btn-glass">I already have an account</button>
          </SignInButton>
        </div>
        <p className="mt-3 text-xs text-slate">Once you&apos;re signed in, tap &ldquo;Get my certificate&rdquo; again.</p>
        <button
          onClick={handleClick}
          disabled={loading}
          className="glass btn-glass mt-3"
        >
          {loading ? "Checking\u2026" : "Get my certificate"}
        </button>
      </div>
    );
  }

  return (
    <div>
      <button
        onClick={handleClick}
        disabled={loading}
        className="btn-primary w-full sm:w-auto"
      >
        {loading ? "Creating your certificate\u2026" : "Get my certificate"}
      </button>
      <p className="mt-2 text-xs text-slate">
        Free, and shareable on LinkedIn and WhatsApp.
        {isClerkConfigured ? " You'll need a free account so you can find it again later." : ""}
      </p>
      {error && (
        <p className="mt-3 rounded-2xl border border-brass/40 bg-brass/10 px-4 py-3 text-sm text-brass-dark" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}
