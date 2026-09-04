import { NextRequest, NextResponse } from "next/server";
import { getPythonApiUrl } from "@/lib/config";

export const runtime = "nodejs";

export async function POST(req: NextRequest) {
  let incomingForm: FormData;
  try {
    incomingForm = await req.formData();
  } catch {
    return NextResponse.json(
      { error: "Could not read the submitted form." },
      { status: 400 }
    );
  }

  try {
    const res = await fetch(`${getPythonApiUrl()}/api/analyze`, {
      method: "POST",
      body: incomingForm,
    });

    const data = await res.json().catch(() => null);

    if (!res.ok) {
      return NextResponse.json(
        { error: data?.detail || "Analysis failed. Please try again." },
        { status: res.status }
      );
    }

    return NextResponse.json(data);
  } catch {
    return NextResponse.json(
      {
        error:
          "The analysis engine is unavailable right now. Please make sure the Python API is running and try again.",
      },
      { status: 503 }
    );
  }
}
