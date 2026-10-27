import { fetchVerification } from "@/lib/serverApi";
import { IMAGE_SIZES, renderCertificateImage, renderNotFoundImage } from "@/lib/certificateImage";

export const runtime = "nodejs";
export const alt = "Career readiness certificate";
export const size = IMAGE_SIZES.wide;
export const contentType = "image/png";

// The picture that appears when the verify link is shared on LinkedIn,
// WhatsApp, Facebook or X.
export default async function Image({ params }: { params: { certificateId: string } }) {
  const cert = await fetchVerification(params.certificateId);
  return cert.verified ? renderCertificateImage(cert, "wide") : renderNotFoundImage();
}
