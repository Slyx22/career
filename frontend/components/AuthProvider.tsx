"use client";

import { ClerkProvider } from "@clerk/nextjs";
import { isClerkConfigured } from "@/lib/clerk";

/**
 * Wraps children with ClerkProvider only when Clerk keys are actually
 * configured. This keeps `npm run build` / `npm run dev` working out of
 * the box before you've connected Clerk (per build spec: the core
 * analyze -> results -> certificate flow must never require an account),
 * while making the swap to "auth is live" a matter of setting two env
 * vars - no code changes.
 */

// Our own wording on the sign-in / sign-up cards, so people see our
// brand, not the auth provider's.
const localization = {
  signIn: {
    start: {
      title: "Sign in to srmaps",
      subtitle: "Welcome back! Sign in to see your certificates.",
    },
  },
  signUp: {
    start: {
      title: "Create your srmaps account",
      subtitle: "Free, and it keeps your certificates in one place.",
    },
  },
};

const appearance = {
  layout: {
    // Hides the orange "Development mode" strip on the sign-in card.
    // The proper long-term fix is Clerk's production keys (pk_live_/sk_live_),
    // see README "Integrating Clerk"; this keeps the card clean until then.
    unsafe_disableDevelopmentModeWarnings: true,
  },
  variables: {
    colorPrimary: "#141a2e",
    borderRadius: "14px",
  },
};

export default function AuthProvider({ children }: { children: React.ReactNode }) {
  if (!isClerkConfigured) {
    return <>{children}</>;
  }

  // next.config.mjs maps clerk1/CLERK1 -> NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
  // at build time, so only the NEXT_PUBLIC_ var is visible here.
  const publishableKey = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY || "";

  return (
    <ClerkProvider publishableKey={publishableKey} localization={localization} appearance={appearance}>
      {children}
    </ClerkProvider>
  );
}
