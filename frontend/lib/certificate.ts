import { CertificateVerification } from "@/lib/types";
import { SITE_NAME, SITE_URL } from "@/lib/site";
import { bandFor } from "@/lib/bands";

/** Public page anyone can open to check the certificate. This is the link people share. */
export function verifyUrl(certificateId: string) {
  return `${SITE_URL}/verify/${encodeURIComponent(certificateId)}`;
}

export function formatCertDate(iso?: string | null) {
  if (!iso) return "";
  try {
    return new Date(iso).toLocaleDateString("en-ZA", { day: "numeric", month: "long", year: "numeric" });
  } catch {
    return iso;
  }
}

export function fullName(cert: CertificateVerification) {
  return `${cert.first_name ?? ""} ${cert.surname ?? ""}`.trim();
}

export function shareTitle(cert: CertificateVerification) {
  return `${fullName(cert)} - ${cert.career}: ${cert.score}/100 career readiness`;
}

export function shareText(cert: CertificateVerification) {
  return (
    `I scored ${cert.score}/100 for career readiness as a ${cert.career} on ${SITE_NAME}` +
    (bandFor(cert.score).seal ? ` (${bandFor(cert.score).label}). ` : ". ") +
    `Verify my certificate: ${verifyUrl(cert.certificate_id ?? "")}`
  );
}

/**
 * LinkedIn "Add to profile" link: opens the person's LinkedIn with the
 * Licenses & certifications form already filled in.
 */
export function linkedInAddToProfileUrl(cert: CertificateVerification) {
  const issued = cert.issued_at ? new Date(cert.issued_at) : null;
  const expires = cert.valid_until ? new Date(cert.valid_until) : null;
  const params = new URLSearchParams({
    startTask: "CERTIFICATION_NAME",
    name: `Career Readiness Certificate - ${cert.career} (${cert.score}/100${
      bandFor(cert.score).seal ? `, ${bandFor(cert.score).label}` : ""
    })`,
    organizationName: SITE_NAME,
    certUrl: verifyUrl(cert.certificate_id ?? ""),
    certId: cert.certificate_id ?? "",
  });
  if (issued) {
    params.set("issueYear", String(issued.getUTCFullYear()));
    params.set("issueMonth", String(issued.getUTCMonth() + 1));
  }
  if (expires) {
    params.set("expirationYear", String(expires.getUTCFullYear()));
    params.set("expirationMonth", String(expires.getUTCMonth() + 1));
  }
  return `https://www.linkedin.com/profile/add?${params.toString()}`;
}

export function linkedInPostUrl(certificateId: string) {
  return `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(verifyUrl(certificateId))}`;
}

export function whatsAppUrl(cert: CertificateVerification) {
  return `https://wa.me/?text=${encodeURIComponent(shareText(cert))}`;
}

export function facebookUrl(certificateId: string) {
  return `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(verifyUrl(certificateId))}`;
}

export function xUrl(cert: CertificateVerification) {
  return `https://x.com/intent/post?text=${encodeURIComponent(shareText(cert))}`;
}
