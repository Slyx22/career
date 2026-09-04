/**
 * Clerk is optional in Phase 1 (build spec: auth must never block the
 * core CV -> score -> certificate flow). This flag lets the rest of the
 * app render sensibly whether or not Clerk has been connected yet.
 *
 * Set NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY and CLERK_SECRET_KEY (see
 * .env.example / README "Integrating Clerk" section) to turn auth on -
 * no other code changes are needed.
 */
export const isClerkConfigured = Boolean(
  process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY && process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY.length > 0
);
