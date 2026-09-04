import { isClerkConfigured } from "@/lib/clerk";
import { Header } from "@/components/Header";
import { Footer } from "@/components/Footer";

/**
 * This route is where "sign in to save your certificates / track
 * progress over time" (build spec section 24, and the Phase 2 account
 * features) lives. It's wired into middleware.ts as a protected route:
 * once Clerk is configured, visiting /dashboard while signed out
 * redirects to sign-in automatically - no extra code needed here.
 *
 * What's NOT built yet: actually linking a signed-in user's Clerk user
 * id to their saved analyses/certificates in Supabase. That's real
 * Phase 2 work (see README "Integrating Clerk" for the concrete next
 * steps) - this page is the wired-up entry point for it, not the
 * finished feature.
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

  return (
    <div className="min-h-screen bg-paper">
      <Header />
      <main className="mx-auto max-w-2xl px-6 py-16">
        <h1 className="font-display text-2xl text-ink">
          Welcome{user?.firstName ? `, ${user.firstName}` : ""}
        </h1>
        <p className="mt-3 font-body text-slate">
          This is the entry point for saved results and certificate history.
          Linking your saved analyses/certificates to your account is a Phase
          2 feature - the auth and route protection are wired up; the
          Supabase-side linking (see <code className="text-sm">analyses.user_id</code>{" "}
          in <code className="text-sm">supabase/migrations/</code>) is the next
          piece to build.
        </p>
      </main>
      <Footer />
    </div>
  );
}
