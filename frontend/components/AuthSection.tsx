"use client";

import Link from "next/link";
import { SignedIn, SignedOut, SignInButton, UserButton } from "@clerk/nextjs";
import { isClerkConfigured } from "@/lib/clerk";

/**
 * Renders real Clerk auth UI once NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY /
 * CLERK_SECRET_KEY are set. Until then it shows nothing more than a
 * quiet, disabled-looking placeholder - the point is that the core
 * product works identically either way (see build spec section 24: auth
 * must never block the CV -> score -> certificate flow).
 */
export function AuthSection() {
  if (!isClerkConfigured) {
    return (
      <span
        className="font-body text-xs text-slate-700"
        title="Sign-in will appear here once Clerk is connected (see README: Integrating Clerk)."
      >
        Sign in (coming soon)
      </span>
    );
  }

  return (
    <>
      <SignedOut>
        <SignInButton mode="modal">
          <button className="font-body text-sm text-slate hover:text-ink focus-ring rounded-sm">
            Sign in
          </button>
        </SignInButton>
      </SignedOut>
      <SignedIn>
        <Link
          href="/dashboard"
          className="font-body text-sm text-slate hover:text-ink focus-ring rounded-sm"
        >
          My dashboard
        </Link>
        <UserButton afterSignOutUrl="/" />
      </SignedIn>
    </>
  );
}
