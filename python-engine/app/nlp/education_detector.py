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
]

DIPLOMA_PATTERNS = [
    r"\bdiploma\b",
    r"\bhnd\b",
    r"\bnational diploma\b",
    r"\badvanced diploma\b",
    r"\btechnician diploma\b",
]

CERTIFICATE_PATTERNS = [
    r"\bcertificate\b",
    r"\bcertified\b",
    r"\bcertification\b",
    r"\bbootcamp\b",
    r"\btraining certificate\b",
    r"\bprofessional certificate\b",
]

ASSOCIATE_PATTERNS = [
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
