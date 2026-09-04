import { NextResponse } from "next/server";
import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";
import { isClerkConfigured } from "@/lib/clerk";

/**
 * Route protection is intentionally narrow: only /dashboard (the
 * optional "save your results" area, see build spec section 24) sits
 * behind auth. Everything else - landing, /analyze, /results,
 * /certificate, /verify - stays public, because the core CV -> score ->
 * certificate flow must never require an account.
 *
 * When Clerk isn't configured yet (no NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY /
 * CLERK_SECRET_KEY), this middleware is a harmless no-op passthrough, so
 * the app runs fine before you've connected Clerk. Once you set those two
 * env vars (see README "Integrating Clerk"), /dashboard becomes
 * auth-protected automatically - no code changes needed.
 */

const isProtectedRoute = createRouteMatcher(["/dashboard(.*)"]);

const middleware = isClerkConfigured
  ? clerkMiddleware(async (auth, req) => {
      if (isProtectedRoute(req)) {
        await auth.protect();
      }
    })
  : function noopMiddleware() {
      return NextResponse.next();
    };

export default middleware;

export const config = {
  matcher: [
    // Skip static files and Next internals; run on everything else and API routes.
    "/((?!_next|.*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)",
    "/(api|trpc)(.*)",
  ],
};
