import type { Metadata } from "next";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { PrintButton } from "@/components/PrintButton";
import { ShareCertificate } from "@/components/ShareCertificate";
import { fetchVerification } from "@/lib/serverApi";
import { formatCertDate, fullName, shareTitle, verifyUrl } from "@/lib/certificate";
import { SITE_NAME } from "@/lib/site";

export async function generateMetadata({ params }: { params: { certificateId: string } }): Promise<Metadata> {
  const cert = await fetchVerification(params.certificateId);
  if (!cert.verified) return { title: `Certificate not found - ${SITE_NAME}`, robots: { index: false } };
  const title = shareTitle(cert);
  const description = `Verified career readiness certificate issued by ${SITE_NAME}. Check it at ${verifyUrl(params.certificateId)}`;
  return {
    title,
    description,
    alternates: { canonical: verifyUrl(params.certificateId) },
    openGraph: { title, description, url: verifyUrl(params.certificateId), type: "website", siteName: SITE_NAME },
    twitter: { card: "summary_large_image", title, description },
    // Found through the shared link, not by searching someone's name.
    robots: { index: false, follow: false },
  };
}

function ScoreRing({ score }: { score: number }) {
  const r = 52;
  const c = 2 * Math.PI * r;
  const filled = (Math.max(0, Math.min(100, score)) / 100) * c;
  return (
    <div className="relative h-36 w-36 shrink-0">
      <svg viewBox="0 0 120 120" className="h-full w-full -rotate-90" aria-hidden="true">
        <circle cx="60" cy="60" r={r} fill="none" stroke="#E8DFC9" strokeWidth="10" />
        <circle
          cx="60"
          cy="60"
          r={r}
          fill="none"
          stroke="#B8801F"
          strokeWidth="10"
          strokeLinecap="round"
          strokeDasharray={`${filled} ${c}`}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="font-display text-4xl font-semibold text-ink">{score}</span>
        <span className="font-body text-[11px] text-slate-600">out of 100</span>
      </div>
    </div>
  );
}

export default async function CertificatePage({ params }: { params: { certificateId: string } }) {
  const cert = await fetchVerification(params.certificateId);

  if (!cert.verified) {
    return (
      <div className="flex min-h-screen flex-col">
        <Header />
        <main className="flex-1">
          <section className="mx-auto max-w-xl px-6 py-24 text-center">
            <h1 className="font-display text-2xl text-ink">Certificate Not Found</h1>
            <p className="mt-3 font-body text-sm text-slate-600">
              Please check the link, or generate your certificate again from your results.
            </p>
          </section>
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col bg-paper">
      <div className="print:hidden">
        <Header />
      </div>
      <main className="flex-1">
        <section className="mx-auto max-w-3xl px-4 py-12 sm:px-6">
          <div id="certificate" className="bg-[#FBF8F1] p-3 shadow-sm print:shadow-none sm:p-4">
            <div className="border-[5px] border-brass px-6 py-8 sm:px-10 sm:py-10">
              <p className="text-center font-body text-xs font-semibold tracking-[0.3em] text-brass-dark sm:text-left">
                CERTIFICATE OF CAREER READINESS
              </p>
              <div className="mx-auto mt-3 h-[3px] w-24 bg-brass sm:mx-0" />

              <div className="mt-8 flex flex-col items-center gap-8 sm:flex-row sm:justify-between">
                <div className="text-center sm:text-left">
                  <p className="font-body text-sm italic text-slate-600">This certifies that</p>
                  <h1 className="mt-1 font-display text-3xl font-semibold text-ink sm:text-4xl">{fullName(cert)}</h1>
                  <p className="mt-3 font-body text-sm text-slate-600">has been assessed for career readiness as</p>
                  <p className="mt-1 font-display text-xl text-brass-dark">{cert.career}</p>
                </div>
                <ScoreRing score={cert.score ?? 0} />
              </div>

              <div className="mt-10 grid grid-cols-2 gap-4 border-t border-line pt-5 font-body text-xs text-slate-600 sm:grid-cols-4">
                <div>
                  <p className="text-[10px] uppercase tracking-wide">Issued</p>
                  <p className="text-ink">{formatCertDate(cert.issued_at)}</p>
                </div>
                <div>
                  <p className="text-[10px] uppercase tracking-wide">Valid until</p>
                  <p className="text-ink">{formatCertDate(cert.valid_until)}</p>
                </div>
                <div>
                  <p className="text-[10px] uppercase tracking-wide">Certificate ID</p>
                  <p className="text-ink">{cert.certificate_id}</p>
                </div>
                <div>
                  <p className="text-[10px] uppercase tracking-wide">Status</p>
                  <p className="text-ink">{cert.expired ? "Expired" : "✓ Verified"}</p>
                </div>
              </div>

              <p className="mt-5 break-all font-body text-xs text-slate-600">
                Verify: <span className="text-ink">{verifyUrl(cert.certificate_id ?? "")}</span>
              </p>
              <p className="mt-4 font-body text-[10px] italic leading-relaxed text-slate-500">
                Issued by {cert.issuer ?? SITE_NAME}
                {cert.method_version ? ` · method ${cert.method_version}` : ""}. Automated skills assessment of the CV
                supplied by the holder; name as entered by the holder. Not a qualification or professional
                accreditation. Skills data: O*NET (USDOL/ETA), CC BY 4.0.
              </p>
            </div>
          </div>

          <div className="mt-8 print:hidden">
            <ShareCertificate cert={cert} />
          </div>

          <div className="mt-4 flex flex-wrap justify-center gap-3 print:hidden">
            <PrintButton />
            <a
              href={`/verify/${cert.certificate_id}`}
              className="focus-ring rounded border border-line px-6 py-3 font-body text-sm text-ink hover:border-ink"
            >
              View public verification page
            </a>
          </div>
        </section>
      </main>
      <div className="print:hidden">
        <Footer />
      </div>
    </div>
  );
}
