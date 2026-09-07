import Link from "next/link";
import { isClerkConfigured } from "@/lib/clerk";
import { getPythonApiUrl } from "@/lib/config";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";

type Certificate = {
  certificate_id: string;
  first_name: string;
  surname: string;
  career: string;
  score: number;
  issued_at: string;
  verify_path: string;
};

/**
 * This route is where "sign in to save your certificates / track
 * progress over time" (build spec section 24, and the Phase 2 account
 * features) lives. It's wired into middleware.ts as a protected route:
 * once Clerk is configured, visiting /dashboard while signed out
 * redirects to sign-in automatically - no extra code needed here.
 */
export default async function DashboardPage() {
  if (!isClerkConfigured) {
    return (
      <div className="min-h-screen bg-paper">
        <Header />
        <main className="mx-auto max-w-2xl px-6 py-16">
          <h1 className="font-display text-2xl text-ink">Dashboard not available yet</h1>
          <p className="mt-3 font-body text-slate">
            Clerk isn&apos;t configured in this environment, so accounts aren&apos;t
            enabled. Set <code className="text-sm">NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY</code>{" "}
            and <code className="text-sm">CLERK_SECRET_KEY</code> to turn this on - see the
            README&apos;s &quot;Integrating Clerk&quot; section.
          </p>
        </main>
        <Footer />
      </div>
    );
  }

  const { currentUser } = await import("@clerk/nextjs/server");
  const user = await currentUser();

  let certificates: Certificate[] = [];
  let loadError: string | null = null;

  if (user) {
    try {
      const res = await fetch(
        `${getPythonApiUrl()}/api/certificates?clerk_user_id=${encodeURIComponent(user.id)}`,
        { cache: "no-store" }
      );
      if (res.ok) {
        const data = await res.json();
        certificates = data.certificates ?? [];
      } else {
        loadError = "Could not load your certificates right now.";
      }
    } catch {
      loadError = "The analysis engine is unavailable right now.";
    }
  }

  return (
    <div className="min-h-screen bg-paper">
      <Header />
      <main className="mx-auto max-w-2xl px-6 py-16">
        <h1 className="font-display text-2xl text-ink">
          Welcome{user?.firstName ? `, ${user.firstName}` : ""}
        </h1>
        <p className="mt-3 font-body text-slate">
          Certificates you&apos;ve generated while signed in show up here.
        </p>

        <div className="mt-8">
          {loadError && (
            <p className="rounded border border-brass bg-brass/10 px-3 py-2 font-body text-sm text-brass-dark">
              {loadError}
            </p>
          )}

          {!loadError && certificates.length === 0 && (
            <div className="rounded border border-line bg-white px-5 py-6 font-body text-sm text-slate">
              No certificates yet.{" "}
              <Link href="/analyze" className="underline hover:text-ink">
                Run an analysis
              </Link>{" "}
              to generate your first one.
            </div>
          )}

          {!loadError && certificates.length > 0 && (
            <ul className="flex flex-col gap-3">
              {certificates.map((cert) => (
                <li
                  key={cert.certificate_id}
                  className="flex items-center justify-between rounded border border-line bg-white px-5 py-4"
                >
                  <div>
                    <p className="font-body text-sm font-medium text-ink">{cert.career}</p>
                    <p className="font-body text-xs text-slate">
                      {cert.score}/100 · {new Date(cert.issued_at).toLocaleDateString("en-US", {
                        day: "numeric",
                        month: "long",
                        year: "numeric",
                      })}{" "}
                      · {cert.certificate_id}
                    </p>
                  </div>
                  <Link
                    href={`/certificate/${cert.certificate_id}`}
                    className="focus-ring rounded border border-line px-4 py-2 font-body text-xs font-medium text-ink hover:border-slate"
                  >
                    View
                  </Link>
                </li>
              ))}
            </ul>
          )}
        </div>
      </main>
      <Footer />
    </div>
  );
}
