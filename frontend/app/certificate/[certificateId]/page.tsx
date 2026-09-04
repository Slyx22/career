import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { fetchVerification } from "@/lib/serverApi";
import { PrintButton } from "@/components/PrintButton";

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

export default async function CertificatePage({
  params,
}: {
  params: { certificateId: string };
}) {
  const cert = await fetchVerification(params.certificateId);

  if (!cert.verified) {
    return (
      <div className="flex min-h-screen flex-col">
        <Header />
        <main className="flex-1">
          <section className="mx-auto max-w-xl px-6 py-24 text-center">
            <h1 className="font-display text-2xl text-ink">
              Certificate Not Found
            </h1>
          </section>
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="flex min-h-screen flex-col">
      <div className="print:hidden">
        <Header />
      </div>
      <main className="flex-1">
        <section className="mx-auto max-w-2xl px-6 py-16">
          <div
            id="certificate"
            className="border-2 border-ink px-10 py-14 text-center print:border-0"
          >
            <div className="border border-line px-8 py-10">
              <p className="font-body text-sm tracking-normal text-slate">
                Career Readiness Certificate
              </p>
              <h1 className="mt-6 font-display text-3xl text-ink">
                {cert.first_name?.toUpperCase()} {cert.surname?.toUpperCase()}
              </h1>
              <p className="mt-3 font-body text-lg text-slate">
                {cert.career?.toUpperCase()}
              </p>

              <p className="mt-10 font-body text-xs text-slate">
                Career Readiness Score
              </p>
              <p className="font-display text-4xl text-brass-dark">
                {cert.score} / 100
              </p>

              <div className="mt-10 space-y-1 font-body text-xs text-slate">
                <p>Assessment completed: {cert.issued_at ? formatDate(cert.issued_at) : ""}</p>
                <p>Certificate ID: {cert.certificate_id}</p>
                <p>Verify at: /verify/{cert.certificate_id}</p>
              </div>

              <p className="mt-8 font-body text-[11px] italic text-slate">
                This certificate confirms completion of a Career Readiness
                Assessment. It is not a professional accreditation.
              </p>
            </div>
          </div>

          <div className="mt-8 flex flex-wrap items-center justify-center gap-4 print:hidden">
            <a
              href={`/api/certificate/${cert.certificate_id}/pdf`}
              className="focus-ring rounded bg-ink px-6 py-3 font-body text-sm font-medium text-paper transition-colors hover:bg-brass-dark"
            >
              Download PDF
            </a>
            <PrintButton />
            <a
              href={`/verify/${cert.certificate_id}`}
              className="focus-ring rounded border border-line px-6 py-3 font-body text-sm text-ink hover:border-ink"
            >
              View verification page
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
