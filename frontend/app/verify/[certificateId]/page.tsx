import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { fetchVerification } from "@/lib/serverApi";

function formatDate(iso: string) {
  try {
    return new Date(iso).toLocaleDateString("en-US", {
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
                &#10003; Certificate Verified
              </p>
              <h1 className="mt-2 font-display text-2xl text-ink">
                Career Readiness Assessment
              </h1>

              <dl className="mt-8 space-y-4 font-body text-sm">
                <div>
                  <dt className="text-slate-600">Name</dt>
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
                <div>
                  <dt className="text-slate-600">Certificate ID</dt>
                  <dd className="text-ink">{cert.certificate_id}</dd>
                </div>
                <div>
                  <dt className="text-slate-600">Status</dt>
                  <dd className="text-ink">Verified</dd>
                </div>
              </dl>
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
