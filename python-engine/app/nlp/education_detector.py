"""
Education level detection from CV text.

Detects mentions of degrees, diplomas, certifications, and educational
attainment levels to provide contextual boost to readiness scores.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class EducationLevel(Enum):
    """Detected education level (from highest to lowest relevant qualification)."""
    DOCTORAL = "doctoral"  # PhD, EdD, MD, DDS, etc.
    MASTERS = "masters"  # MSc, MBA, MA, MEng, etc.
    BACHELOR = "bachelor"  # BSc, BA, BEng, etc.
    DIPLOMA = "diploma"  # HND, National Diploma, etc.
    CERTIFICATE = "certificate"  # Professional certificates, bootcamps
    ASSOCIATE = "associate"  # Associate degree
    UNKNOWN = "unknown"


@dataclass
class EducationInfo:
    """Detected education information."""
    level: EducationLevel
    field: Optional[str]  # e.g., "Computer Science", "Business Administration"
    institution: Optional[str]  # e.g., "University of Cambridge"
    confidence: float  # 0-1, how confident we are in this detection


# Regex patterns for degree detection
DOCTORAL_PATTERNS = [
    r"\bphd\b",
    r"\bph\.d\b",
    r"\bed\.d\b",
    r"\bmd\b",
    r"\bdds\b",
    r"\bdvm\b",
    r"\bdoctorate\b",
    r"\bdoctor of",
]

MASTERS_PATTERNS = [
    r"\bmsc\b",
    r"\bm\.sc\b",
    r"\bma\b",
    r"\bm\.a\b",
    r"\bmba\b",
    r"\bm\.b\.a\b",
    r"\bmeng\b",
    r"\bm\.eng\b",
    r"\bllm\b",
    r"\bm\.law\b",
    r"\bmaster'?s\b",
    r"\bmaster degree\b",
]

BACHELOR_PATTERNS = [
    r"\bbsc\b",
    r"\bb\.sc\b",
    r"\bba\b",
    r"\bb\.a\b",
    r"\bbeng\b",
    r"\bb\.eng\b",
    r"\bllb\b",
    r"\bb\.law\b",
    r"\bbachelor'?s?\b",
    r"\bbachelor degree\b",
    r"\bundergraduate degree\b",
    # Common South African bachelor's degree abbreviations
    r"\bb\.?com\b",
    r"\bb\.?compt\b",
    r"\bb\.?acc\b",
    r"\bb\.ed\b",
    r"\bb\.?tech\b",
    r"\bb\.?pharm\b",
    r"\bb\.?cur\b",
    r"\bmbchb\b",
    r"\bb\.?bus\.?sci\b",
    r"\bb\.?soc\.?sci\b",
    r"\bb\.?admin\b",
    # South African NQF levels 7-8 (bachelor's, advanced diploma, honours)
    r"\bhonours\b",
    r"\bhons\b",
    r"\bnqf\s*(level\s*)?[78]\b",
]

DIPLOMA_PATTERNS = [
    r"\bdiploma\b",
    r"\bhnd\b",
    r"\bnational diploma\b",
    r"\badvanced diploma\b",
    r"\btechnician diploma\b",
    # South African: N6 / National N Diploma, NQF level 6, artisan trade test
    r"\bn6\b",
    r"\bnational n diploma\b",
    r"\bnqf\s*(level\s*)?6\b",
    r"\btrade test\b",
    r"\bred seal\b",
]

CERTIFICATE_PATTERNS = [
    r"\bcertificate\b",
    r"\bcertified\b",
    r"\bcertification\b",
    r"\bbootcamp\b",
    r"\btraining certificate\b",
    r"\bprofessional certificate\b",
    # South African learnerships / occupational certificates (NQF 1-4)
    r"\blearnership\b",
    r"\bnational certificate\b",
    r"\bnqf\s*(level\s*)?[1-4]\b",
]

ASSOCIATE_PATTERNS = [
    # South African higher certificate / N4-N5 / NQF level 5
    r"\bhigher certificate\b",
    r"\bn[45]\b",
    r"\bnqf\s*(level\s*)?5\b",
    r"\bassociate'?s?\b",
    r"\bassociate degree\b",
    r"\bassociate'?s degree\b",
]


def detect_education_level(cv_text: str) -> Optional[EducationInfo]:
    """
    Detect education level from CV text.

    Args:
        cv_text: Raw CV text to analyze

    Returns:
        EducationInfo with detected level, or None if no education detected
    """
    text_lower = cv_text.lower()

    # Check in order of highest to lowest degree
    patterns_by_level = [
        (EducationLevel.DOCTORAL, DOCTORAL_PATTERNS, 0.95),
        (EducationLevel.MASTERS, MASTERS_PATTERNS, 0.92),
        (EducationLevel.BACHELOR, BACHELOR_PATTERNS, 0.90),
        (EducationLevel.DIPLOMA, DIPLOMA_PATTERNS, 0.85),
        (EducationLevel.ASSOCIATE, ASSOCIATE_PATTERNS, 0.85),
        (EducationLevel.CERTIFICATE, CERTIFICATE_PATTERNS, 0.75),
    ]

    for level, patterns, confidence in patterns_by_level:
        for pattern in patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                # Try to extract field of study
                field = _extract_field_of_study(cv_text, text_lower)
                institution = _extract_institution(cv_text, text_lower)

                return EducationInfo(
                    level=level,
                    field=field,
                    institution=institution,
                    confidence=confidence,
                )

    return None


def _extract_field_of_study(cv_text: str, cv_text_lower: str) -> Optional[str]:
    """
    Try to extract field of study (e.g., "Computer Science", "Business Administration").

    Looks for patterns like "BSc in Computer Science" or "degree in Engineering".
    """
    # Pattern: degree keyword followed by "in" and field name
    pattern = r"(?:in|of)\s+([A-Z][a-zA-Z\s&]+)"
    matches = re.finditer(pattern, cv_text)

    for match in matches:
        field = match.group(1).strip()
        # Filter out common false positives
        if field and len(field) < 60 and field.lower() not in ["the", "a", "and", "or"]:
            return field

    return None


def _extract_institution(cv_text: str, cv_text_lower: str) -> Optional[str]:
    """
    Try to extract institution name (e.g., "University of Cambridge", "MIT").

    Looks for common university name patterns.
    """
    patterns = [
        r"(?:university|college|institute|school)\s+of\s+([A-Z][a-zA-Z\s&]+)",
        r"([A-Z][a-zA-Z\s&]*?)\s+(?:university|college|institute|school)",
    ]

    for pattern in patterns:
        matches = re.finditer(pattern, cv_text)
        for match in matches:
            institution = match.group(1).strip()
            if institution and len(institution) < 100:
                return institution

    return None


def calculate_education_boost(education_info: Optional[EducationInfo]) -> float:
    """
    Calculate readiness score boost based on education level.

    Boost values are conservative and represent additional points out of 100.
    Higher education levels and stronger confidence = higher boost.

    Args:
        education_info: Detected education information

    Returns:
        Score boost (0-15 points) to add to readiness score
    """
    if not education_info:
        return 0.0

    # Base boost by level
    level_boost = {
        EducationLevel.DOCTORAL: 15.0,
        EducationLevel.MASTERS: 12.0,
        EducationLevel.BACHELOR: 8.0,
        EducationLevel.DIPLOMA: 5.0,
        EducationLevel.ASSOCIATE: 3.0,
        EducationLevel.CERTIFICATE: 2.0,
        EducationLevel.UNKNOWN: 0.0,
    }

    base = level_boost.get(education_info.level, 0.0)

    # Apply confidence multiplier
    boosted = base * education_info.confidence

    return boosted
