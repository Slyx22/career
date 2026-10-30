// Server-only. Reads the founder dashboard numbers from Supabase.

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL || process.env.SUPABASE_URL;
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_SERVICE_ROLE;

export type StepStats = { clicks: number; people: number };

export type CareerStats = {
  career: string;
  selections: number;
  selected_by: number;
  submitted: number;
  completed: number;
  failed: number;
  certificate_clicks: number;
  shares: number;
  checks: number;
  avg_score: number | null;
  scored_70_plus: number;
};

export type UsageStats = {
  generated_at: string;
  days: number | null;
  tracking_started: string | null;
  unique_visitors: number;
  steps: Partial<Record<string, StepStats>>;
  checks_all_time: number;
  checks_in_period: number;
  signed_in_checkers: number;
  certificates_all_time: number;
  certificates_in_period: number;
  per_career: CareerStats[];
  daily: { day: string; visitors: number; selections: number; checks: number }[];
  shares_by_channel: { channel: string; clicks: number }[];
  failures: { reason: string; times: number }[];
  feature_interest: { feature: string; votes: number }[];
};

export async function fetchUsageStats(days: number | null): Promise<{ stats: UsageStats | null; error: string | null }> {
  if (!SUPABASE_URL || !SUPABASE_SERVICE_KEY) {
    return { stats: null, error: "Supabase isn't connected (SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are needed)." };
  }
  try {
    const res = await fetch(`${SUPABASE_URL}/rest/v1/rpc/admin_usage_stats`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        apikey: SUPABASE_SERVICE_KEY,
        Authorization: `Bearer ${SUPABASE_SERVICE_KEY}`,
      },
      body: JSON.stringify({ p_days: days }),
      cache: "no-store",
    });
    if (res.status === 404) {
      return { stats: null, error: "The analytics database update (migration 0008) hasn't been applied yet." };
    }
    if (!res.ok) return { stats: null, error: `Could not load analytics (${res.status}).` };
    return { stats: (await res.json()) as UsageStats, error: null };
  } catch {
    return { stats: null, error: "Could not reach the database." };
  }
}

/** Who may open /admin: emails in ADMIN_EMAILS or Clerk IDs in ADMIN_USER_IDS (comma-separated). */
export function isAdmin(userId: string, emails: string[]): boolean {
  const list = (name: string) =>
    (process.env[name] || "")
      .split(",")
      .map((s) => s.trim().toLowerCase())
      .filter(Boolean);
  const adminEmails = list("ADMIN_EMAILS");
  const adminIds = list("ADMIN_USER_IDS");
  if (adminIds.includes(userId.toLowerCase())) return true;
  return emails.some((e) => adminEmails.includes(e.toLowerCase()));
}
