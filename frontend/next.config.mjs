/** @type {import('next').NextConfig} */

// Vercel env vars can be named in any of these spellings (sensitive vars
// can't be renamed on Vercel, so we accept the names already in use).
const pick = (...names) => {
  for (const name of names) {
    const value = (process.env[name] || "").trim();
    if (value) return value;
  }
  return "";
};

const clerkPublishableKey = pick("NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY", "CLERK_PUBLISHABLE_KEY", "CLERK1", "clerk1");
const clerkSecretKey = pick("CLERK_SECRET_KEY", "CLERK2", "clerk2");

if (process.env.VERCEL) {
  // Shows up in the Vercel build log so it's obvious whether Clerk got its keys.
  console.log(
    `[clerk] publishable key: ${clerkPublishableKey ? (clerkPublishableKey.startsWith("pk_") ? "found" : "found but does not start with pk_") : "MISSING"}; ` +
      `secret key: ${clerkSecretKey ? (clerkSecretKey.startsWith("sk_") ? "found" : "found but does not start with sk_") : "MISSING"}`
  );
}

const nextConfig = {
  reactStrictMode: true,
  // Inlined at build time. The secret key is only referenced by Clerk's
  // server code, so it never ends up in browser JavaScript.
  env: {
    NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: clerkPublishableKey,
    CLERK_SECRET_KEY: clerkSecretKey,
    NEXT_PUBLIC_SUPABASE_URL: pick("NEXT_PUBLIC_SUPABASE_URL", "SUPABASE_URL"),
    NEXT_PUBLIC_SUPABASE_ANON_KEY: pick("NEXT_PUBLIC_SUPABASE_ANON_KEY", "SUPABASE_ANON"),
  },
};

export default nextConfig;
