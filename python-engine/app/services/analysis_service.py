from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.extractors.cv_extractor import CVExtractionError, ExtractedCV, extract_cv
from app.models.schemas import AnalysisResponse, OnetSourceInfo, SkillBreakdownItem
from app.nlp.skill_extractor import extract_skill_evidence
from app.recommendations.engine import generate_recommendations
from app.scoring.career_model import CareerModel, get_career_model
from app.scoring.scorer import ScoringResult, score_career_readiness
from app.db.interface import Repository

GENERIC_BENCHMARK_DISCLAIMER = (
    "Skill importance and frequency figures used in this analysis are a mix of "
    "O*NET-sourced data and initial benchmark estimates set by the product team. "
    "See onet_source below for which skills are independently verified."
)


class AnalysisError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _build_onet_source_info(career_model: CareerModel) -> OnetSourceInfo:
    onet = career_model.onet
    return OnetSourceInfo(
        soc_code=onet.soc_code if onet else None,
        occupation_title=onet.occupation_title if onet else None,
        source_url=onet.source_url if onet else None,
        last_synced=onet.last_synced if onet else None,
        note=onet.note if onet else None,
        onet_confirmed_skill_count=career_model.onet_confirmed_skill_count,
        total_skill_count=len(career_model.skills),
    )


def _build_breakdown(result: ScoringResult) -> list:
    return [
        SkillBreakdownItem(
            slug=d.slug,
            name=d.name,
            category=d.category,
            present=d.present,
            score_percent=round(d.final_score * 100),
            weight_source=d.weight_source,
            onet_confirmed=d.onet_confirmed,
        )
        for d in sorted(result.skill_details, key=lambda d: d.market_importance, reverse=True)
    ]


def run_analysis(
    *,
    store: Repository,
    filename: str,
    file_bytes: bytes,
    first_name: str,
    surname: str,
    career_slug: str,
) -> AnalysisResponse:
    first_name = (first_name or "").strip()
    surname = (surname or "").strip()

    if not first_name:
        raise AnalysisError("First name is required.")
    if not surname:
        raise AnalysisError("Surname is required.")
    if not file_bytes:
        raise AnalysisError("A CV file is required.")

    try:
        career_model = get_career_model(career_slug)
    except KeyError as exc:
        raise AnalysisError(f"Unsupported career: {career_slug}") from exc

    try:
        cv: ExtractedCV = extract_cv(filename, file_bytes)
    except CVExtractionError as exc:
        raise AnalysisError(str(exc)) from exc

    if cv.is_empty:
        raise AnalysisError(
            "The uploaded CV appears to be empty or unreadable. Please upload a "
            "text-based PDF or DOCX file."
        )

    evidence = extract_skill_evidence(cv)
    result = score_career_readiness(evidence, career_model)

    gap_details = sorted(
        [d for d in result.skill_details if (not d.present) or d.final_score < 0.35],
        key=lambda d: (d.market_importance * d.market_frequency),
        reverse=True,
    )
    recommendations = generate_recommendations(gap_details, limit=5)
    breakdown = _build_breakdown(result)
    onet_source = _build_onet_source_info(career_model)

    analysis_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()

    payload = {
        "career_slug": career_model.slug,
        "career_name": career_model.name,
        "strengths": result.strengths,
        "gaps": result.gaps,
        "skill_breakdown": [b.model_dump() for b in breakdown],
        "recommendations": recommendations,
        "onet_source": onet_source.model_dump(),
    }

    store.save_analysis(
        {
            "id": analysis_id,
            "first_name": first_name,
            "surname": surname,
            "career": career_model.name,
            "score": result.overall_score,
            "payload": payload,
            "created_at": created_at,
        }
    )

    return AnalysisResponse(
        analysis_id=analysis_id,
        score=result.overall_score,
        career=career_model.name,
        career_slug=career_model.slug,
        first_name=first_name,
        surname=surname,
        strengths=result.strengths,
        gaps=result.gaps,
        skill_breakdown=breakdown,
        recommendations=recommendations,
        benchmark_disclaimer=GENERIC_BENCHMARK_DISCLAIMER,
        onet_source=onet_source,
        created_at=created_at,
    )


def get_analysis_response(*, store: Repository, analysis_id: str) -> AnalysisResponse:
    record = store.get_analysis(analysis_id)
    if not record:
        raise AnalysisError("Analysis not found.", status_code=404)

    payload = record["payload"]
    onet_source_raw = payload.get("onet_source")
    return AnalysisResponse(
        analysis_id=record["id"],
        score=record["score"],
        career=payload.get("career_name", record["career"]),
        career_slug=payload.get("career_slug", ""),
        first_name=record["first_name"],
        surname=record["surname"],
        strengths=payload.get("strengths", []),
        gaps=payload.get("gaps", []),
        skill_breakdown=[SkillBreakdownItem(**item) for item in payload.get("skill_breakdown", [])],
        recommendations=payload.get("recommendations", []),
        benchmark_disclaimer=GENERIC_BENCHMARK_DISCLAIMER,
        onet_source=OnetSourceInfo(**onet_source_raw) if onet_source_raw else None,
        created_at=record["created_at"],
    )
