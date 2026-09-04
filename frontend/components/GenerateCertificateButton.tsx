"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

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

  async function handleClick() {
    setError(null);
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
        setError(data.error || "Could not generate your certificate.");
        setLoading(false);
        return;
      }
      router.push(`/certificate/${data.certificate_id}`);
    } catch {
      setError("Something went wrong reaching the certificate service.");
      setLoading(false);
    }
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
      {error && (
        <p className="mt-3 rounded border border-brass bg-brass/10 px-3 py-2 font-body text-sm text-brass-dark" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}
