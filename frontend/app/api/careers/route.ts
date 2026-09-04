import { NextResponse } from "next/server";
import { getPythonApiUrl } from "@/lib/config";

export async function GET() {
  try {
    const res = await fetch(`${getPythonApiUrl()}/api/careers`, {
      cache: "no-store",
    });
    if (!res.ok) {
      return NextResponse.json(
        { error: "Could not load careers." },
        { status: 502 }
      );
    }
    const data = await res.json();
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
