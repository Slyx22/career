import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { isClerkConfigured } from "@/lib/clerk";
import { fetchUsageStats, isAdmin } from "@/lib/adminStats";
import { AdminDashboard, RANGES } from "@/components/AdminDashboard";

// Founder-only analytics. Signed-out visitors are sent to sign-in by
// middleware.ts; signed-in people who aren't in ADMIN_EMAILS / ADMIN_USER_IDS
// get a plain 404, so the page's existence isn't revealed.
export const dynamic = "force-dynamic";
export const metadata: Metadata = { title: "Founder dashboard", robots: { index: false, follow: false } };

async function signUpCount(): Promise<number | null> {
  try {
    const { clerkClient } = await import("@clerk/nextjs/server");
    const client = await clerkClient();
    return await client.users.getCount();
  } catch {
    return null;
  }
}

export default async function AdminPage({ searchParams }: { searchParams: { range?: string } }) {
  if (!isClerkConfigured) notFound();
  const { currentUser } = await import("@clerk/nextjs/server");
  const user = await currentUser();
  const verifiedEmails = (user?.emailAddresses ?? [])
    .filter((e) => e.verification?.status === "verified")
    .map((e) => e.emailAddress);
  if (!user || !isAdmin(user.id, verifiedEmails)) notFound();

  const range = RANGES.find((r) => r.key === searchParams.range) ?? RANGES[1];
  const [{ stats, error }, signUps] = await Promise.all([fetchUsageStats(range.days), signUpCount()]);
  return <AdminDashboard stats={stats} error={error} signUps={signUps} rangeKey={range.key} />;
}
