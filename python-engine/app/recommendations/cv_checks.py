"""
Rule-based checks on the CV itself, beyond skills. No AI is used.

  weak_lines        job lines that describe a duty with no result or number
  cv_basics         whether the CV has the parts employers look for first
                    (structure only: we never ask for personal details)
  privacy_warnings  personal details a CV doesn't need and that are a
                    privacy risk (ID number, date of birth, race, ...).
                    Only the TYPE of detail is reported: the value itself is
                    never copied, stored or shown back.
  work_link_step    for careers where one piece of work online is normal
                    (design, writing, software, research...), a suggestion
                    to link ONE relevant piece, only if the CV has no link

Everything here is about what can be added to or changed on the CV today.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional

from app.extractors.cv_extractor import ExtractedCV

# --------------------------------------------------------------- weak lines

_WEAK_OPENERS = re.compile(
    r"^\W*(responsible for|duties (?:included|include|were)|duties:|tasks (?:included|include)|"
    r"helped (?:with|to)|assisted (?:with|in)|in charge of|worked (?:at|as|in|on)|"
    r"involved in|tasked with|my role was|job description)\b",
    re.IGNORECASE,
)


def weak_lines(cv: ExtractedCV) -> List[str]:
    """For each experience line that states a duty with no number or result,
    the weak opening phrase it uses (our fixed wording, e.g. "Responsible
    for"), never the person's own words: CV wording is not kept."""
    source = cv.sections.get("experience") or ""
    found: List[str] = []
    for raw in source.splitlines():
        line = raw.strip(" \t•·-–—*")
        words = line.split()
        if not 3 <= len(words) <= 30:
            continue
        if re.search(r"\d", line):
            continue
        m = _WEAK_OPENERS.search(line)
        if m:
            found.append(m.group(1).rstrip(":").capitalize())
    return found


def experience_has_numbers(cv: ExtractedCV) -> Optional[bool]:
    """None when there's no experience section to judge."""
    exp = cv.sections.get("experience") or ""
    if len(exp.split()) < 25:
        return None
    # Years alone ("2021 - 2023") aren't results.
    without_years = re.sub(r"\b(19|20)\d{2}\b", "", exp)
    return bool(re.search(r"\d", without_years))


# --------------------------------------------------------------- CV basics

@dataclass(frozen=True)
class Basic:
    key: str
    label: str
    ok: bool
    fix: str


_LANG_HEADING = re.compile(r"^\s*(languages?|language proficiency|languages spoken)\s*:?\s*$", re.I | re.M)
_LANG_NAMES = re.compile(
    r"\b(english|afrikaans|isizulu|zulu|isixhosa|xhosa|sesotho|sepedi|setswana|tswana|xitsonga|tsonga|"
    r"siswati|swati|tshivenda|venda|isindebele|ndebele|french|portuguese|german|spanish)\b",
    re.I,
)


def cv_basics(cv: ExtractedCV) -> List[Basic]:
    text = cv.raw_text
    words = len(text.split())
    years = re.findall(r"\b(?:19|20)\d{2}\b", text)
    has_lang = bool(_LANG_HEADING.search(text)) or len(set(m.lower() for m in _LANG_NAMES.findall(text))) >= 2
    basics = [
        Basic("skills_section", "A Skills section", bool((cv.sections.get("skills") or "").strip()),
              "Add a Skills heading that lists your main skills and the software or tools you use."),
        Basic("experience_section", "Work experience", bool((cv.sections.get("experience") or "").strip())
              or bool((cv.sections.get("projects") or "").strip()),
              "Add an Experience heading with each job (including part-time, holiday or volunteer work), "
              "your role and what you did."),
        Basic("education_section", "Education", bool((cv.sections.get("education") or "").strip()),
              "Add an Education heading with your qualifications, where you got them and the year."),
        Basic("dates", "Dates on jobs and studies", len(years) >= 2,
              "Add the month and year you started and finished each job and qualification."),
        Basic("languages", "Languages you speak", has_lang,
              "Add a Languages heading listing the languages you speak and how well."),
        Basic("length", "A length employers will read", words <= 1400,
              "Your CV is long. Keep it to about two pages: cut older or unrelated detail, and keep each "
              "job to the lines that matter for this career."),
    ]
    return basics


# --------------------------------------------------------------- privacy

def _valid_sa_id(digits: str) -> bool:
    """13 digits, a real YYMMDD date and a valid Luhn check digit."""
    if len(digits) != 13 or not digits.isdigit():
        return False
    mm, dd = int(digits[2:4]), int(digits[4:6])
    if not (1 <= mm <= 12 and 1 <= dd <= 31):
        return False
    total = 0
    for i, ch in enumerate(reversed(digits)):
        n = int(ch)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0


_PRIVACY_PATTERNS: Dict[str, re.Pattern] = {
    "date_of_birth": re.compile(r"\b(date of birth|d\.?\s?o\.?\s?b\.?|birth ?date|born on)\b|\bage\s*:\s*\d", re.I),
    "race": re.compile(r"\b(race|ethnicity|ethnic group|population group)\s*:", re.I),
    "gender": re.compile(r"\b(gender|sex)\s*:", re.I),
    "marital_status": re.compile(r"\bmarital status\b", re.I),
    "religion": re.compile(r"\b(religion|religious affiliation|denomination)\s*:", re.I),
    "health": re.compile(r"\b(health status|health\s*:|state of health)\b", re.I),
    "dependants": re.compile(r"\b(dependants|dependents|number of children)\s*:", re.I),
    "criminal_record": re.compile(r"\bcriminal record\b", re.I),
    "id_label": re.compile(r"\b(id (?:no|number)|identity number|i\.d\. number|id\s*:)", re.I),
}

_PRIVACY_LABELS = {
    "id_number": "ID number",
    "date_of_birth": "date of birth or age",
    "race": "race or population group",
    "gender": "gender",
    "marital_status": "marital status",
    "religion": "religion",
    "health": "health status",
    "dependants": "children or dependants",
    "criminal_record": "criminal record status",
}


def privacy_warnings(cv: ExtractedCV) -> List[Dict[str, str]]:
    """Personal details the CV includes that employers don't need. Only the
    kind of detail is returned, never its value."""
    text = cv.raw_text
    keys: List[str] = []
    id_found = any(_valid_sa_id(m) for m in re.findall(r"(?<!\d)(\d{13})(?!\d)", re.sub(r"(?<=\d)[ -](?=\d)", "", text)))
    if id_found or _PRIVACY_PATTERNS["id_label"].search(text):
        keys.append("id_number")
    for key, pattern in _PRIVACY_PATTERNS.items():
        if key == "id_label":
            continue
        if pattern.search(text):
            keys.append(key)
    out = []
    for key in keys:
        out.append({"key": key, "label": _PRIVACY_LABELS[key]})
    return out


PRIVACY_ADVICE = (
    "Employers don't need these to judge whether you can do the job. Leaving them on your CV is a privacy "
    "risk, because CVs get forwarded and saved in many places (and an ID number can be used for fraud), and "
    "details like age, race, religion or marital status can open the door to unfair discrimination. Consider "
    "removing them. If an employer needs any of them later, for example to verify your identity, they'll ask."
)


# --------------------------------------------------------------- work link

# Careers where linking one relevant piece of work is normal, and what that
# piece usually is. Matched on the O*NET SOC code. Everyone else gets no
# link suggestion, so no one is told to link work their field doesn't show.
_WORK_LINK = (
    ("27-1", "a design, illustration or other creative piece you made"),
    ("27-3", "an article, script or piece of writing you published"),
    ("27-4", "a photo, video or recording you produced"),
    ("27-2", "a recording or video of a performance"),
    ("15-", "a project you built or contributed to (for example its code repository or live site)"),
    ("17-1011", "a drawing or plan you produced"),
    ("17-1012", "a design or plan you produced"),
    ("17-301", "a drawing you produced"),
    ("19-", "a report, paper or poster you contributed to"),
    ("11-2", "a campaign or piece of content you worked on"),
    ("13-1161", "a research report you worked on"),
    ("25-1", "a paper or course material you published"),
)

_URL = re.compile(r"(https?://|www\.|\b[a-z0-9-]+\.(?:com|co\.za|org|io|dev|net|me)/)", re.I)


def work_link_step(soc_code: Optional[str], cv: ExtractedCV) -> Optional[str]:
    if not soc_code or _URL.search(cv.raw_text):
        return None
    for prefix, piece in _WORK_LINK:
        if soc_code.startswith(prefix):
            return (
                f"If one piece of your work is online, such as {piece}, add its link next to the job or "
                "project it belongs to. Link one relevant piece rather than a whole profile, and only work "
                "you're happy for an employer to see."
            )
    return None


# --------------------------------------------------------------- summary

def cv_steps(cv: ExtractedCV) -> List[str]:
    """CV-level suggestions, most useful first, for the recommendations list."""
    steps: List[str] = []
    weak = weak_lines(cv)
    if weak:
        openers = list(dict.fromkeys(weak))[:2]
        quoted = " or ".join(f"“{o}”" for o in openers)
        if len(weak) == 1:
            lead = f"1 job line starts with {quoted}, which describes a duty"
        else:
            lead = f"{len(weak)} job lines start with {quoted}, which describe duties"
        steps.append(
            f"{lead} rather than what you achieved. "
            "Reword these to say what the result was, with a number where you can: how many, how much "
            "or how often."
        )
    elif experience_has_numbers(cv) is False:
        steps.append(
            "None of your job entries include a number. Where you can, add how many, how much or how often "
            "(customers served, stock counted, targets met), because employers look for scale."
        )
    for b in cv_basics(cv):
        if not b.ok and b.key in ("skills_section", "experience_section", "education_section", "dates"):
            steps.append(b.fix)
            break
    return steps
