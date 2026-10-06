"""Tests for education level detection."""
from app.nlp.education_detector import (
    EducationLevel,
    detect_education_level,
    calculate_education_boost,
)


def test_detects_phd():
    cv = "Education: PhD in Computer Science, MIT, 2020"
    result = detect_education_level(cv)
    assert result is not None
    assert result.level == EducationLevel.DOCTORAL
    assert result.confidence > 0.9


def test_detects_masters():
    cv = "MSc in Data Science, University of Cambridge, 2019"
    result = detect_education_level(cv)
    assert result is not None
    assert result.level == EducationLevel.MASTERS
    assert result.confidence > 0.9


def test_detects_bachelor():
    cv = "BSc Computer Science, University of Cape Town, 2018"
    result = detect_education_level(cv)
    assert result is not None
    assert result.level == EducationLevel.BACHELOR
    assert result.confidence > 0.85


def test_detects_diploma():
    cv = "National Diploma in Information Technology, 2017"
    result = detect_education_level(cv)
    assert result is not None
    assert result.level == EducationLevel.DIPLOMA
    assert result.confidence > 0.8


def test_detects_mba():
    cv = "MBA from Harvard Business School"
    result = detect_education_level(cv)
    assert result is not None
    assert result.level == EducationLevel.MASTERS


def test_detects_bachelor_variants():
    tests = [
        "Bachelor's degree in Engineering",
        "Bachelor of Science",
        "B.Sc in Mathematics",
    ]
    for cv in tests:
        result = detect_education_level(cv)
        assert result is not None
        assert result.level == EducationLevel.BACHELOR


def test_no_education_returns_none():
    cv = "Work Experience: Software Engineer at Google, 5 years"
    result = detect_education_level(cv)
    assert result is None


def test_education_boost_doctoral():
    cv = "PhD in Machine Learning"
    info = detect_education_level(cv)
    boost = calculate_education_boost(info)
    assert 12.0 <= boost <= 15.0  # PhD gets 15 points * confidence


def test_education_boost_masters():
    cv = "MSc Computer Science"
    info = detect_education_level(cv)
    boost = calculate_education_boost(info)
    assert 10.0 <= boost <= 12.5  # Masters gets ~12 points


def test_education_boost_bachelor():
    cv = "BSc Software Engineering"
    info = detect_education_level(cv)
    boost = calculate_education_boost(info)
    assert 6.0 <= boost <= 9.0  # Bachelor gets ~8 points


def test_education_boost_diploma():
    cv = "National Diploma in IT"
    info = detect_education_level(cv)
    boost = calculate_education_boost(info)
    assert 3.0 <= boost <= 6.0  # Diploma gets ~5 points


def test_no_education_no_boost():
    boost = calculate_education_boost(None)
    assert boost == 0.0
