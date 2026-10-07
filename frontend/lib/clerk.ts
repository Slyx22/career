/**
 * Clerk is optional in Phase 1 (build spec: auth must never block the
 * core CV -> score -> certificate flow). This flag lets the rest of the
 * app render sensibly whether or not Clerk has been connected yet.
 *
 * Supports both standard Clerk env vars and custom Vercel naming:
 * - NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY or CLERK1 (publishable key)
 * - CLERK_SECRET_KEY or CLERK2 (secret key)
 */
export const isClerkConfigured = Boolean(
  (process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY && process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY.length > 0) ||
  (process.env.CLERK1 && process.env.CLERK1.length > 0)
);
