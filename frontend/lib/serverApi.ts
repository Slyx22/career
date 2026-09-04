// Intended for use only from Server Components / Route Handlers.
// Calls the Python engine directly using PYTHON_API_URL (never exposed to
// the browser).
import { getPythonApiUrl } from "@/lib/config";
import { AnalysisResult, CertificateVerification } from "@/lib/types";

export async function fetchAnalysis(analysisId: string): Promise<AnalysisResult | null> {
  try {
    const res = await fetch(`${getPythonApiUrl()}/api/analysis/${encodeURIComponent(analysisId)}`, {
      cache: "no-store",
    });
    if (!res.ok) return null;
    return (await res.json()) as AnalysisResult;
  } catch {
    return null;
  }
}

export async function fetchVerification(certificateId: string): Promise<CertificateVerification> {
  try {
    const res = await fetch(`${getPythonApiUrl()}/api/verify/${encodeURIComponent(certificateId)}`, {
      cache: "no-store",
    });
    if (!res.ok) return { verified: false };
    return (await res.json()) as CertificateVerification;
  } catch {
    return { verified: false };
  }
}
