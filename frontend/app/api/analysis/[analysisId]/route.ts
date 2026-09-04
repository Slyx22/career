import { NextRequest, NextResponse } from "next/server";
import { getPythonApiUrl } from "@/lib/config";

export async function GET(
  _req: NextRequest,
  { params }: { params: { analysisId: string } }
) {
  try {
    const res = await fetch(
      `${getPythonApiUrl()}/api/analysis/${encodeURIComponent(
        params.analysisId
      )}`,
      { cache: "no-store" }
    );
    const data = await res.json().catch(() => null);

    if (!res.ok) {
      return NextResponse.json(
        { error: data?.detail || "Analysis not found." },
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
