import { NextRequest, NextResponse } from "next/server";
import { getPythonApiUrl } from "@/lib/config";

export async function GET(
  _req: NextRequest,
  { params }: { params: { certificateId: string } }
) {
  try {
    const res = await fetch(
      `${getPythonApiUrl()}/api/verify/${encodeURIComponent(
        params.certificateId
      )}`,
      { cache: "no-store" }
    );
    const data = await res.json().catch(() => null);

    if (!res.ok) {
      return NextResponse.json(
        { error: "Could not verify this certificate right now." },
        { status: res.status }
      );
    }

    return NextResponse.json(data);
  } catch {
    return NextResponse.json(
      { error: "The verification service is unavailable right now." },
      { status: 503 }
    );
  }
}
