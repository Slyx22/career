import { NextRequest, NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL;
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

export async function POST(request: NextRequest) {
  try {
    const { analysisId, featureKey } = await request.json();

    if (!analysisId || !featureKey) {
      return NextResponse.json(
        { error: "analysisId and featureKey required" },
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
