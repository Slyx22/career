"""
Explainable career-readiness scoring engine.

This is the SOLE authority for the numeric readiness score. No LLM is
involved in deciding the number - an LLM (if configured later) may only
be used to phrase recommendations more naturally, never to change scores.

Conceptual model per skill (see build spec section 16):

    skill_contribution = coverage x evidence x depth x recency x importance

Where:
    coverage    = 1 if the skill is present at all in the CV, else 0
    evidence    = evidence_score from the NLP layer (0-1)
    depth       = depth_score from the NLP layer (0-1)
    recency     = recency_score from the NLP layer (0-1)
    importance  = market_importance from the career model (0-1)

The per-skill contributions are combined into an overall 0-100 score,
weighted by each skill's market_frequency (how often it matters for this
career) so rare/niche skills don't dominate the score as much as core
skills.

EDUCATION BOOST (added): Relevant degrees/diplomas provide a modest boost
to the overall score (5-15 points) to reward formal education attainment.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from app.nlp.skill_extractor import SkillEvidence
from app.nlp.taxonomy import SKILL_BY_SLUG
from app.scoring.career_model import CareerModel
from app.nlp.education_detector import detect_education_level, calculate_education_boost, EducationInfo

# O*NET rates broad abilities such as active listening or speaking as
# important for almost every occupation, but CVs rarely name them and
# recruiters screen mainly on job-specific knowledge and tools. These
# categories still count, at half weight, so a CV isn't marked down mainly
# for not spelling out "active listening".
GENERAL_SKILL_CATEGORIES = {"Core skills", "People skills"}
GENERAL_SKILL_WEIGHT = 0.5

# O*NET lists many software tools per occupation; nobody uses all of them.
# The tools count as one group: having any TOOLS_EXPECTED of the listed
# tools earns full credit for the group.
TOOL_SOURCE = "onet_technology_skills"
TOOLS_EXPECTED = 3


@dataclass
class SkillScoreDetail:
    slug: str
    name: str
    category: str
    present: bool
    evidence_score: float
    depth_score: float
    recency_score: float
    market_frequency: float
    market_importance: float
    final_score: float  # 0-1, this skill's normalized contribution
    weight_source: str = "benchmark_estimate"
    onet_confirmed: bool = False
    effective_weight: float = 0.0  # weight in the overall score (after general/tool adjustments)
    importance_level: str = ""  # "essential" | "important" | "useful"
    is_tool: bool = False


@dataclass
class ScoringResult:
    overall_score: int  # 0-100
    skill_details: List[SkillScoreDetail]
    strengths: List[str]
    gaps: List[str]
    education_info: Optional[EducationInfo] = None  # Detected education level
    education_boost: float = 0.0  # Points added for education (0-15)
    gap_details: List["SkillScoreDetail"] = None  # gaps, most valuable to close first
    tools_found: int = 0
    tools_listed: int = 0


def score_career_readiness(
    evidence_by_slug: Dict[str, SkillEvidence], career_model: CareerModel, cv_text: Optional[str] = None
) -> ScoringResult:
    details: List[SkillScoreDetail] = []
    weighted_sum = 0.0
    weight_total = 0.0

    for weight in career_model.skills:
        skill = SKILL_BY_SLUG.get(weight.skill_slug)
        if skill is None:
            continue
        ev = evidence_by_slug.get(weight.skill_slug)

        coverage = 1.0 if (ev and ev.present) else 0.0
        evidence_score = ev.evidence_score if ev else 0.0
        depth_score = ev.depth_score if ev else 0.0
        recency_score = ev.recency_score if ev else 0.0

        # Per-skill normalized contribution (0-1).
        skill_final = coverage * (
            0.45 * evidence_score + 0.35 * depth_score + 0.20 * recency_score
        )

        # Skills the person doesn't have at all contribute 0, which is
        # correct - the market_importance still determines how much that
        # absence costs them via the weighting below.
        importance_weight = weight.market_importance
        frequency_weight = weight.market_frequency
        combined_weight = (0.6 * importance_weight) + (0.4 * frequency_weight)
        if skill.category in GENERAL_SKILL_CATEGORIES:
            combined_weight *= GENERAL_SKILL_WEIGHT

        # Irrelevant skills (low market importance) contribute 0 — prevents
        # unrelated skills (e.g., Python in non-ML career) from inflating score.
        if importance_weight < 0.05:
            skill_final = 0.0

        is_tool = weight.source == TOOL_SOURCE
        if importance_weight >= 0.7:
            level = "essential"
        elif importance_weight >= 0.55:
            level = "important"
        else:
            level = "useful"

        details.append(
            SkillScoreDetail(
                slug=skill.slug,
                name=skill.canonical,
                category=skill.category,
                present=bool(coverage),
                evidence_score=round(evidence_score, 3),
                depth_score=round(depth_score, 3),
                recency_score=round(recency_score, 3),
                market_frequency=weight.market_frequency,
                market_importance=weight.market_importance,
                final_score=round(skill_final, 3),
                weight_source=weight.source,
                onet_confirmed=weight.onet_confirmed,
                effective_weight=combined_weight,
                importance_level="useful" if is_tool else level,
                is_tool=is_tool,
            )
        )

    # Skills and knowledge: each counts with its own weight.
    for d in details:
        if not d.is_tool:
            weighted_sum += d.final_score * d.effective_weight
            weight_total += d.effective_weight

    # Tools: one group. The best TOOLS_EXPECTED tool scores count, at the
    # average tool weight, so knowing any 3 of the listed tools is full credit.
    tools = [d for d in details if d.is_tool]
    tools_found = sum(1 for d in tools if d.present)
    if tools:
        slots = min(TOOLS_EXPECTED, len(tools))
        avg_w = sum(d.effective_weight for d in tools) / len(tools)
        best = sorted((d.final_score for d in tools), reverse=True)[:slots]
        weighted_sum += sum(best) * avg_w
        weight_total += slots * avg_w
        for d in tools:
            d.effective_weight = avg_w * slots / len(tools)

    overall_fraction = (weighted_sum / weight_total) if weight_total else 0.0
    base_score = max(0.0, min(1.0, overall_fraction)) * 100

    # Detect education level and calculate boost
    education_info = None
    education_boost = 0.0
    if cv_text:
        education_info = detect_education_level(cv_text)
        education_boost = calculate_education_boost(education_info)

    # Apply education boost (capped at 100)
    overall_score = round(min(100, base_score + education_boost))

    # Strengths: present skills with strong final_score, job-specific ones
    # (knowledge, technical skills, tools) first, then by importance.
    present_sorted = sorted(
        [d for d in details if d.present and d.final_score >= 0.45],
        key=lambda d: (d.category not in GENERAL_SKILL_CATEGORIES, d.market_importance, d.final_score),
        reverse=True,
    )
    strengths = [d.name for d in present_sorted[:6]]

    # Gaps: missing or weak skills, ranked by how many points closing them
    # would add (their weight in the score x how much is missing). Missing
    # tools only count as gaps while fewer than TOOLS_EXPECTED tools were
    # found, and then only the most in-demand ones.
    def points(d):
        return d.effective_weight * (1.0 - d.final_score)

    gap_candidates = [d for d in details if not d.is_tool and ((not d.present) or d.final_score < 0.35)]
    if tools and tools_found < min(TOOLS_EXPECTED, len(tools)):
        missing_tools = sorted((d for d in tools if not d.present), key=lambda d: d.market_importance, reverse=True)
        needed = min(TOOLS_EXPECTED, len(tools)) - tools_found
        for d in missing_tools[:needed]:
            d.effective_weight = avg_w  # each missing tool would fill one full slot
            gap_candidates.append(d)
    gap_candidates.sort(key=points, reverse=True)
    gaps = [d.name for d in gap_candidates[:6]]

    return ScoringResult(
        overall_score=overall_score,
        skill_details=details,
        strengths=strengths,
        gaps=gaps,
        education_info=education_info,
        education_boost=round(education_boost, 1),
        gap_details=gap_candidates,
        tools_found=tools_found,
        tools_listed=len(tools),
    )
