"use client";

import Link from "next/link";
import { SignedIn, SignedOut, SignInButton, UserButton } from "@clerk/nextjs";
import { isClerkConfigured } from "@/lib/clerk";
import { UserIcon } from "@/components/Icons";

// Clerk's account menu, styled to match the glass design.
const userButtonAppearance = {
  elements: {
    avatarBox: "h-9 w-9 ring-2 ring-white/80 shadow-[0_4px_12px_-4px_rgba(48,36,110,0.45)]",
    userButtonTrigger: "rounded-full focus:shadow-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#7C6BE0]",
    userButtonPopoverCard:
      "rounded-[22px] border border-white/60 bg-white/80 backdrop-blur-2xl shadow-[0_20px_40px_-16px_rgba(48,36,110,0.45)]",
    userButtonPopoverActionButton: "rounded-xl",
  },
};

/**
 * The account control at the right of the header: a round avatar when
 * signed in, a "Sign in" pill when signed out. Always a fixed 36px-high
 * slot, so it lines up with the rest of the header.
 */
export function AccountButton() {
  if (!isClerkConfigured) {
    return (
      <span
        className="flex h-9 w-9 items-center justify-center rounded-full text-slate-light"
        title="Accounts are not switched on yet"
      >
        <UserIcon />
      </span>
    );
  }
  return (
    <div className="flex h-9 items-center">
      <SignedOut>
        <SignInButton mode="modal">
          <button className="glass btn-glass min-h-0 h-9 px-4 text-sm">Sign in</button>
        </SignInButton>
      </SignedOut>
      <SignedIn>
        <UserButton afterSignOutUrl="/" appearance={userButtonAppearance}>
          <UserButton.MenuItems>
            <UserButton.Link label="My certificates" labelIcon={<span aria-hidden>🎓</span>} href="/dashboard" />
          </UserButton.MenuItems>
        </UserButton>
      </SignedIn>
    </div>
  );
}

/** Only renders its children for signed-in users (when accounts are on). */
export function WhenSignedIn({ children }: { children: React.ReactNode }) {
  if (!isClerkConfigured) return null;
  return <SignedIn>{children}</SignedIn>;
}

/** Kept for any page still using the old name. */
export function AuthSection() {
  return <AccountButton />;
}

export function DashboardLink({ className }: { className?: string }) {
  return (
    <Link href="/dashboard" className={className}>
      My certificates
    </Link>
  );
}
