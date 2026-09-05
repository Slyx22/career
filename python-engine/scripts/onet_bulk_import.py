"""
Import career models from the O*NET Database bulk download - no API
credentials required, unlike scripts/onet_sync.py.

--------------------------------------------------------------------------
WHAT THIS IS
--------------------------------------------------------------------------
O*NET publishes their ENTIRE database as a free zip file, updated a few
times a year, containing every occupation's Skills, Knowledge, and
Technology Skills ratings as plain tab-delimited text files. No signup,
no API key, no rate limits - just a direct download.

This is the better option if you want to add several careers at once, or
don't want to register for O*NET Web Services API credentials. Use
scripts/onet_sync.py instead if you only need one or two careers and
already have API credentials.

--------------------------------------------------------------------------
HOW TO GET THE DATABASE (you do this step yourself - see README)
--------------------------------------------------------------------------
1. Go to https://www.onetcenter.org/database.html#individual-files
2. Under "Text Format", download the latest full database zip
   (e.g. "db_29_1_text.zip" - the exact version number changes over time).
3. Unzip it somewhere on your machine, e.g. ~/Downloads/db_29_1_text/
4. You should see files including:
     Occupation Data.txt
     Skills.txt
     Knowledge.txt
     Technology Skills.txt

--------------------------------------------------------------------------
USAGE
--------------------------------------------------------------------------
    cd python-engine
    python3 -m scripts.onet_bulk_import \\
        --db-dir ~/Downloads/db_29_1_text \\
        --soc-code 15-1221.00 \\
        --career-slug ml-engineer

Add --list-occupations to just browse what's in the database first:

    python3 -m scripts.onet_bulk_import --db-dir ~/Downloads/db_29_1_text --list-occupations

This will:
  1. Read "Occupation Data.txt" to confirm the SOC code and get the
     official occupation title.
  2. Read "Skills.txt" and "Knowledge.txt" (Scale ID "IM" = Importance,
     rated 1-5) for that SOC code, converting to our 0-1 scale.
  3. Read "Technology Skills.txt" for that SOC code to find specific
     tools/technologies and their "Hot Technology" flag.
  4. Map everything onto our skill taxonomy (app/nlp/taxonomy.py) using
     each skill's aliases (same matching logic as scripts/onet_sync.py).
  5. Write/update app/data/career_models/<career-slug>.json, tagging
     matched skills "source": "onet_bulk_database" with real numeric
     Importance values, and unmatched taxonomy skills left untouched.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

DATA_DIR = Path(__file__).resolve().parent.parent / "app" / "data" / "career_models"

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.nlp.taxonomy import SKILL_TAXONOMY  # noqa: E402


def _match_taxonomy_slug(onet_name: str) -> Optional[str]:
    name_lower = onet_name.lower()
    for skill in SKILL_TAXONOMY:
        candidates = [skill.canonical.lower()] + [a.lower() for a in skill.aliases]
        for candidate in candidates:
            if candidate in name_lower or name_lower in candidate:
                return skill.slug
    return None


def _read_tsv(path: Path) -> List[dict]:
    if not path.exists():
        raise SystemExit(
            f"Expected file not found: {path}\n"
            "Check --db-dir points at the unzipped O*NET database folder "
            "(it should directly contain files like 'Skills.txt')."
        )
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        return list(reader)


def list_occupations(db_dir: Path) -> None:
    rows = _read_tsv(db_dir / "Occupation Data.txt")
    for row in rows:
        print(f"{row['O*NET-SOC Code']}\t{row['Title']}")
    print(f"\n{len(rows)} occupations total.")


def _importance_rows_for_soc(rows: List[dict], soc_code: str) -> List[dict]:
    """Filter Skills.txt / Knowledge.txt rows to a SOC code and the
    Importance ('IM') scale only - these files also contain Level ('LV')
    rows on a different 0-7 scale, which we don't want mixed in."""
    return [
        r
        for r in rows
        if r.get("O*NET-SOC Code") == soc_code and r.get("Scale ID") == "IM"
    ]


def _technology_rows_for_soc(rows: List[dict], soc_code: str) -> List[dict]:
    return [r for r in rows if r.get("O*NET-SOC Code") == soc_code]


def import_career_model(
    db_dir: Path, soc_code: str, career_slug: str, career_name: Optional[str], description: str
) -> dict:
    occupations = _read_tsv(db_dir / "Occupation Data.txt")
    match = next((o for o in occupations if o["O*NET-SOC Code"] == soc_code), None)
    if not match:
        raise SystemExit(
            f"SOC code {soc_code} not found in Occupation Data.txt. "
            "Run with --list-occupations to see what's available."
        )
    occupation_title = match["Title"]

    skills_rows = _importance_rows_for_soc(_read_tsv(db_dir / "Skills.txt"), soc_code)
    knowledge_rows = _importance_rows_for_soc(_read_tsv(db_dir / "Knowledge.txt"), soc_code)

    tech_path = db_dir / "Technology Skills.txt"
    tech_rows = _technology_rows_for_soc(_read_tsv(tech_path), soc_code) if tech_path.exists() else []

    # Load existing career file if present, so unmatched skills keep
    # their current (benchmark) weights instead of being lost.
    existing_path = DATA_DIR / f"{career_slug}.json"
    existing_weights: Dict[str, dict] = {}
    if existing_path.exists():
        with open(existing_path, "r", encoding="utf-8") as f:
            existing = json.load(f)
        for s in existing.get("skills", []):
            existing_weights[s["skill_slug"]] = s

    onet_confirmed_slugs = set()
    for row in tech_rows:
        slug = _match_taxonomy_slug(row.get("Example", ""))
        if slug:
            onet_confirmed_slugs.add(slug)

    matched, unmatched = 0, 0
    for row in skills_rows + knowledge_rows:
        slug = _match_taxonomy_slug(row.get("Element Name", ""))
        try:
            value = float(row.get("Data Value", ""))
        except (TypeError, ValueError):
            value = None
        if slug and value is not None:
            # O*NET Importance scale is 1-5; normalize to 0-1.
            importance = round(max(0.0, min(1.0, (value - 1) / 4)), 3)
            existing_weights[slug] = {
                "skill_slug": slug,
                "market_frequency": existing_weights.get(slug, {}).get("market_frequency", importance),
                "market_importance": importance,
                "source": "onet_bulk_database",
                "onet_confirmed": True,
            }
            matched += 1
        elif not slug:
            unmatched += 1

    for slug in onet_confirmed_slugs:
        if slug in existing_weights:
            existing_weights[slug]["onet_confirmed"] = True
        else:
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
        "name": career_name or occupation_title,
        "description": description,
        "onet": {
            "soc_code": soc_code,
            "occupation_title": occupation_title,
            "note": (
                "Numeric Importance scores in this file were parsed directly "
                "from the official O*NET Database bulk download (Skills.txt / "
                "Knowledge.txt, Importance scale)."
            ),
            "source_url": f"https://www.onetonline.org/link/summary/{soc_code}",
            "last_synced": now,
            "sync_method": "onet_bulk_database",
        },
        "skills": list(existing_weights.values()),
    }

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(existing_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)

    print(f"Occupation: {occupation_title} ({soc_code})")
    print(f"Matched {matched} O*NET Skills/Knowledge elements onto taxonomy skills.")
    print(f"{unmatched} elements had no taxonomy match (left untouched).")
    print(f"{len(onet_confirmed_slugs)} taxonomy skills confirmed via Technology Skills report.")
    print(f"Wrote {existing_path}")
    return output


def main():
    parser = argparse.ArgumentParser(description="Import a career model from the O*NET bulk database download.")
    parser.add_argument("--db-dir", required=True, help="Path to the unzipped O*NET database folder")
    parser.add_argument("--list-occupations", action="store_true", help="List all SOC codes/titles and exit")
    parser.add_argument("--soc-code", help="O*NET-SOC code, e.g. 15-1221.00")
    parser.add_argument("--career-slug", help="Career slug, e.g. ml-engineer")
    parser.add_argument("--career-name", default=None, help="Display name (defaults to the O*NET occupation title)")
    parser.add_argument("--description", default="", help="Short career description")
    args = parser.parse_args()

    db_dir = Path(args.db_dir).expanduser()

    if args.list_occupations:
        list_occupations(db_dir)
        return

    if not args.soc_code or not args.career_slug:
        parser.error("--soc-code and --career-slug are required unless --list-occupations is used.")

    import_career_model(
        db_dir=db_dir,
        soc_code=args.soc_code,
        career_slug=args.career_slug,
        career_name=args.career_name,
        description=args.description,
    )


if __name__ == "__main__":
    main()
