from __future__ import annotations

import io
import os
import secrets
import string
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from app.db.interface import Repository
from app.models.schemas import CertificateResponse, CertificateVerifyResponse

_ID_ALPHABET = string.ascii_uppercase + string.digits

# Shown on certificates and the verify page. Keep these generic: no
# personal names. Bump METHOD_VERSION whenever the scoring method or the
# career data changes, so old and new certificates can be told apart.
ISSUER_NAME = os.environ.get("CERTIFICATE_ISSUER_NAME", "Career Readiness Analyzer")
METHOD_VERSION = "2.0"
CERTIFICATE_VALID_DAYS = 365


def certificate_valid_until(issued: datetime) -> datetime:
    return issued + timedelta(days=CERTIFICATE_VALID_DAYS)


def _format_date(dt: datetime) -> str:
    return f"{dt.day} {dt.strftime('%B %Y')}"


class CertificateError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _generate_certificate_id() -> str:
    suffix = "".join(secrets.choice(_ID_ALPHABET) for _ in range(8))
    return f"CR-{suffix}"


def _account_required_for_certificates() -> bool:
    """
    Certificates are free but require a signed-in account (per product
    decision - see README "Certificates require a free account"). The
    primary enforcement lives in the Next.js layer (frontend/app/api/
    certificate/route.ts), which knows the caller's real Clerk session.
    This is a defense-in-depth secondary check: if this env var is set,
    the Python engine will also refuse to issue a certificate with no
    clerk_user_id, even if something bypassed the Next.js layer.
    Defaults to off so local development without Clerk configured keeps
    working exactly as before.
    """
    return os.environ.get("REQUIRE_ACCOUNT_FOR_CERTIFICATE", "false").lower() == "true"


def create_certificate(
    *, store: Repository, analysis_id: str, first_name: str, surname: str, clerk_user_id: Optional[str] = None
) -> CertificateResponse:
    analysis = store.get_analysis(analysis_id)
    if not analysis:
        raise CertificateError("Analysis not found. Please run an analysis first.", status_code=404)

    first_name = (first_name or "").strip()
    surname = (surname or "").strip()
    if not first_name or not surname:
        raise CertificateError("First name and surname are required to generate a certificate.")

    if _account_required_for_certificates() and not clerk_user_id:
        raise CertificateError(
            "A free account is required to generate a certificate. Please sign up or sign in first.",
            status_code=401,
        )

    career = analysis["payload"].get("career_name") or analysis["career"]
    score = analysis["score"]

    if score is None or career is None:
        raise CertificateError("Analysis is incomplete; cannot generate a certificate.")

    certificate_id = _generate_certificate_id()
    # Extremely unlikely, but guard against a collision.
    while store.get_certificate(certificate_id):
        certificate_id = _generate_certificate_id()

    issued_at = datetime.now(timezone.utc).isoformat()

    store.save_certificate(
        {
            "certificate_id": certificate_id,
            "analysis_id": analysis_id,
            "first_name": first_name,
            "surname": surname,
            "career": career,
            "score": score,
            "clerk_user_id": clerk_user_id,
            "issued_at": issued_at,
        }
    )

    verify_base = os.environ.get("PUBLIC_VERIFY_BASE_PATH", "/verify")

    return CertificateResponse(
        certificate_id=certificate_id,
        first_name=first_name,
        surname=surname,
        career=career,
        score=score,
        issued_at=issued_at,
        verify_path=f"{verify_base}/{certificate_id}",
    )


def verify_certificate(*, store: Repository, certificate_id: str) -> CertificateVerifyResponse:
    cert = store.get_certificate(certificate_id)
    if not cert:
        return CertificateVerifyResponse(verified=False)

    issued_dt = datetime.fromisoformat(cert["issued_at"])
    if issued_dt.tzinfo is None:
        issued_dt = issued_dt.replace(tzinfo=timezone.utc)
    valid_until = certificate_valid_until(issued_dt)

    return CertificateVerifyResponse(
        verified=True,
        valid_until=valid_until.isoformat(),
        expired=datetime.now(timezone.utc) > valid_until,
        issuer=ISSUER_NAME,
        method_version=METHOD_VERSION,
        certificate_id=cert["certificate_id"],
        first_name=cert["first_name"],
        surname=cert["surname"],
        career=cert["career"],
        score=cert["score"],
        issued_at=cert["issued_at"],
    )


def list_certificates_for_user(*, store: Repository, clerk_user_id: str) -> List[CertificateResponse]:
    verify_base = os.environ.get("PUBLIC_VERIFY_BASE_PATH", "/verify")
    certs = store.list_certificates_for_user(clerk_user_id)
    return [
        CertificateResponse(
            certificate_id=c["certificate_id"],
            first_name=c["first_name"],
            surname=c["surname"],
            career=c["career"],
            score=c["score"],
            issued_at=c["issued_at"],
            verify_path=f"{verify_base}/{c['certificate_id']}",
        )
        for c in certs
    ]


def render_certificate_pdf(*, store: Repository, certificate_id: str) -> Optional[bytes]:
    cert = store.get_certificate(certificate_id)
    if not cert:
        return None

    buffer = io.BytesIO()
    page_size = landscape(A4)
    c = canvas.Canvas(buffer, pagesize=page_size)
    width, height = page_size

    # Elegant border with gradient feel (double border)
    c.setStrokeColor(colors.HexColor("#B8801F"))  # Brass color
    c.setLineWidth(4)
    c.rect(12 * mm, 12 * mm, width - 24 * mm, height - 24 * mm)

    c.setStrokeColor(colors.HexColor("#E8D4A7"))  # Light brass
    c.setLineWidth(1)
    c.rect(16 * mm, 16 * mm, width - 32 * mm, height - 32 * mm)

    center_x = width / 2

    # Header with decorative line
    c.setFont("Helvetica", 11)
    c.setFillColor(colors.HexColor("#B8801F"))
    c.drawCentredString(center_x, height - 35 * mm, "CERTIFICATE OF CAREER READINESS")

    # Decorative line under header
    c.setStrokeColor(colors.HexColor("#B8801F"))
    c.setLineWidth(0.5)
    c.line(center_x - 40 * mm, height - 38 * mm, center_x + 40 * mm, height - 38 * mm)

    # "This certifies that"
    c.setFont("Helvetica-Oblique", 12)
    c.setFillColor(colors.HexColor("#475569"))
    c.drawCentredString(center_x, height - 50 * mm, "This certifies that")

    # Name (larger, more prominent)
    full_name = f"{cert['first_name']} {cert['surname']}"
    c.setFont("Helvetica-Bold", 32)
    c.setFillColor(colors.HexColor("#0F172A"))
    c.drawCentredString(center_x, height - 65 * mm, full_name)

    # Decorative underline for name
    name_width = c.stringWidth(full_name, "Helvetica-Bold", 32)
    c.setStrokeColor(colors.HexColor("#B8801F"))
    c.setLineWidth(0.5)
    c.line(center_x - name_width/2 - 5*mm, height - 68*mm,
           center_x + name_width/2 + 5*mm, height - 68*mm)

    # Achievement text
    c.setFont("Helvetica", 13)
    c.setFillColor(colors.HexColor("#334155"))
    c.drawCentredString(center_x, height - 80 * mm, "has been assessed for career readiness for the occupation")

    # Career (prominent, kept centered, not extending to sig area)
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(colors.HexColor("#B8801F"))
    career_text = cert["career"]
    # Truncate very long career names so they stay on one line
    max_career_chars = 42
    if len(career_text) > max_career_chars:
        career_text = career_text[:max_career_chars] + "..."
    c.drawCentredString(center_x, height - 92 * mm, career_text)

    # Score box (Udemy-style)
    c.setFont("Helvetica", 11)
    c.setFillColor(colors.HexColor("#475569"))
    c.drawCentredString(center_x, height - 108 * mm, "Career Readiness Score")

    c.setFont("Helvetica-Bold", 28)
    c.setFillColor(colors.HexColor("#B8801F"))
    c.drawCentredString(center_x, height - 122 * mm, f"{cert['score']}/100")

    # Issue / validity section. No personal signature: a handwritten
    # signature image in a public repo can be copied, and the certificate's
    # authority comes from the public verification link, not a signature.
    issued_dt = datetime.fromisoformat(cert["issued_at"])
    valid_until_dt = certificate_valid_until(issued_dt)
    issued_str = _format_date(issued_dt)
    valid_str = _format_date(valid_until_dt)

    for x, value, label in (
        (width * 0.3, issued_str, "Date Issued"),
        (width * 0.7, valid_str, "Valid Until"),
    ):
        c.setFont("Helvetica", 10)
        c.setFillColor(colors.HexColor("#334155"))
        c.drawCentredString(x, 55 * mm, value)
        c.setStrokeColor(colors.HexColor("#CBD5E1"))
        c.setLineWidth(0.5)
        c.line(x - 30 * mm, 52 * mm, x + 30 * mm, 52 * mm)
        c.setFont("Helvetica", 8)
        c.setFillColor(colors.HexColor("#475569"))
        c.drawCentredString(x, 46 * mm, label)

    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor("#475569"))
    c.drawCentredString(center_x, 40 * mm, f"Issued by {ISSUER_NAME}  \u00b7  Method {METHOD_VERSION}")

    # Bottom info
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor("#64748B"))
    c.drawCentredString(center_x, 33 * mm, f"Certificate ID: {cert['certificate_id']}")

    verify_base = os.environ.get("PUBLIC_VERIFY_URL_BASE", "https://srmaps.co.za").rstrip("/")
    verify_line = (
        f"Verify at: {verify_base}/verify/{cert['certificate_id']}"
        if verify_base
        else f"Verify authenticity at: /verify/{cert['certificate_id']}"
    )
    c.drawCentredString(center_x, 29 * mm, verify_line)

    c.setFont("Helvetica-Oblique", 7)
    c.setFillColor(colors.HexColor("#94A3B8"))
    c.drawCentredString(
        center_x,
        23 * mm,
        "Automated skills assessment of the CV supplied by the holder. Name as entered by the holder. "
        "Not a qualification or professional accreditation.",
    )
    c.drawCentredString(
        center_x,
        19.5 * mm,
        "Skills data: O*NET Database, U.S. Department of Labor/ETA, used under CC BY 4.0.",
    )

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue()
