import { NextResponse } from "next/server";
import { clerkMiddleware } from "@clerk/nextjs/server";
import { isClerkConfigured } from "@/lib/clerk";

/**
 * Makes the signed-in user available to pages and API routes. No page is
 * locked behind a redirect: /dashboard shows signed-out visitors our own
 * sign-in card, and the core CV -> score -> certificate flow never needs an
 * account.
 *
 * When Clerk isn't configured yet (no clerk1/clerk2 or standard Clerk env
 * vars), this middleware is a harmless no-op passthrough.
 */
const middleware = isClerkConfigured
  ? // No route redirects to Clerk's hosted sign-in page: signed-out
    // visitors to /dashboard see our own sign-in card there instead, the
    // same one the header's "Sign in" opens, so there's one sign-in look.
    clerkMiddleware()
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
