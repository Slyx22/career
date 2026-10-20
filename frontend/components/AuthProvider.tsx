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
export default function AuthProvider({ children }: { children: React.ReactNode }) {
  if (!isClerkConfigured) {
    return <>{children}</>;
  }

  // next.config.mjs already maps CLERK1 -> NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
  // at build time, so only the NEXT_PUBLIC_ var is visible here.
  const publishableKey = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY || '';

  return <ClerkProvider publishableKey={publishableKey}>{children}</ClerkProvider>;
}
