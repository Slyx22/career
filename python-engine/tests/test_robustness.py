"""
Robustness tests against messier CV formats: missing punctuation, mixed
strong/weak evidence sentences placed close together, career changers,
and inconsistent capitalization/spacing. These are the kinds of real CVs
that a fixed-window (rather than sentence-aware) heuristic gets wrong.
"""
from app.extractors.cv_extractor import extract_from_text
from app.nlp.skill_extractor import extract_skill_evidence
from app.scoring.career_model import get_career_model
from app.scoring.scorer import score_career_readiness

from tests.fixtures import (
    CAREER_CHANGER_CV,
    MIXED_SIGNALS_CV,
    NO_PUNCTUATION_BULLET_CV,
    ODD_FORMATTING_CV,
)


def _analyze(text: str):
    cv = extract_from_text(text)
    evidence = extract_skill_evidence(cv)
    career_model = get_career_model("ml-engineer")
    result = score_career_readiness(evidence, career_model)
    return evidence, result


def test_no_punctuation_cv_does_not_crash_and_scores_in_range():
    _, result = _analyze(NO_PUNCTUATION_BULLET_CV)
    assert 0 <= result.overall_score <= 100


def test_no_punctuation_cv_detects_applied_skills():
    evidence, _ = _analyze(NO_PUNCTUATION_BULLET_CV)
    assert evidence["python"].present
    assert evidence["docker"].present
    # "Built and deployed a fraud detection model using Python" is a
    # same-line strong-evidence statement even without a period.
    assert evidence["python"].depth_score >= 0.75


def test_mixed_signals_cv_keeps_evidence_scoped_per_sentence():
    evidence, _ = _analyze(MIXED_SIGNALS_CV)

    # Python/Git: genuinely built-and-shipped in the same sentence -> high depth.
    assert evidence["python"].depth_score >= 0.75

    # TensorFlow: "somewhat familiar with... from a weekend tutorial" ->
    # must stay low even though the previous sentence contains "Built and
    # shipped". This is the core regression this test file protects.
    assert evidence["tensorflow"].present
    assert evidence["tensorflow"].depth_score <= 0.3

    # Kubernetes: "Basic knowledge of... never used it hands-on" -> low too.
    assert evidence["kubernetes"].present
    assert evidence["kubernetes"].depth_score <= 0.3


def test_career_changer_scores_meaningfully_lower_than_strong_ml_cv():
    from tests.fixtures import STRONG_ML_ENGINEER_CV

    _, changer_result = _analyze(CAREER_CHANGER_CV)
    _, strong_result = _analyze(STRONG_ML_ENGINEER_CV)

    assert 0 <= changer_result.overall_score <= 100
    assert changer_result.overall_score < strong_result.overall_score
    # A backend developer with zero ML evidence should not score as
    # "ready" for an ML Engineer role.
    assert changer_result.overall_score <= 35


def test_odd_capitalization_and_spacing_still_matches_skills():
    evidence, result = _analyze(ODD_FORMATTING_CV)
    assert evidence["python"].present
    assert evidence["pytorch"].present
    assert evidence["docker"].present
    assert evidence["aws"].present
    assert 0 <= result.overall_score <= 100
