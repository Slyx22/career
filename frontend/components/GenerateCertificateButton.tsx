"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { SignInButton, SignUpButton, useAuth } from "@clerk/nextjs";
import { isClerkConfigured } from "@/lib/clerk";

// Remembers "this person was about to get a certificate" across the
// sign-up step, including sign-ups that leave the page (e.g. Google).
const PENDING_KEY = "srmaps:pending-certificate";

function readPending(): string | null {
  try {
    return window.sessionStorage.getItem(PENDING_KEY);
  } catch {
    return null;
  }
}
function writePending(analysisId: string | null) {
  try {
    if (analysisId) window.sessionStorage.setItem(PENDING_KEY, analysisId);
    else window.sessionStorage.removeItem(PENDING_KEY);
  } catch {
    /* storage blocked: the manual button below still works */
  }
}

/**
 * Watches for the person finishing sign-up / sign-in and then carries on
 * creating their certificate, so they don't have to tap the button again.
 * Only mounted when Clerk is on (useAuth needs ClerkProvider).
 */
function ContinueAfterSignIn({ analysisId, onReady }: { analysisId: string; onReady: () => void }) {
  const { isLoaded, isSignedIn } = useAuth();
  const fired = useRef(false);
  useEffect(() => {
    if (!isLoaded || !isSignedIn || fired.current) return;
    if (readPending() !== analysisId) return;
    fired.current = true;
    writePending(null);
    onReady();
  }, [isLoaded, isSignedIn, analysisId, onReady]);
  return null;
}

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
  const pathname = usePathname() || "/";
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [needsSignUp, setNeedsSignUp] = useState(false);

  const handleClick = useCallback(async () => {
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
          writePending(analysisId);
          setNeedsSignUp(true);
          setLoading(false);
          return;
        }
        setError(data.error || data.message || "Could not generate your certificate.");
        setLoading(false);
        return;
      }
      writePending(null);
      router.push(`/certificate/${data.certificate_id}`);
    } catch {
      setError("Something went wrong reaching the certificate service.");
      setLoading(false);
    }
  }, [analysisId, firstName, surname, router]);

  const autoContinue = isClerkConfigured ? (
    <ContinueAfterSignIn analysisId={analysisId} onReady={handleClick} />
  ) : null;

  if (needsSignUp && isClerkConfigured) {
    return (
      <div>
        {autoContinue}
        <p className="text-sm text-slate">
          Certificates are free, but generating one needs a free account
          (so you can find it again later on your dashboard).
        </p>
        <div className="mt-3 flex flex-wrap items-center gap-3">
          <SignUpButton mode="modal" forceRedirectUrl={pathname} signInForceRedirectUrl={pathname}>
            <button className="btn-primary">Sign up free</button>
          </SignUpButton>
          <SignInButton mode="modal" forceRedirectUrl={pathname} signUpForceRedirectUrl={pathname}>
            <button className="glass btn-glass">I already have an account</button>
          </SignInButton>
        </div>
        {loading ? (
          <p className="mt-3 text-sm text-slate" role="status">Creating your certificate&hellip;</p>
        ) : (
          <p className="mt-3 text-xs text-slate">
            Your certificate will be created as soon as you&apos;re signed in.{" "}
            <button onClick={handleClick} className="underline underline-offset-2 hover:text-ink">
              Already signed in?
            </button>
          </p>
        )}
        {error && (
          <p className="mt-3 rounded-2xl border border-brass/40 bg-brass/10 px-4 py-3 text-sm text-brass-dark" role="alert">
            {error}
          </p>
        )}
      </div>
    );
  }

  return (
    <div>
      {autoContinue}
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
