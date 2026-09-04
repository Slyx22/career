from __future__ import annotations

import io
import os
import secrets
import string
from datetime import datetime, timezone
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from app.db.interface import Repository
from app.models.schemas import CertificateResponse, CertificateVerifyResponse

_ID_ALPHABET = string.ascii_uppercase + string.digits


class CertificateError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _generate_certificate_id() -> str:
    suffix = "".join(secrets.choice(_ID_ALPHABET) for _ in range(8))
    return f"CR-{suffix}"


def create_certificate(
    *, store: Repository, analysis_id: str, first_name: str, surname: str
) -> CertificateResponse:
    analysis = store.get_analysis(analysis_id)
    if not analysis:
        raise CertificateError("Analysis not found. Please run an analysis first.", status_code=404)

    first_name = (first_name or "").strip()
    surname = (surname or "").strip()
    if not first_name or not surname:
        raise CertificateError("First name and surname are required to generate a certificate.")

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

    return CertificateVerifyResponse(
        verified=True,
        certificate_id=cert["certificate_id"],
        first_name=cert["first_name"],
        surname=cert["surname"],
        career=cert["career"],
        score=cert["score"],
        issued_at=cert["issued_at"],
    )


def render_certificate_pdf(*, store: Repository, certificate_id: str) -> Optional[bytes]:
    cert = store.get_certificate(certificate_id)
    if not cert:
        return None

    buffer = io.BytesIO()
    page_size = landscape(A4)
    c = canvas.Canvas(buffer, pagesize=page_size)
    width, height = page_size

    # Border
    c.setStrokeColor(colors.HexColor("#1E293B"))
    c.setLineWidth(3)
    c.rect(15 * mm, 15 * mm, width - 30 * mm, height - 30 * mm)
    c.setLineWidth(0.75)
    c.rect(19 * mm, 19 * mm, width - 38 * mm, height - 38 * mm)

    center_x = width / 2

    c.setFont("Helvetica", 12)
    c.setFillColor(colors.HexColor("#475569"))
    c.drawCentredString(center_x, height - 40 * mm, "CAREER READINESS CERTIFICATE")

    full_name = f"{cert['first_name']} {cert['surname']}".upper()
    c.setFont("Helvetica-Bold", 30)
    c.setFillColor(colors.HexColor("#0F172A"))
    c.drawCentredString(center_x, height - 60 * mm, full_name)

    c.setFont("Helvetica", 16)
    c.setFillColor(colors.HexColor("#334155"))
    c.drawCentredString(center_x, height - 72 * mm, cert["career"].upper())

    c.setFont("Helvetica", 11)
    c.drawCentredString(center_x, height - 88 * mm, "Career Readiness Score")
    c.setFont("Helvetica-Bold", 26)
    c.setFillColor(colors.HexColor("#2563EB"))
    c.drawCentredString(center_x, height - 100 * mm, f"{cert['score']} / 100")

    issued_dt = datetime.fromisoformat(cert["issued_at"])
    issued_str = issued_dt.strftime("%-d %B %Y") if os.name != "nt" else issued_dt.strftime("%d %B %Y")

    c.setFont("Helvetica", 10)
    c.setFillColor(colors.HexColor("#475569"))
    c.drawCentredString(center_x, 40 * mm, f"Assessment completed: {issued_str}")
    c.drawCentredString(center_x, 34 * mm, f"Certificate ID: {cert['certificate_id']}")

    verify_base = os.environ.get("PUBLIC_VERIFY_URL_BASE", "")
    verify_line = (
        f"Verify at: {verify_base}/verify/{cert['certificate_id']}"
        if verify_base
        else f"Verify at: /verify/{cert['certificate_id']}"
    )
    c.drawCentredString(center_x, 28 * mm, verify_line)

    c.setFont("Helvetica-Oblique", 8)
    c.setFillColor(colors.HexColor("#94A3B8"))
    c.drawCentredString(
        center_x,
        22 * mm,
        "This certificate confirms completion of a Career Readiness Assessment. "
        "It is not a professional accreditation or certification.",
    )

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer.getvalue()
