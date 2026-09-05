from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class SkillBreakdownItem(BaseModel):
    slug: str
    name: str
    category: str
    present: bool
    score_percent: int  # 0-100, for the UI progress bar
    weight_source: str = "benchmark_estimate"  # "onet_api" | "onet_technology_list_only" | "benchmark_estimate"
    onet_confirmed: bool = False


class OnetSourceInfo(BaseModel):
    soc_code: Optional[str] = None
    occupation_title: Optional[str] = None
    source_url: Optional[str] = None
    last_synced: Optional[str] = None
    note: Optional[str] = None
    onet_confirmed_skill_count: int = 0
    total_skill_count: int = 0


class AnalysisResponse(BaseModel):
    analysis_id: str
    score: int
    career: str
    career_slug: str
    first_name: str
    surname: str
    strengths: List[str]
    gaps: List[str]
    skill_breakdown: List[SkillBreakdownItem]
    recommendations: List[str]
    benchmark_disclaimer: str
    onet_source: Optional[OnetSourceInfo] = None
    created_at: str


class CertificateRequest(BaseModel):
    analysis_id: str = Field(..., min_length=1)
    first_name: str = Field(..., min_length=1)
    surname: str = Field(..., min_length=1)
    clerk_user_id: Optional[str] = Field(
        default=None,
        description=(
            "The signed-in user's Clerk user id, set by the Next.js server "
            "after verifying the session - never sent by the browser "
            "directly. Certificates are free but require an account; see "
            "REQUIRE_ACCOUNT_FOR_CERTIFICATE."
        ),
    )


class CertificateResponse(BaseModel):
    certificate_id: str
    first_name: str
    surname: str
    career: str
    score: int
    issued_at: str
    verify_path: str


class CertificateVerifyResponse(BaseModel):
    verified: bool
    certificate_id: Optional[str] = None
    first_name: Optional[str] = None
    surname: Optional[str] = None
    career: Optional[str] = None
    score: Optional[int] = None
    issued_at: Optional[str] = None


class CertificateListResponse(BaseModel):
    certificates: List[CertificateResponse]


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
