import { NextRequest, NextResponse } from "next/server";
import { fetchVerification } from "@/lib/serverApi";
import { ImageShape, renderCertificateImage } from "@/lib/certificateImage";

export const runtime = "nodejs";

// Downloadable certificate image: ?shape=wide (1200x630) or square (1080x1080).
export async function GET(req: NextRequest, { params }: { params: { certificateId: string } }) {
  const cert = await fetchVerification(params.certificateId);
  if (!cert.verified) {
    return NextResponse.json({ error: "Certificate not found." }, { status: 404 });
  }
  const shape: ImageShape = req.nextUrl.searchParams.get("shape") === "square" ? "square" : "wide";
  const image = renderCertificateImage(cert, shape);
  const body = await image.arrayBuffer();
  return new NextResponse(body, {
    headers: {
      "Content-Type": "image/png",
      "Content-Disposition": `attachment; filename="career-readiness-${params.certificateId}-${shape}.png"`,
      "Cache-Control": "public, max-age=3600",
    },
  });
}
