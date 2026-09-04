from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import Response

from app.db.interface import Repository
from app.db.local_store import get_store
from app.models.schemas import (
    AnalysisResponse,
    CertificateRequest,
    CertificateResponse,
    CertificateVerifyResponse,
)
from app.scoring.career_model import list_careers
from app.services.analysis_service import AnalysisError, get_analysis_response, run_analysis
from app.services.certificate_service import (
    CertificateError,
    create_certificate,
    render_certificate_pdf,
    verify_certificate,
)

router = APIRouter()

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = (".pdf", ".docx")


def get_repository() -> Repository:
    return get_store()


@router.get("/careers")
def careers_endpoint():
    return {"careers": list_careers()}


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_endpoint(
    first_name: str = Form(...),
    surname: str = Form(...),
    career: str = Form(...),
    file: UploadFile = File(...),
    store: Repository = Depends(get_repository),
):
    if not file.filename or not file.filename.lower().endswith(ALLOWED_EXTENSIONS):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file format. Please upload a PDF or DOCX file.",
        )

    file_bytes = await file.read()
    if len(file_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=400, detail="File is too large (10MB limit).")

    try:
        result = run_analysis(
            store=store,
            filename=file.filename,
            file_bytes=file_bytes,
            first_name=first_name,
            surname=surname,
            career_slug=career,
        )
    except AnalysisError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc

    return result


@router.get("/analysis/{analysis_id}", response_model=AnalysisResponse)
def get_analysis_endpoint(analysis_id: str, store: Repository = Depends(get_repository)):
    result = get_analysis_response(store=store, analysis_id=analysis_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    return result


@router.post("/certificate", response_model=CertificateResponse)
def certificate_endpoint(payload: CertificateRequest, store: Repository = Depends(get_repository)):
    try:
        result = create_certificate(
            store=store,
            analysis_id=payload.analysis_id,
            first_name=payload.first_name,
            surname=payload.surname,
        )
    except CertificateError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return result


@router.get("/certificate/{certificate_id}/pdf")
def certificate_pdf_endpoint(certificate_id: str, store: Repository = Depends(get_repository)):
    pdf_bytes = render_certificate_pdf(store=store, certificate_id=certificate_id)
    if pdf_bytes is None:
        raise HTTPException(status_code=404, detail="Certificate not found.")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{certificate_id}.pdf"'},
    )


@router.get("/verify/{certificate_id}", response_model=CertificateVerifyResponse)
def verify_endpoint(certificate_id: str, store: Repository = Depends(get_repository)):
    return verify_certificate(store=store, certificate_id=certificate_id)
