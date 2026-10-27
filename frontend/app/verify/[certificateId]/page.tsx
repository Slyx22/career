import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { fetchVerification } from "@/lib/serverApi";

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
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex-1">
        <section className="mx-auto max-w-xl px-6 py-20">
          {cert.verified ? (
            <div className="border border-line bg-panel px-8 py-10">
              <p className="font-body text-sm font-medium text-brass-dark">
                {cert.expired
                  ? "Genuine certificate — validity period has ended"
                  : "✓ Certificate Verified"}
              </p>
              <h1 className="mt-2 font-display text-2xl text-ink">
                Career Readiness Assessment
              </h1>

              <dl className="mt-8 space-y-4 font-body text-sm">
                <div>
                  <dt className="text-slate-600">Name (as entered by the holder)</dt>
                  <dd className="text-ink">
                    {cert.first_name} {cert.surname}
                  </dd>
                </div>
                <div>
                  <dt className="text-slate-600">Career</dt>
                  <dd className="text-ink">{cert.career}</dd>
                </div>
                <div>
                  <dt className="text-slate-600">Readiness Score</dt>
                  <dd className="text-ink">{cert.score} / 100</dd>
                </div>
                <div>
                  <dt className="text-slate-600">Issued</dt>
                  <dd className="text-ink">
                    {cert.issued_at ? formatDate(cert.issued_at) : ""}
                  </dd>
                </div>
                {cert.valid_until && (
                  <div>
                    <dt className="text-slate-600">Valid until</dt>
                    <dd className="text-ink">{formatDate(cert.valid_until)}</dd>
                  </div>
                )}
                <div>
                  <dt className="text-slate-600">Certificate ID</dt>
                  <dd className="text-ink">{cert.certificate_id}</dd>
                </div>
                <div>
                  <dt className="text-slate-600">Status</dt>
                  <dd className="text-ink">
                    {cert.expired ? "Expired (issued genuinely, now out of date)" : "Valid"}
                  </dd>
                </div>
                {cert.issuer && (
                  <div>
                    <dt className="text-slate-600">Issued by</dt>
                    <dd className="text-ink">
                      {cert.issuer}
                      {cert.method_version ? ` · method ${cert.method_version}` : ""}
                    </dd>
                  </div>
                )}
              </dl>

              <div className="mt-8 border-t border-line pt-6 font-body text-xs leading-relaxed text-slate-600">
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
            <div className="border border-line bg-panel px-8 py-10 text-center">
              <h1 className="font-display text-2xl text-ink">
                Certificate Not Found
              </h1>
              <p className="mt-3 font-body text-sm text-slate-600">
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
