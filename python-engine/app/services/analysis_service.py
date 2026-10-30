from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from app.extractors.cv_extractor import CVExtractionError, ExtractedCV, extract_cv
from app.models.schemas import AnalysisResponse, CvBasic, OnetSourceInfo, PrivacyWarning, SkillBreakdownItem
from app.nlp.skill_extractor import extract_skill_evidence
from app.recommendations.cv_checks import PRIVACY_ADVICE, cv_basics, cv_steps, privacy_warnings, work_link_step
from app.recommendations.engine import action_for, generate_recommendations
from app.scoring.career_model import CareerModel, get_career_model
from app.scoring.scorer import ScoringResult, score_career_readiness
from app.scoring.sa_requirements import sa_requirements_for
from app.scoring.sa_titles import resolve_sa_title
from app.db.interface import Repository

GENERIC_BENCHMARK_DISCLAIMER = (
    "How this works: your CV is compared with the skills, knowledge areas and tools "
    "that the O*NET database (U.S. Department of Labor) rates as important for this "
    "occupation. A skill counts as found when your CV shows it in words a recruiter "
    "would recognise. The score reflects your CV, not everything you can do, so "
    "adding clear evidence to your CV can raise it. Tools count as a group: any 3 of "
    "the listed tools earn full credit."
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
            importance_level=d.importance_level,
            is_tool=d.is_tool,
            tip=None if d.present and d.final_score >= 0.35 else action_for(d),
        )
        for d in sorted(result.skill_details, key=lambda d: (d.is_tool, -d.market_importance))
    ]


def run_analysis(
    *,
    store: Repository,
    filename: str,
    file_bytes: bytes,
    first_name: str,
    surname: str,
    career_slug: str,
    career_title: Optional[str] = None,
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
            "typed CV as a PDF or Word file."
        )

    evidence = extract_skill_evidence(cv)
    # Pass the raw CV text for education level detection
    result = score_career_readiness(evidence, career_model, cv_text=cv.raw_text)

    gap_details = result.gap_details or []
    breakdown = _build_breakdown(result)
    onet_source = _build_onet_source_info(career_model)
    # Show the South African title the user picked (if it really is one
    # linked to this career); the O*NET occupation is kept for reference.
    display_name = resolve_sa_title(career_model.slug, career_title) or career_model.name
    soc_code = career_model.onet.soc_code if career_model.onet else None
    sa_requirements = sa_requirements_for(soc_code, cv.raw_text)

    # Next steps: all things to add or change on the CV, most useful first.
    first_steps = []
    missing_required = [r for r in sa_requirements if not r["found_in_cv"] and r.get("kind") == "required"]
    if missing_required:
        labels = " and ".join(r["label"] for r in missing_required[:2])
        first_steps.append(
            f"South African employers check for {labels} for this job. If you have it, "
            "state it clearly on your CV, with your registration or licence number if you have one."
        )
    first_steps += cv_steps(cv)
    link_step = work_link_step(soc_code, cv)
    recommendations = generate_recommendations(gap_details, limit=4 if link_step else 5, first_steps=first_steps)
    if link_step:
        recommendations.append(link_step)

    warnings = privacy_warnings(cv)
    basics = [b.__dict__ for b in cv_basics(cv)]

    analysis_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()

    payload = {
        "career_slug": career_model.slug,
        "career_name": display_name,
        "onet_career_name": career_model.name,
        "sa_requirements": sa_requirements,
        "strengths": result.strengths,
        "gaps": result.gaps,
        "skill_breakdown": [b.model_dump() for b in breakdown],
        "recommendations": recommendations,
        "onet_source": onet_source.model_dump(),
        # Only the KIND of personal detail found, never its value.
        "privacy_warnings": warnings,
        "cv_basics": basics,
    }

    store.save_analysis(
        {
            "id": analysis_id,
            "first_name": first_name,
            "surname": surname,
            "career": display_name,
            "score": result.overall_score,
            "payload": payload,
            "created_at": created_at,
        }
    )

    return AnalysisResponse(
        analysis_id=analysis_id,
        score=result.overall_score,
        career=display_name,
        career_slug=career_model.slug,
        onet_career=career_model.name,
        first_name=first_name,
        surname=surname,
        strengths=result.strengths,
        gaps=result.gaps,
        skill_breakdown=breakdown,
        recommendations=recommendations,
        benchmark_disclaimer=GENERIC_BENCHMARK_DISCLAIMER,
        onet_source=onet_source,
        sa_requirements=sa_requirements,
        privacy_warnings=[PrivacyWarning(**w) for w in warnings],
        privacy_advice=PRIVACY_ADVICE if warnings else None,
        cv_basics=[CvBasic(**b) for b in basics],
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
        onet_career=payload.get("onet_career_name"),
        first_name=record["first_name"],
        surname=record["surname"],
        strengths=payload.get("strengths", []),
        gaps=payload.get("gaps", []),
        skill_breakdown=[SkillBreakdownItem(**item) for item in payload.get("skill_breakdown", [])],
        recommendations=payload.get("recommendations", []),
        benchmark_disclaimer=GENERIC_BENCHMARK_DISCLAIMER,
        onet_source=OnetSourceInfo(**onet_source_raw) if onet_source_raw else None,
        sa_requirements=payload.get("sa_requirements", []),
        privacy_warnings=[PrivacyWarning(**w) for w in payload.get("privacy_warnings", [])],
        privacy_advice=PRIVACY_ADVICE if payload.get("privacy_warnings") else None,
        cv_basics=[CvBasic(**b) for b in payload.get("cv_basics", [])],
        created_at=record["created_at"],
    )
