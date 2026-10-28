import type { Metadata } from "next";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { fetchVerification } from "@/lib/serverApi";
import { shareTitle, verifyUrl } from "@/lib/certificate";
import { SITE_NAME } from "@/lib/site";

// Title, description and preview picture used when this link is shared.
export async function generateMetadata({ params }: { params: { certificateId: string } }): Promise<Metadata> {
  const cert = await fetchVerification(params.certificateId);
  if (!cert.verified) return { title: `Certificate not found - ${SITE_NAME}`, robots: { index: false } };
  const title = shareTitle(cert);
  const description = cert.expired
    ? `Genuine career readiness certificate from ${SITE_NAME} (validity period ended).`
    : `Verified career readiness certificate issued by ${SITE_NAME}.`;
  return {
    title,
    description,
    openGraph: { title, description, url: verifyUrl(params.certificateId), type: "website", siteName: SITE_NAME },
    twitter: { card: "summary_large_image", title, description },
    // Found through the shared link, not by searching someone's name.
    robots: { index: false, follow: false },
  };
}

function formatDate(iso: string) {
  try {
    return new Date(iso).toLocaleDateString("en-ZA", {
      day: "numeric",
      month: "long",
      year: "numeric",
    });
  } catch {
    return iso;
  }
}

export default async function VerifyPage({
  params,
}: {
  params: { certificateId: string };
}) {
  const cert = await fetchVerification(params.certificateId);

  return (
    <div className="min-h-screen">
      <Header />
      <main className="page-top">
        <section className="mx-auto max-w-xl px-4 sm:px-6">
          {cert.verified ? (
            <div className="glass-sheet p-6 sm:p-8">
              <p className="inline-flex items-center gap-2 rounded-full bg-jacaranda/15 px-3 py-1 text-sm font-medium text-jacaranda-dark">
                {cert.expired
                  ? "Genuine certificate — validity period has ended"
                  : "✓ Certificate Verified"}
              </p>
              <h1 className="mt-3 font-display text-2xl font-semibold tracking-tight">
                Career Readiness Assessment
              </h1>

              <dl className="mt-6 grid grid-cols-1 gap-x-6 gap-y-4 text-sm sm:grid-cols-2">
                <div>
                  <dt className="text-xs text-slate">Name (as entered by the holder)</dt>
                  <dd className="mt-0.5 font-medium">
                    {cert.first_name} {cert.surname}
                  </dd>
                </div>
                <div>
                  <dt className="text-xs text-slate">Career</dt>
                  <dd className="mt-0.5 font-medium">{cert.career}</dd>
                </div>
                <div>
                  <dt className="text-xs text-slate">Readiness Score</dt>
                  <dd className="mt-0.5 font-medium">
                    {cert.score} / 100{cert.band_label ? ` \u00b7 ${cert.band_label}` : ""}
                  </dd>
                </div>
                <div>
                  <dt className="text-xs text-slate">Issued</dt>
                  <dd className="mt-0.5 font-medium">
                    {cert.issued_at ? formatDate(cert.issued_at) : ""}
                  </dd>
                </div>
                {cert.valid_until && (
                  <div>
                    <dt className="text-xs text-slate">Valid until</dt>
                    <dd className="mt-0.5 font-medium">{formatDate(cert.valid_until)}</dd>
                  </div>
                )}
                <div>
                  <dt className="text-xs text-slate">Certificate ID</dt>
                  <dd className="mt-0.5 font-medium">{cert.certificate_id}</dd>
                </div>
                <div>
                  <dt className="text-xs text-slate">Status</dt>
                  <dd className="mt-0.5 font-medium">
                    {cert.expired ? "Expired (issued genuinely, now out of date)" : "Valid"}
                  </dd>
                </div>
                {cert.issuer && (
                  <div>
                    <dt className="text-xs text-slate">Issued by</dt>
                    <dd className="mt-0.5 font-medium">
                      {cert.issuer}
                      {cert.method_version ? ` · method ${cert.method_version}` : ""}
                    </dd>
                  </div>
                )}
              </dl>

              <div className="mt-8 border-t border-ink/[0.08] pt-6 text-xs leading-relaxed text-slate">
                <p>
                  <strong className="text-ink">What this certificate means.</strong>{" "}
                  The score is an automated comparison between the skills
                  evidenced in the CV the holder uploaded and the skills that
                  matter for this occupation. It shows how well the CV matched
                  the occupation on the date issued. It is not a
                  qualification, a professional accreditation, or proof of
                  identity, and we have not checked the CV&apos;s claims.
                </p>
                <p className="mt-3">
                  Occupation skills data comes from the{" "}
                  <a
                    href="https://www.onetcenter.org/database.html"
                    className="underline hover:text-ink"
                    rel="noopener noreferrer"
                    target="_blank"
                  >
                    O*NET Database
                  </a>{" "}
                  (U.S. Department of Labor, Employment and Training
                  Administration), used under the CC BY 4.0 licence. O*NET is
                  a trademark of USDOL/ETA. We have modified the data, and
                  USDOL/ETA has not approved, endorsed, or tested this
                  product.
                </p>
              </div>
            </div>
          ) : (
            <div className="glass-sheet p-8 text-center">
              <h1 className="font-display text-2xl font-semibold">
                Certificate Not Found
              </h1>
              <p className="mt-3 text-sm text-slate">
                We couldn&apos;t find a certificate with this ID. Please
                double-check the verification link.
              </p>
            </div>
          )}
        </section>
      </main>
      <Footer />
    </div>
  );
}
