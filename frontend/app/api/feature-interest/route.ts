import { NextRequest, NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL || process.env.SUPABASE_URL;
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_SERVICE_ROLE;

// Only accept the feature keys the survey actually offers, and analysis
// IDs shaped like the UUIDs the engine issues, so the table can't be
// filled with junk.
const ALLOWED_FEATURE_KEYS = new Set([
  "personalized_roadmap",
  "employer_insights",
  "score_increase_tips",
  "cv_improvement",
  "profile_integration",
  "download_certificate",
]);
const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export async function POST(request: NextRequest) {
  try {
    const { analysisId, featureKey } = await request.json();

    if (
      typeof analysisId !== "string" ||
      typeof featureKey !== "string" ||
      !UUID_RE.test(analysisId) ||
      !ALLOWED_FEATURE_KEYS.has(featureKey)
    ) {
      return NextResponse.json(
        { error: "A valid analysisId and featureKey are required" },
        { status: 400 }
      );
    }

    // Get user info if authenticated
    let clerkUserId: string | null = null;
    try {
      const { userId } = await auth();
      clerkUserId = userId;
    } catch {
      // Not authenticated - that's okay, we'll track anonymously
    }

    // If Supabase is configured, save the interest
    if (SUPABASE_URL && SUPABASE_SERVICE_KEY) {
      const response = await fetch(`${SUPABASE_URL}/rest/v1/feature_interest`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          apikey: SUPABASE_SERVICE_KEY,
          Authorization: `Bearer ${SUPABASE_SERVICE_KEY}`,
          Prefer: "resolution=ignore-duplicates",
        },
        body: JSON.stringify({
          analysis_id: analysisId,
          feature_key: featureKey,
          clerk_user_id: clerkUserId,
        }),
      });

      if (!response.ok) {
        console.error("Supabase insert failed:", await response.text());
      }
    }

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("Feature interest API error:", error);
    return NextResponse.json(
      { error: "Failed to save feature interest" },
      { status: 500 }
    );
  }
}
