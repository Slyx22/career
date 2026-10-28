"""
Score bands. One place defines them; the website mirrors these values in
frontend/lib/bands.ts.

A band describes how well the CV matches the occupation's skills. It is
not an employer endorsement (see Terms, section 2).
"""
from __future__ import annotations

from typing import Optional

# (minimum score, key, label)
BANDS = (
    (85, "excellent", "Excellent match"),
    (70, "strong", "Strong match"),
    (50, "developing", "Developing"),
    (0, "early", "Early stage"),
)

# Certificates at or above this score carry the recognition seal.
SEAL_THRESHOLD = 70


def band_for(score: Optional[int]) -> tuple[str, str]:
    s = int(score or 0)
    for minimum, key, label in BANDS:
        if s >= minimum:
            return key, label
    return BANDS[-1][1], BANDS[-1][2]


def has_seal(score: Optional[int]) -> bool:
    return int(score or 0) >= SEAL_THRESHOLD


def points_to_seal(score: Optional[int]) -> int:
    return max(0, SEAL_THRESHOLD - int(score or 0))
