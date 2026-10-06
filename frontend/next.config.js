/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    // Map CLERK1 and CLERK2 to the standard Clerk environment variable names
    // This allows Vercel to use custom variable names while Clerk SDK gets what it expects
    NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: process.env.CLERK1 || process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY || '',
    CLERK_SECRET_KEY: process.env.CLERK2 || process.env.CLERK_SECRET_KEY || '',
  },
};

module.exports = nextConfig;
