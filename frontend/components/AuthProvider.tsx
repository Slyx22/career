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

  // Get the publishable key from environment - supports both standard and custom naming
  const publishableKey = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY ||
                         process.env.CLERK1 || '';

  return <ClerkProvider publishableKey={publishableKey}>{children}</ClerkProvider>;
}
