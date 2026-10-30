import Link from "next/link";
import { Suspense } from "react";
import { isClerkConfigured } from "@/lib/clerk";
import { engineFetch } from "@/lib/config";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";
import { SignInPrompt } from "@/components/SignInPrompt";

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
      <div className="min-h-screen">
        <Header />
        <main className="page-top mx-auto max-w-2xl px-4 sm:px-6">
          {/* Developers: accounts turn on when the Clerk keys are set (see README, "Integrating Clerk"). */}
          <div className="glass-sheet p-6 text-center sm:p-8">
            <h1 className="font-display text-2xl font-semibold">Sign-in isn&apos;t available right now</h1>
            <p className="mt-2 text-sm text-slate">You can still check your CV and see your results.</p>
            <Link href="/analyze" className="btn-primary mt-5">
              Check my CV
            </Link>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  const { currentUser } = await import("@clerk/nextjs/server");
  const user = await currentUser();

  return (
    <div className="min-h-screen">
      <Header />
      <main className="page-top mx-auto max-w-2xl px-4 sm:px-6">
        <h1 className="px-1 font-display text-3xl font-semibold tracking-tight">
          {user ? `Welcome${user.firstName ? `, ${user.firstName}` : ""}` : "My certificates"}
        </h1>
        <p className="mt-2 px-1 text-slate">
          {user ? "Your certificates. Open one to share it or download it." : "Check your CV, get your certificate, and find it here any time."}
        </p>

        <div className="mt-8">
          {/* The page shows at once; the list streams in when the engine
              answers, so a sleeping engine never freezes the whole page. */}
          <Suspense fallback={<CertificatesSkeleton />}>
            {user ? <CertificateList userId={user.id} /> : <SignInPrompt />}
          </Suspense>
        </div>
      </main>
      <Footer />
    </div>
  );
}

function CertificatesSkeleton() {
  return (
    <div className="glass-sheet space-y-2 p-2" aria-busy="true">
      {[0, 1].map((i) => (
        <div key={i} className="flex items-center justify-between gap-3 px-4 py-4">
          <div className="w-full space-y-2">
            <div className="skeleton h-4 w-1/2" />
            <div className="skeleton h-3 w-2/3" />
          </div>
          <div className="skeleton h-10 w-16 shrink-0 rounded-full" />
        </div>
      ))}
      <p className="px-4 pb-3 text-center text-xs text-slate" role="status">
        Loading your certificates. This can take up to a minute after a quiet spell.
      </p>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="glass-sheet p-6 text-center sm:p-8">
      <p className="font-display text-lg font-semibold">No certificates yet</p>
      <p className="mt-1 text-sm text-slate">Check your CV, then tap &ldquo;Get my certificate&rdquo; on your results.</p>
      <Link href="/analyze" className="btn-primary mt-5">
        Check my CV
      </Link>
    </div>
  );
}

async function CertificateList({ userId }: { userId: string }) {
  let certificates: Certificate[] = [];
  let loadError: string | null = null;

  try {
    const res = await engineFetch(`/api/certificates?clerk_user_id=${encodeURIComponent(userId)}`, {
      cache: "no-store",
      // A sleeping engine can take ~50s to wake; don't wait forever.
      signal: AbortSignal.timeout(55_000),
    });
    if (res.ok) {
      const data = await res.json();
      certificates = data.certificates ?? [];
    } else {
      loadError = "Could not load your certificates right now.";
    }
  } catch {
    loadError = "Our engine is taking a while to wake up. Please try again in a minute.";
  }

  if (loadError) {
    return (
      <div className="rounded-2xl border border-brass/40 bg-brass/10 px-4 py-3 text-sm text-brass-dark">
        <p>{loadError}</p>
        <Link href="/dashboard" className="mt-2 inline-block font-medium underline underline-offset-2">
          Try again
        </Link>
      </div>
    );
  }

  if (certificates.length === 0) return <EmptyState />;

  return (
    <ul className="glass-sheet divide-y divide-ink/[0.07] p-2">
      {certificates.map((cert) => (
        <li key={cert.certificate_id} className="flex items-center justify-between gap-3 px-4 py-4">
          <div>
            <p className="font-medium">{cert.career}</p>
            <p className="mt-0.5 text-xs text-slate">
              {cert.score}/100 ·{" "}
              {new Date(cert.issued_at).toLocaleDateString("en-ZA", {
                day: "numeric",
                month: "long",
                year: "numeric",
              })}{" "}
              · {cert.certificate_id}
            </p>
          </div>
          <Link
            href={`/certificate/${cert.certificate_id}`}
            className="btn-glass shrink-0 border border-white/70 bg-white/60 px-4 text-sm"
          >
            View
          </Link>
        </li>
      ))}
    </ul>
  );
}
