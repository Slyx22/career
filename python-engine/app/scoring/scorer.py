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
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from app.nlp.skill_extractor import SkillEvidence
from app.nlp.taxonomy import SKILL_BY_SLUG
from app.scoring.career_model import CareerModel


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


@dataclass
class ScoringResult:
    overall_score: int  # 0-100
    skill_details: List[SkillScoreDetail]
    strengths: List[str]
    gaps: List[str]


def score_career_readiness(
    evidence_by_slug: Dict[str, SkillEvidence], career_model: CareerModel
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

        weighted_sum += skill_final * combined_weight
        weight_total += combined_weight

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
            )
        )

    overall_fraction = (weighted_sum / weight_total) if weight_total else 0.0
    overall_score = round(max(0.0, min(1.0, overall_fraction)) * 100)

    # Strengths: present skills with strong final_score, ranked by
    # importance so the most career-relevant strengths surface first.
    present_sorted = sorted(
        [d for d in details if d.present and d.final_score >= 0.45],
        key=lambda d: (d.market_importance, d.final_score),
        reverse=True,
    )
    strengths = [d.name for d in present_sorted[:6]]

    # Gaps: absent or weak skills, ranked by how much they'd matter
    # (importance x frequency) - the highest-value gaps to close first.
    gap_candidates = sorted(
        [d for d in details if (not d.present) or d.final_score < 0.35],
        key=lambda d: (d.market_importance * d.market_frequency),
        reverse=True,
    )
    gaps = [d.name for d in gap_candidates[:6]]

    return ScoringResult(overall_score=overall_score, skill_details=details, strengths=strengths, gaps=gaps)
