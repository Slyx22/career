import { NextRequest, NextResponse } from "next/server";
import { getPythonApiUrl } from "@/lib/config";

export async function GET(
  _req: NextRequest,
  { params }: { params: { certificateId: string } }
) {
  try {
    const res = await fetch(
      `${getPythonApiUrl()}/api/certificate/${encodeURIComponent(
        params.certificateId
      )}/pdf`,
      { cache: "no-store" }
    );

    if (!res.ok) {
      return NextResponse.json(
        { error: "Certificate not found." },
        { status: res.status }
      );
    }

    const pdfBuffer = await res.arrayBuffer();
    return new NextResponse(pdfBuffer, {
      status: 200,
      headers: {
        "Content-Type": "application/pdf",
        "Content-Disposition": `attachment; filename="${params.certificateId}.pdf"`,
      },
    });
  } catch {
    return NextResponse.json(
      { error: "The certificate service is unavailable right now." },
      { status: 503 }
    );
  }
}
