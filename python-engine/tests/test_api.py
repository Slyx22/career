import io
import os
import tempfile

os.environ.setdefault("LOCAL_DB_PATH", os.path.join(tempfile.gettempdir(), "test_local_dev.db"))

import pytest
from docx import Document
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _make_docx_bytes(text: str) -> bytes:
    doc = Document()
    for line in text.splitlines():
        doc.add_paragraph(line)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


STRONG_CV_TEXT = """
SUMMARY
Machine learning engineer.

EXPERIENCE
Built and deployed a production ML inference API using Python and FastAPI.
Designed and trained deep learning models using PyTorch on AWS with Docker
and Kubernetes. Implemented CI/CD with MLflow experiment tracking.

SKILLS
Python, SQL, Docker, Kubernetes, AWS, PyTorch, FastAPI, MLflow
"""


def test_health_check():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_careers_endpoint():
    resp = client.get("/api/careers")
    assert resp.status_code == 200
    careers = resp.json()["careers"]
    assert any(c["slug"] == "ml-engineer" for c in careers)


def test_analyze_missing_first_name_rejected():
    file_bytes = _make_docx_bytes(STRONG_CV_TEXT)
    resp = client.post(
        "/api/analyze",
        data={"first_name": "", "surname": "Smith", "career": "ml-engineer"},
        files={"file": ("cv.docx", file_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )
    assert resp.status_code == 400


def test_analyze_unsupported_file_rejected():
    resp = client.post(
        "/api/analyze",
        data={"first_name": "John", "surname": "Smith", "career": "ml-engineer"},
        files={"file": ("cv.txt", b"hello", "text/plain")},
    )
    assert resp.status_code == 400


def test_full_analysis_and_certificate_flow():
    file_bytes = _make_docx_bytes(STRONG_CV_TEXT)
    analyze_resp = client.post(
        "/api/analyze",
        data={"first_name": "John", "surname": "Smith", "career": "ml-engineer"},
        files={"file": ("cv.docx", file_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )
    assert analyze_resp.status_code == 200
    analysis = analyze_resp.json()
    assert 0 <= analysis["score"] <= 100
    assert analysis["career"] == "ML Engineer"
    assert isinstance(analysis["skill_breakdown"], list) and len(analysis["skill_breakdown"]) > 0

    fetch_resp = client.get(f"/api/analysis/{analysis['analysis_id']}")
    assert fetch_resp.status_code == 200
    assert fetch_resp.json()["score"] == analysis["score"]

    cert_resp = client.post(
        "/api/certificate",
        json={"analysis_id": analysis["analysis_id"], "first_name": "John", "surname": "Smith"},
    )
    assert cert_resp.status_code == 200
    cert = cert_resp.json()
    assert cert["certificate_id"].startswith("CR-")
    assert cert["first_name"] == "John"
    assert cert["surname"] == "Smith"

    verify_resp = client.get(f"/api/verify/{cert['certificate_id']}")
    assert verify_resp.status_code == 200
    verify_data = verify_resp.json()
    assert verify_data["verified"] is True
    assert verify_data["first_name"] == "John"

    pdf_resp = client.get(f"/api/certificate/{cert['certificate_id']}/pdf")
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["content-type"] == "application/pdf"
    assert pdf_resp.content[:4] == b"%PDF"


def test_verify_invalid_certificate_id_returns_not_verified():
    resp = client.get("/api/verify/CR-DOESNOTEXIST")
    assert resp.status_code == 200
    assert resp.json()["verified"] is False


def test_certificate_requires_existing_analysis():
    resp = client.post(
        "/api/certificate",
        json={"analysis_id": "does-not-exist", "first_name": "John", "surname": "Smith"},
    )
    assert resp.status_code == 404


def test_get_missing_analysis_returns_404_not_unhandled_exception():
    """Regression test: get_analysis_response raises AnalysisError for a
    missing analysis - the route must catch it and return a clean 404,
    not let it propagate as an unhandled 500."""
    resp = client.get("/api/analysis/does-not-exist")
    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


def test_certificate_stores_and_lists_by_clerk_user_id():
    """
    Certificates are free but tied to an account once Clerk is connected
    (see frontend/app/api/certificate/route.ts for the actual sign-in
    gate - that's enforced at the Next.js layer, not here). The Python
    engine just needs to correctly store and retrieve by clerk_user_id
    when the Next.js layer supplies one.
    """
    file_bytes = _make_docx_bytes(STRONG_CV_TEXT)
    analyze_resp = client.post(
        "/api/analyze",
        data={"first_name": "Ada", "surname": "Lovelace", "career": "ml-engineer"},
        files={"file": ("cv.docx", file_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )
    analysis = analyze_resp.json()

    cert_resp = client.post(
        "/api/certificate",
        json={
            "analysis_id": analysis["analysis_id"],
            "first_name": "Ada",
            "surname": "Lovelace",
            "clerk_user_id": "user_test_12345",
        },
    )
    assert cert_resp.status_code == 200
    cert = cert_resp.json()

    list_resp = client.get("/api/certificates", params={"clerk_user_id": "user_test_12345"})
    assert list_resp.status_code == 200
    certs = list_resp.json()["certificates"]
    assert any(c["certificate_id"] == cert["certificate_id"] for c in certs)

    # A different (or no) user id should not see this certificate.
    other_resp = client.get("/api/certificates", params={"clerk_user_id": "user_someone_else"})
    assert other_resp.status_code == 200
    assert all(c["certificate_id"] != cert["certificate_id"] for c in other_resp.json()["certificates"])


def test_certificate_without_clerk_user_id_still_works_by_default():
    """Local dev / Clerk-not-configured behavior must be unaffected:
    certificates can still be created with no clerk_user_id unless
    REQUIRE_ACCOUNT_FOR_CERTIFICATE is explicitly turned on."""
    file_bytes = _make_docx_bytes(STRONG_CV_TEXT)
    analyze_resp = client.post(
        "/api/analyze",
        data={"first_name": "Grace", "surname": "Hopper", "career": "ml-engineer"},
        files={"file": ("cv.docx", file_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
    )
    analysis = analyze_resp.json()

    cert_resp = client.post(
        "/api/certificate",
        json={"analysis_id": analysis["analysis_id"], "first_name": "Grace", "surname": "Hopper"},
    )
    assert cert_resp.status_code == 200
