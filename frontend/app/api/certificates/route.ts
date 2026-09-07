import { NextResponse } from "next/server";
import { getPythonApiUrl } from "@/lib/config";
import { isClerkConfigured } from "@/lib/clerk";

/**
 * Powers the /dashboard "my certificates" list. Always uses the caller's
 * own verified Clerk session id - never a client-supplied one - so one
 * signed-in user can never list another's certificates.
 */
export async function GET() {
  if (!isClerkConfigured) {
    return NextResponse.json({ certificates: [] });
  }

  const { auth } = await import("@clerk/nextjs/server");
  const { userId } = await auth();
  if (!userId) {
    return NextResponse.json({ error: "Not signed in." }, { status: 401 });
  }

  try {
    const res = await fetch(
      `${getPythonApiUrl()}/api/certificates?clerk_user_id=${encodeURIComponent(userId)}`,
      { cache: "no-store" }
    );
    const data = await res.json().catch(() => null);

    if (!res.ok) {
      return NextResponse.json(
        { error: data?.detail || "Could not load your certificates." },
        { status: res.status }
      );
    }

    return NextResponse.json(data);
  } catch {
    return NextResponse.json(
      { error: "The analysis engine is unavailable right now." },
      { status: 503 }
    );
  }
}
