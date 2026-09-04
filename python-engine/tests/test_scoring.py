from app.extractors.cv_extractor import extract_from_text
from app.nlp.skill_extractor import extract_skill_evidence
from app.scoring.career_model import get_career_model
from app.scoring.scorer import score_career_readiness

from tests.fixtures import (
    BEGINNER_CV,
    DATA_SCIENTIST_TRANSITION_CV,
    STRONG_ML_ENGINEER_CV,
)


def _score_for(text: str) -> int:
    cv = extract_from_text(text)
    evidence = extract_skill_evidence(cv)
    career_model = get_career_model("ml-engineer")
    result = score_career_readiness(evidence, career_model)
    return result.overall_score


def test_strong_cv_scores_high():
    score = _score_for(STRONG_ML_ENGINEER_CV)
    assert score >= 65, f"expected a high score for a strong CV, got {score}"


def test_beginner_cv_scores_low():
    score = _score_for(BEGINNER_CV)
    assert score <= 40, f"expected a low score for a beginner CV, got {score}"


def test_strong_cv_scores_higher_than_beginner():
    assert _score_for(STRONG_ML_ENGINEER_CV) > _score_for(BEGINNER_CV)


def test_data_scientist_transition_has_deployment_gaps():
    cv = extract_from_text(DATA_SCIENTIST_TRANSITION_CV)
    evidence = extract_skill_evidence(cv)
    career_model = get_career_model("ml-engineer")
    result = score_career_readiness(evidence, career_model)

    assert 30 <= result.overall_score <= 80
    gap_slugs = set()
    for detail in result.skill_details:
        if (not detail.present) or detail.final_score < 0.35:
            gap_slugs.add(detail.slug)

    # Should surface at least one deployment/MLOps-style gap.
    assert gap_slugs & {"docker", "kubernetes", "aws", "gcp", "azure", "model_deployment", "cicd", "mlflow"}


def test_skill_presence_detected_for_strong_cv():
    cv = extract_from_text(STRONG_ML_ENGINEER_CV)
    evidence = extract_skill_evidence(cv)
    assert evidence["python"].present
    assert evidence["docker"].present
    assert evidence["pytorch"].present


def test_evidence_score_higher_for_applied_vs_listed_skill():
    cv = extract_from_text(STRONG_ML_ENGINEER_CV)
    evidence = extract_skill_evidence(cv)
    # "Built and deployed a production ML inference API using Python" should
    # give Python's evidence a strong score, well above the neutral baseline.
    assert evidence["python"].evidence_score > 0.6


def test_depth_not_leaked_across_sentence_boundary():
    """
    Regression test: a strong evidence verb in one sentence must not
    inflate the depth score of a skill mentioned only in the *next*
    sentence. Evidence must be scoped to the sentence containing the
    actual mention, not a fixed character window that can bleed into
    neighbouring sentences.
    """
    cv = extract_from_text(
        "Built and deployed a production recommendation engine end to end. "
        "Also somewhat familiar with Kubernetes from a single tutorial."
    )
    evidence = extract_skill_evidence(cv)
    kubernetes = evidence["kubernetes"]

    assert kubernetes.present
    # "familiar with" should pull depth down (weak evidence), not up -
    # the neighbouring sentence's "Built and deployed" must not leak in.
    assert kubernetes.depth_score <= 0.3, (
        f"expected low depth for a merely-familiar mention, got {kubernetes.depth_score}"
    )


def test_depth_correctly_high_when_verb_is_in_same_sentence():
    """Sanity check the same regression scenario the other way round:
    when the strong verb genuinely is in the same sentence as the
    skill, depth should still score high."""
    cv = extract_from_text(
        "Also somewhat familiar with tutorials in general. "
        "Built and deployed a production Kubernetes cluster for model serving."
    )
    evidence = extract_skill_evidence(cv)
    kubernetes = evidence["kubernetes"]

    assert kubernetes.present
    assert kubernetes.depth_score >= 0.75
