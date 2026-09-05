import { NextRequest, NextResponse } from "next/server";
import { getPythonApiUrl } from "@/lib/config";
import { isClerkConfigured } from "@/lib/clerk";

/**
 * Certificates are free, but require a signed-in account once Clerk is
 * connected (product decision - see README "Certificates require a free
 * account"). The CV upload -> score -> results flow stays completely
 * open; only certificate generation is gated here.
 *
 * The gate lives here, server-side, using Clerk's verified session - a
 * client can't fake being signed in by just sending a user id in the
 * request body. When Clerk isn't configured (no keys set), this route
 * behaves exactly as it always has: no gate, so local development
 * without a Clerk account keeps working.
 */
export async function POST(req: NextRequest) {
  let body: Record<string, unknown>;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json(
      { error: "Invalid certificate request." },
      { status: 400 }
    );
  }

  let clerkUserId: string | null = null;

  if (isClerkConfigured) {
    const { auth } = await import("@clerk/nextjs/server");
    const { userId } = await auth();
    if (!userId) {
      return NextResponse.json(
        {
          error: "signup_required",
          message:
            "Certificates are free, but you need a free account to generate one. Please sign up or sign in first.",
        },
        { status: 401 }
      );
    }
    clerkUserId = userId;
  }

  try {
    const res = await fetch(`${getPythonApiUrl()}/api/certificate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ...body, clerk_user_id: clerkUserId }),
    });

    const data = await res.json().catch(() => null);

    if (!res.ok) {
      return NextResponse.json(
        {
          error:
            data?.detail || "Could not generate the certificate. Please try again.",
        },
        { status: res.status }
      );
    }

    return NextResponse.json(data);
  } catch {
    return NextResponse.json(
      {
        error:
          "The analysis engine is unavailable right now. Please try again shortly.",
      },
      { status: 503 }
    );
  }
}
