"""
Evidence-aware skill extraction.

Rather than a simple keyword match, this module tries to answer, for
each taxonomy skill:

  presence        - is the skill mentioned at all?
  evidence_score  - how strongly is it demonstrated (0-1)?
  depth_score     - is it merely mentioned, used, or owned end-to-end (0-1)?
  recency_score   - how recent is the most relevant mention (0-1)?
  matched_snippets - short supporting quotes (kept internal, for future UI)

This intentionally avoids requiring a large NLP model download so the
service runs fully offline in local development. Sentence splitting and
verb/phrase heuristics are regex-based. Swapping in spaCy or a
sentence-transformers similarity model later is a drop-in upgrade behind
this same function's return shape.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from app.extractors.cv_extractor import ExtractedCV, extract_years_mentioned
from app.nlp.taxonomy import SKILL_TAXONOMY, Skill

CURRENT_YEAR = 2026

# Verbs/phrases that suggest the skill was actually *applied*, not just listed.
STRONG_EVIDENCE_PATTERNS = [
    r"\bbuilt\b", r"\bbuild\b", r"\bbuilding\b", r"\bdeveloped\b", r"\bdeploy(ed|ing)?\b",
    r"\bimplemented\b", r"\bdesigned\b", r"\barchitected\b", r"\bled\b", r"\btrained\b",
    r"\boptimi[sz]ed\b", r"\bshipped\b", r"\bdelivered\b", r"\bcreated\b", r"\bmaintained\b",
    r"\bautomated\b", r"\bscaled\b", r"\bowned\b", r"\bproduction\b", r"\brefactored\b",
    r"\bintegrated\b", r"\blaunched\b",
]

# Phrases that suggest weak / superficial exposure only.
WEAK_EVIDENCE_PATTERNS = [
    r"\bfamiliar with\b", r"\bexposure to\b", r"\bbasic knowledge of\b",
    r"\bintroductory\b", r"\bcoursework\b", r"\blearning\b", r"\bstudying\b",
    r"\bbeginner\b",
]

SECTION_WEIGHT = {
    "experience": 1.0,
    "projects": 0.9,
    "summary": 0.6,
    "skills": 0.35,
    "education": 0.5,
    "other": 0.55,
}


@dataclass
class SkillEvidence:
    skill: Skill
    present: bool = False
    mentions: int = 0
    evidence_score: float = 0.0   # 0-1: how strongly demonstrated
    depth_score: float = 0.0      # 0-1: applied vs merely mentioned
    recency_score: float = 0.0    # 0-1: how recent
    snippets: List[str] = field(default_factory=list)


def _build_pattern(skill: Skill) -> re.Pattern:
    terms = [skill.canonical] + list(skill.aliases)
    terms = sorted(set(t.lower() for t in terms), key=len, reverse=True)
    escaped = [re.escape(t) for t in terms]
    pattern = r"(?<![a-z0-9])(" + "|".join(escaped) + r")(?![a-z0-9])"
    return re.compile(pattern, re.IGNORECASE)


_SKILL_PATTERNS = {s.slug: _build_pattern(s) for s in SKILL_TAXONOMY}

SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+|\n+")

# Explicit self-rated proficiency levels, as commonly written in CVs like
# "Python - Moderate" or "SQL: Beginner". This is a very common real-world
# CV pattern (skills listed with a self-declared level) that plain
# verb-based evidence detection completely misses - a bullet like
# "SQL - BEGINNER" contains no verb at all, so without this explicit
# check it would default to the neutral 0.5 depth score, the same as a
# bare skill mention with no self-assessment at all.
PROFICIENCY_LEVELS = {
    "beginner": 0.20,
    "basic": 0.25,
    "novice": 0.20,
    "moderate": 0.45,
    "average": 0.45,
    "intermediate": 0.55,
    "competent": 0.60,
    "good": 0.65,
    "proficient": 0.75,
    "very good": 0.80,
    "advanced": 0.85,
    "excellent": 0.90,
    "expert": 0.95,
}
# Sorted longest-first so "very good" matches before "good" would.
_PROFICIENCY_PATTERN = re.compile(
    r"[-:–—]\s*(" + "|".join(re.escape(k) for k in sorted(PROFICIENCY_LEVELS, key=len, reverse=True)) + r")\b",
    re.IGNORECASE,
)


def _detect_explicit_proficiency(text: str, match_end: int, window: int = 30) -> Optional[float]:
    """
    Looks just after a skill mention (e.g. right after "SQL" in
    "SQL - BEGINNER") for an explicit self-rated proficiency level, and
    returns the corresponding depth score if found. This is treated as
    stronger signal than the verb-based heuristic, since it's the
    person's own direct claim about their level, not an inference from
    phrasing.
    """
    snippet = text[match_end:match_end + window]
    m = _PROFICIENCY_PATTERN.match(snippet.lstrip() if snippet[:1] in " \t" else snippet)
    if not m:
        # Also allow a little leading whitespace before the dash.
        stripped = snippet.lstrip(" \t")
        m = _PROFICIENCY_PATTERN.match(stripped)
    if not m:
        return None
    return PROFICIENCY_LEVELS[m.group(1).lower()]


def _sentence_spans(text: str) -> List[tuple]:
    """Return (start, end) offsets for each sentence in text."""
    spans = []
    pos = 0
    for part in SENTENCE_SPLIT.split(text):
        if not part:
            continue
        idx = text.find(part, pos)
        if idx == -1:
            idx = pos
        spans.append((idx, idx + len(part)))
        pos = idx + len(part)
    return spans


def _sentence_context(text: str, spans: List[tuple], start: int, end: int, pad_chars: int = 40) -> str:
    """
    Return the sentence(s) actually containing the match, not a fixed
    character window. This matters: a fixed window can pull evidence
    verbs from an *adjacent, unrelated* sentence into a skill's context
    (e.g. "Built a to-do app. Also familiar with Kubernetes." must NOT
    credit Kubernetes with the word "Built").
    """
    for lo, hi in spans:
        if lo <= start < hi or lo < end <= hi:
            # A small amount of padding is still useful for short
            # fragments (e.g. bullet points with no terminal punctuation),
            # but we never cross into a different sentence's verbs.
            return text[lo:hi].replace("\n", " ").strip()
    # Fallback: no sentence boundary detected (e.g. a single unbroken
    # line) - use a tight window instead of the whole sentence list.
    lo = max(0, start - pad_chars)
    hi = min(len(text), end + pad_chars)
    return text[lo:hi].replace("\n", " ").strip()


def _score_context(context: str) -> Dict[str, float]:
    ctx = context.lower()
    strong_hits = sum(1 for p in STRONG_EVIDENCE_PATTERNS if re.search(p, ctx))
    weak_hits = sum(1 for p in WEAK_EVIDENCE_PATTERNS if re.search(p, ctx))

    if strong_hits >= 2:
        depth = 1.0
    elif strong_hits == 1:
        depth = 0.75
    elif weak_hits >= 1:
        depth = 0.25
    else:
        depth = 0.5  # neutral mention, e.g. plain skills-list entry

    return {"depth": depth, "strong_hits": strong_hits, "weak_hits": weak_hits}


def _recency_score_for_years(years: List[int]) -> float:
    if not years:
        return 0.6  # unknown recency: neutral-ish, don't punish CVs without dates
    most_recent = max(years)
    delta = max(0, CURRENT_YEAR - most_recent)
    if delta <= 1:
        return 1.0
    if delta <= 3:
        return 0.8
    if delta <= 5:
        return 0.55
    if delta <= 8:
        return 0.3
    return 0.15


def extract_skill_evidence(cv: ExtractedCV) -> Dict[str, SkillEvidence]:
    text = cv.raw_text
    doc_years = extract_years_mentioned(text)
    sentence_spans = _sentence_spans(text)
    results: Dict[str, SkillEvidence] = {}

    # Figure out which section each character offset roughly falls into,
    # using section text membership (cheap approximation - good enough for
    # weighting purposes without a full layout parser).
    section_spans = []
    for section_name, section_text in cv.sections.items():
        if section_text.strip():
            section_spans.append((section_name, section_text))

    for skill in SKILL_TAXONOMY:
        pattern = _SKILL_PATTERNS[skill.slug]
        evidence = SkillEvidence(skill=skill)
        matches = list(pattern.finditer(text))
        if not matches:
            results[skill.slug] = evidence
            continue

        evidence.present = True
        evidence.mentions = len(matches)

        best_combined = 0.0
        depth_values = []
        explicit_level_values = []
        recency_values = []

        for m in matches[:8]:  # cap for performance/no runaway CVs
            context = _sentence_context(text, sentence_spans, m.start(), m.end())
            scores = _score_context(context)
            depth_for_mention = scores["depth"]

            explicit_level = _detect_explicit_proficiency(text, m.end())
            if explicit_level is not None:
                # A direct "Skill - Level" self-rating is more reliable
                # than an inferred verb-based guess for this mention.
                depth_for_mention = explicit_level
                explicit_level_values.append(explicit_level)

            depth_values.append(depth_for_mention)

            local_years = extract_years_mentioned(context)
            years_for_recency = local_years or doc_years
            recency_values.append(_recency_score_for_years(years_for_recency))

            # Determine which section this match likely belongs to.
            section_weight = 0.55
            probe = context[:60].strip()
            for section_name, section_text in section_spans:
                if section_text and probe and probe in section_text:
                    section_weight = SECTION_WEIGHT.get(section_name, 0.55)
                    break

            combined = (0.5 * depth_for_mention + 0.5 * section_weight)
            if combined > best_combined:
                best_combined = combined
                if len(evidence.snippets) < 2:
                    evidence.snippets.append(context)

        evidence.depth_score = max(explicit_level_values) if explicit_level_values else (
            max(depth_values) if depth_values else 0.5
        )
        evidence.recency_score = max(recency_values) if recency_values else 0.6

        # Evidence score blends: presence baseline + mention frequency +
        # depth + best contextual weight, capped at 1.0.
        frequency_bonus = min(0.15, 0.04 * (evidence.mentions - 1))
        evidence.evidence_score = min(
            1.0, 0.45 + frequency_bonus + 0.35 * evidence.depth_score + 0.2 * best_combined
        )

        results[skill.slug] = evidence

    return results
