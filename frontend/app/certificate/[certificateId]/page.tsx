import type { Metadata } from "next";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { PrintButton } from "@/components/PrintButton";
import { ScoreRing } from "@/components/ScoreRing";
import { Seal } from "@/components/Seal";
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

export default async function CertificatePage({ params }: { params: { certificateId: string } }) {
  const cert = await fetchVerification(params.certificateId);

  if (!cert.verified) {
    return (
      <div className="min-h-screen">
        <Header />
        <main className="page-top mx-auto max-w-xl px-4">
          <section className="glass-sheet p-8 text-center">
            <h1 className="font-display text-2xl font-semibold">Certificate not found</h1>
            <p className="mt-3 text-sm text-slate">
              Please check the link, or generate your certificate again from your results.
            </p>
          </section>
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <Header />
      <main className="page-top print:pt-0">
        <section className="mx-auto max-w-3xl px-4 sm:px-6">
          <div
            id="certificate"
            className="rounded-[22px] bg-[#FBF8F1] p-3 shadow-[0_30px_60px_-28px_rgba(48,36,110,0.55)] print:rounded-none print:shadow-none sm:p-4"
          >
            <div className="rounded-[14px] border-[5px] border-brass px-6 py-8 print:rounded-none sm:px-10 sm:py-10">
              <p className="text-center text-xs font-semibold tracking-[0.3em] text-brass-dark sm:text-left">
                CERTIFICATE OF CAREER READINESS
              </p>
              <div className="mx-auto mt-3 h-[3px] w-24 bg-brass sm:mx-0" />

              <div className="mt-8 flex flex-col items-center gap-8 sm:flex-row sm:justify-between">
                <div className="text-center sm:text-left">
                  <p className="text-sm italic text-slate-600">This certifies that</p>
                  <h1 className="mt-1 font-display text-3xl font-semibold text-ink sm:text-4xl">{fullName(cert)}</h1>
                  <p className="mt-3 text-sm text-slate-600">has been assessed for career readiness as</p>
                  <p className="mt-1 font-display text-xl text-brass-dark">{cert.career}</p>
                </div>
                <div className="flex items-center gap-4">
                  <ScoreRing score={cert.score ?? 0} size={140} id="cert" />
                  <Seal score={cert.score ?? 0} size={92} />
                </div>
              </div>

              <div className="mt-10 grid grid-cols-2 gap-4 border-t border-line pt-5 text-xs text-slate-600 sm:grid-cols-4">
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

              <p className="mt-5 break-all text-xs text-slate-600">
                Verify: <span className="text-ink">{verifyUrl(cert.certificate_id ?? "")}</span>
              </p>
              <p className="mt-4 text-[10px] italic leading-relaxed text-slate-500">
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
              className="glass btn-glass"
            >
              View public verification page
            </a>
          </div>
        </section>
      </main>
      <Footer />
    </div>
  );
}
