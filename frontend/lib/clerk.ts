/**
 * Clerk is optional in Phase 1 (build spec: auth must never block the
 * core CV -> score -> certificate flow). This flag lets the rest of the
 * app render sensibly whether or not Clerk has been connected yet.
 *
 * IMPORTANT: This module is imported by client components ("use client"),
 * so only NEXT_PUBLIC_* env vars are available on the client side.
 * next.config.mjs maps clerk1/CLERK1 -> NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY at
 * build time, so by the time this runs, the standard key name is all
 * we need to check.
 *
 * The key must start with "pk_" to be a genuine Clerk publishable key —
 * this guards against empty strings or placeholder values that
 * next.config.mjs may fall through to.
 */
export const isClerkConfigured = Boolean(
  process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY &&
  process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY.length > 0 &&
  process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY.startsWith("pk_")
);
