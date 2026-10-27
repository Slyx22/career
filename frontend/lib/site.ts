// Public, non-secret details used on the legal pages and footer.
// No personal names here on purpose: the service is presented under its
// trading name. Set NEXT_PUBLIC_CONTACT_EMAIL in Vercel to a mailbox you
// check (a free Gmail address that doesn't contain your name works).

export const SITE_NAME = "Career Readiness Analyzer";
export const SITE_URL = "https://srmaps.co.za";

export const CONTACT_EMAIL = process.env.NEXT_PUBLIC_CONTACT_EMAIL || "";

// Update this date whenever the Privacy Policy or Terms change.
export const LEGAL_LAST_UPDATED = "28 October 2026";

// Minimum age to use the service without a parent or guardian's consent.
export const MINIMUM_AGE = 18;
