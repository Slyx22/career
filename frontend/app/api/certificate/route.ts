import { NextRequest, NextResponse } from "next/server";
import { getPythonApiUrl } from "@/lib/config";

export async function POST(req: NextRequest) {
  let body: unknown;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json(
      { error: "Invalid certificate request." },
      { status: 400 }
    );
  }

  try {
    const res = await fetch(`${getPythonApiUrl()}/api/certificate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
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
