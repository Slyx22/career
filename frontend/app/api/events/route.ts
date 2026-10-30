import { NextRequest, NextResponse } from "next/server";
import { auth } from "@clerk/nextjs/server";
import { isClerkConfigured } from "@/lib/clerk";
import { TRACK_EVENTS } from "@/lib/track";

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL || process.env.SUPABASE_URL;
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY || process.env.SUPABASE_SERVICE_ROLE;

const ALLOWED = new Set<string>(TRACK_EVENTS);
const UUID_RE = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const SLUG_RE = /^[a-z0-9][a-z0-9-]{0,119}$/;
const DETAIL_RE = /^[a-z0-9_:.-]{1,60}$/i;

function cleanLabel(v: unknown): string | null {
  if (typeof v !== "string") return null;
  const s = v.replace(/[\u0000-\u001f]/g, " ").trim();
  return s ? s.slice(0, 160) : null;
}

/**
 * Stores one anonymous usage event (see lib/track.ts). Always answers 204
 * so a tracking problem can never show up as an error to the person.
 */
export async function POST(req: NextRequest) {
  try {
    const body = await req.json().catch(() => null);
    if (!body || typeof body.event !== "string" || !ALLOWED.has(body.event)) {
      return new NextResponse(null, { status: 204 });
    }
    if (!SUPABASE_URL || !SUPABASE_SERVICE_KEY) {
      return new NextResponse(null, { status: 204 });
    }

    let signedIn = false;
    if (isClerkConfigured) {
      try {
        const { userId } = await auth();
        signedIn = Boolean(userId);
      } catch {
        /* anonymous */
      }
    }

    const row = {
      event: body.event,
      career: typeof body.career === "string" && SLUG_RE.test(body.career) ? body.career : null,
      career_label: cleanLabel(body.careerLabel),
      detail: typeof body.detail === "string" && DETAIL_RE.test(body.detail) ? body.detail.toLowerCase() : null,
      visitor_id: typeof body.visitorId === "string" && UUID_RE.test(body.visitorId) ? body.visitorId : null,
      signed_in: signedIn,
    };

    const res = await fetch(`${SUPABASE_URL}/rest/v1/usage_events`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        apikey: SUPABASE_SERVICE_KEY,
        Authorization: `Bearer ${SUPABASE_SERVICE_KEY}`,
        Prefer: "return=minimal",
      },
      body: JSON.stringify(row),
    });
    if (!res.ok) console.error("usage event insert failed:", res.status, await res.text());
  } catch (error) {
    console.error("usage event error:", error);
  }
  return new NextResponse(null, { status: 204 });
}
