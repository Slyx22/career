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


def test_bullet_list_cv_sentences_are_not_glued_into_one_block():
    """
    Regression test for a real bug found testing a genuine student CV:
    lines separated only by a single newline (very common in bullet-list
    CVs exported from Word) were not being split into separate
    "sentences" at all, because the old SENTENCE_SPLIT regex required
    whitespace *after* the newline to trigger a split. That silently
    glued an entire bulleted skills section into one giant blob, letting
    evidence bleed between unrelated bullets.
    """
    from app.nlp.skill_extractor import _sentence_spans

    text = (
        "Summary line here.\n"
        "SKILLS\n"
        "HTML - MODERATE\n"
        "PYTHON - MODERATE\n"
        "CSS - MODERATE\n"
        "SQL - BEGINNER\n"
    )
    spans = _sentence_spans(text)
    # Each line should be its own span - not one giant blob.
    assert len(spans) >= 5


def test_explicit_self_rated_proficiency_overrides_vague_generic_mention():
    """
    A CV that both casually name-drops a skill in prose AND explicitly
    self-rates it in a skills list (e.g. 'SQL - BEGINNER') should reflect
    the explicit, more informative self-rating - not let a vague mention
    elsewhere quietly produce a more flattering neutral score.
    """
    cv = extract_from_text(
        "Summary\n"
        "Skilled in full-stack programming with Python, HTML, CSS, and SQL.\n"
        "Skills\n"
        "SQL - BEGINNER\n"
        "PYTHON - MODERATE\n"
    )
    evidence = extract_skill_evidence(cv)
    assert evidence["sql"].present
    assert evidence["sql"].depth_score <= 0.25, (
        f"expected the explicit 'BEGINNER' self-rating to dominate, got {evidence['sql'].depth_score}"
    )
    assert evidence["python"].present
    assert 0.35 <= evidence["python"].depth_score <= 0.55, (
        f"expected the explicit 'MODERATE' self-rating (~0.45), got {evidence['python'].depth_score}"
    )


def test_skill_list_without_explicit_level_still_gets_neutral_depth():
    """Sanity check the proficiency-override doesn't fire on a plain
    skills list with no self-rating at all."""
    cv = extract_from_text("Skills\nPython, SQL, Git\n")
    evidence = extract_skill_evidence(cv)
    assert evidence["python"].depth_score == 0.5
