"use client";

import { SignInButton, SignUpButton } from "@clerk/nextjs";

/**
 * Shown on "My certificates" when signed out. Opens the same srmaps
 * sign-in card as the header's "Sign in" button, and comes back here.
 */
export function SignInPrompt() {
  return (
    <div className="glass-sheet p-6 text-center sm:p-8">
      <p className="font-display text-lg font-semibold">Sign in to see your certificates</p>
      <p className="mt-1 text-sm text-slate">Your certificates are saved to your free srmaps account.</p>
      <div className="mt-5 flex flex-wrap justify-center gap-3">
        <SignInButton mode="modal" forceRedirectUrl="/dashboard" signUpForceRedirectUrl="/dashboard">
          <button className="btn-primary">Sign in</button>
        </SignInButton>
        <SignUpButton mode="modal" forceRedirectUrl="/dashboard" signInForceRedirectUrl="/dashboard">
          <button className="glass btn-glass">Create a free account</button>
        </SignUpButton>
      </div>
    </div>
  );
}
