"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { SignInButton, SignUpButton } from "@clerk/nextjs";
import { isClerkConfigured } from "@/lib/clerk";

export function GenerateCertificateButton({
  analysisId,
  firstName,
  surname,
}: {
  analysisId: string;
  firstName: string;
  surname: string;
}) {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [needsSignUp, setNeedsSignUp] = useState(false);

  async function handleClick() {
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
      <div className="rounded border border-line bg-paper px-4 py-4">
        <p className="font-body text-sm text-slate-700">
          Certificates are free, but generating one needs a free account
          (so you can find it again later on your dashboard).
        </p>
        <div className="mt-3 flex flex-wrap items-center gap-3">
          <SignUpButton mode="modal">
            <button className="focus-ring rounded bg-ink px-5 py-2.5 font-body text-sm font-medium text-paper transition-colors hover:bg-brass-dark">
              Sign up free
            </button>
          </SignUpButton>
          <SignInButton mode="modal">
            <button className="focus-ring rounded border border-line px-5 py-2.5 font-body text-sm font-medium text-slate-700 transition-colors hover:border-slate">
              Already have an account? Sign in
            </button>
          </SignInButton>
        </div>
        <p className="mt-3 font-body text-xs text-slate-600">
          Once you&apos;re signed in, click &quot;Generate My Certificate&quot; again.
        </p>
        <button
          onClick={handleClick}
          disabled={loading}
          className="focus-ring mt-3 rounded bg-ink px-6 py-3 font-body text-sm font-medium text-paper transition-colors hover:bg-brass-dark disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? "Checking\u2026" : "Generate My Certificate"}
        </button>
      </div>
    );
  }

  return (
    <div>
      <button
        onClick={handleClick}
        disabled={loading}
        className="focus-ring rounded bg-ink px-6 py-3 font-body text-sm font-medium text-paper transition-colors hover:bg-brass-dark disabled:cursor-not-allowed disabled:opacity-60"
      >
        {loading ? "Generating\u2026" : "Generate My Certificate"}
      </button>
      <p className="mt-2 font-body text-xs text-slate-600">
        Certificates are completely free.
        {isClerkConfigured ? " A free account is required so you can find it again later." : ""}
      </p>
      {error && (
        <p className="mt-3 rounded border border-brass bg-brass/10 px-3 py-2 font-body text-sm text-brass-dark" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}
