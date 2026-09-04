"""
Sync a career model's skill weights from the real O*NET Web Services API.

This is a REAL, working client for O*NET's documented REST API
(https://services.onetcenter.org/reference). It is not run automatically -
you run it yourself, locally, with your own free O*NET Web Services
credentials. Nothing in the main application calls out to O*NET at
request time; this is an offline data-refresh tool.

--------------------------------------------------------------------------
HOW TO GET FREE O*NET CREDENTIALS
--------------------------------------------------------------------------
1. Go to https://services.onetcenter.org/developer/signup and register
   (free, no cost, no credit card).
2. You'll receive a username/password for HTTP Basic Auth against the API.
3. Set them as environment variables before running this script:

       export ONET_USERNAME=your_username
       export ONET_PASSWORD=your_password

--------------------------------------------------------------------------
USAGE
--------------------------------------------------------------------------
    cd python-engine
    export ONET_USERNAME=...
    export ONET_PASSWORD=...
    python3 -m scripts.onet_sync --soc-code 15-1221.00 --career-slug ml-engineer

This will:
  1. Call the O*NET "skills" and "knowledge" detail endpoints for the given
     SOC code, which return real, numeric 0-100 Importance scores.
  2. Call the "technology_skills" summary endpoint to see which specific
     tools/technologies (e.g. Docker, TensorFlow) are listed for that
     occupation, including "Hot Technology" flags.
  3. Map whatever it can onto our skill taxonomy (app/nlp/taxonomy.py)
     using each skill's aliases.
  4. Write/update app/data/career_models/<career-slug>.json with the real
     numeric values, tagging each updated skill "source": "onet_api" and
     stamping "last_synced" with the current UTC time.

Skills in our taxonomy that O*NET has no direct match for keep their
existing weight untouched (still tagged "benchmark_estimate") rather than
being guessed at or dropped - you'll see a summary of what was and wasn't
matched printed at the end.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import requests

ONET_BASE_URL = "https://services.onetcenter.org/ws/online/occupations"
DATA_DIR = Path(__file__).resolve().parent.parent / "app" / "data" / "career_models"

# Reuse the taxonomy's aliases so O*NET element names map onto our skills
# without duplicating the alias list here.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.nlp.taxonomy import SKILL_TAXONOMY  # noqa: E402


def _onet_auth() -> tuple:
    username = os.environ.get("ONET_USERNAME")
    password = os.environ.get("ONET_PASSWORD")
    if not username or not password:
        raise SystemExit(
            "Missing ONET_USERNAME / ONET_PASSWORD environment variables.\n"
            "Sign up for free at https://services.onetcenter.org/developer/signup "
            "and set them before running this script."
        )
    return (username, password)


def _fetch_onet(endpoint: str, soc_code: str) -> dict:
    url = f"{ONET_BASE_URL}/{soc_code}/{endpoint}"
    resp = requests.get(
        url,
        auth=_onet_auth(),
        headers={"Accept": "application/json"},
        timeout=20,
    )
    resp.raise_for_status()
    return resp.json()


def fetch_skills(soc_code: str) -> List[dict]:
    """Real numeric Importance scores (0-100) per O*NET Skill element."""
    data = _fetch_onet("details/skills", soc_code)
    return data.get("element", [])


def fetch_knowledge(soc_code: str) -> List[dict]:
    """Real numeric Importance scores (0-100) per O*NET Knowledge element."""
    data = _fetch_onet("details/knowledge", soc_code)
    return data.get("element", [])


def fetch_technology_skills(soc_code: str) -> List[dict]:
    """Specific tools/technologies (e.g. 'Docker', 'TensorFlow') with a
    'hot_technology' flag - no numeric importance score, but a strong
    presence/relevance signal."""
    data = _fetch_onet("summary/technology_skills", soc_code)
    return data.get("category", [])


def _match_taxonomy_slug(onet_name: str) -> Optional[str]:
    """Best-effort match of an O*NET element/technology name onto our
    taxonomy slug, via canonical name + aliases."""
    name_lower = onet_name.lower()
    for skill in SKILL_TAXONOMY:
        candidates = [skill.canonical.lower()] + [a.lower() for a in skill.aliases]
        for candidate in candidates:
            if candidate in name_lower or name_lower in candidate:
                return skill.slug
    return None


def sync_career_model(soc_code: str, career_slug: str, career_name: str, description: str) -> dict:
    print(f"Fetching O*NET Skills for {soc_code}...")
    skills = fetch_skills(soc_code)
    print(f"Fetching O*NET Knowledge for {soc_code}...")
    knowledge = fetch_knowledge(soc_code)
    print(f"Fetching O*NET Technology Skills for {soc_code}...")
    tech_categories = fetch_technology_skills(soc_code)

    # Load existing career file if present, so unmatched skills keep their
    # current (benchmark) weights instead of being lost.
    existing_path = DATA_DIR / f"{career_slug}.json"
    existing_weights: Dict[str, dict] = {}
    if existing_path.exists():
        with open(existing_path, "r", encoding="utf-8") as f:
            existing = json.load(f)
        for s in existing.get("skills", []):
            existing_weights[s["skill_slug"]] = s

    onet_confirmed_slugs = set()
    for category in tech_categories:
        for example in category.get("example", []):
            slug = _match_taxonomy_slug(example.get("name", ""))
            if slug:
                onet_confirmed_slugs.add(slug)

    matched, unmatched = 0, 0
    for element in skills + knowledge:
        slug = _match_taxonomy_slug(element.get("name", ""))
        score = element.get("score", {})
        value = score.get("value")
        if slug and value is not None:
            importance = round(value / 100.0, 3)
            existing_weights[slug] = {
                "skill_slug": slug,
                "market_frequency": existing_weights.get(slug, {}).get("market_frequency", importance),
                "market_importance": importance,
                "source": "onet_api",
                "onet_confirmed": True,
            }
            matched += 1
        elif not slug:
            unmatched += 1

    for slug in onet_confirmed_slugs:
        if slug in existing_weights:
            existing_weights[slug]["onet_confirmed"] = True
        else:
            # No numeric Importance score is available for this skill (it
            # only showed up in the Technology Skills report, not the
            # Skills/Knowledge scales), and there's no prior weight to
            # keep. Create a placeholder entry rather than silently
            # dropping a confirmed-relevant skill - it's tagged clearly
            # as unscored so it doesn't masquerade as verified data.
            existing_weights[slug] = {
                "skill_slug": slug,
                "market_frequency": 0.5,
                "market_importance": 0.5,
                "source": "onet_technology_list_only",
                "onet_confirmed": True,
            }

    now = datetime.now(timezone.utc).isoformat()
    output = {
        "slug": career_slug,
        "name": career_name,
        "description": description,
        "onet": {
            "soc_code": soc_code,
            "occupation_title": career_name,
            "note": (
                "Numeric Importance scores in this file were pulled directly "
                "from the O*NET Web Services API."
            ),
            "source_url": f"https://www.onetonline.org/link/summary/{soc_code}",
            "last_synced": now,
            "sync_method": "onet_web_services_api",
        },
        "skills": list(existing_weights.values()),
    }

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(existing_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"\nMatched {matched} O*NET elements onto taxonomy skills.")
    print(f"{unmatched} O*NET elements had no taxonomy match (left untouched).")
    print(f"{len(onet_confirmed_slugs)} taxonomy skills confirmed via Technology Skills report.")
    print(f"Wrote {existing_path}")
    return output


def main():
    parser = argparse.ArgumentParser(description="Sync a career model from the O*NET API.")
    parser.add_argument("--soc-code", required=True, help="O*NET-SOC code, e.g. 15-1221.00")
    parser.add_argument("--career-slug", required=True, help="Career slug, e.g. ml-engineer")
    parser.add_argument("--career-name", default=None, help="Display name, e.g. 'ML Engineer'")
    parser.add_argument("--description", default="", help="Short career description")
    args = parser.parse_args()

    sync_career_model(
        soc_code=args.soc_code,
        career_slug=args.career_slug,
        career_name=args.career_name or args.career_slug.replace("-", " ").title(),
        description=args.description,
    )


if __name__ == "__main__":
    main()
