"""
Import career models from the O*NET Database bulk download - no API
credentials required, unlike scripts/onet_sync.py.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

DATA_DIR = Path(__file__).resolve().parent.parent / "app" / "data" / "career_models"

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.nlp.taxonomy import SKILL_TAXONOMY  # noqa: E402


def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text.strip("-")


def _match_taxonomy_slug(onet_name: str) -> Optional[str]:
    name_lower = onet_name.lower()
    for skill in SKILL_TAXONOMY:
        candidates = [skill.canonical.lower()] + [a.lower() for a in skill.aliases]
        for candidate in candidates:
            if candidate in name_lower or name_lower in candidate:
                return skill.slug
    return None


def _read_tsv_optional(path: Path) -> List[dict]:
    if not path.exists():
        return []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter="\t")
        return list(reader)


def list_occupations(db_dir: Path) -> None:
    rows = _read_tsv_optional(db_dir / "Occupation Data.txt")
    for row in rows:
        print(f"{row['O*NET-SOC Code']}\t{row['Title']}")
    print(f"\n{len(rows)} occupations total.")


def import_all_careers(db_dir: Path) -> None:
    print("Reading O*NET database files into memory...")
    occupations = _read_tsv_optional(db_dir / "Occupation Data.txt")
    if not occupations:
        raise SystemExit(f"Occupation Data.txt not found in {db_dir}")

    # Support O*NET 31.0+ filenames as well as older O*NET filenames
    skills_rows = (
        _read_tsv_optional(db_dir / "Essential Skills.txt")
        + _read_tsv_optional(db_dir / "Transferable Skills.txt")
        + _read_tsv_optional(db_dir / "Skills.txt")
        + _read_tsv_optional(db_dir / "Knowledge.txt")
        + _read_tsv_optional(db_dir / "Abilities.txt")
    )

    tech_rows_all = (
        _read_tsv_optional(db_dir / "Software Skills.txt")
        + _read_tsv_optional(db_dir / "Technology Skills.txt")
    )

    # Pre-group rows by SOC code
    skills_by_soc: Dict[str, List[dict]] = {}
    for r in skills_rows:

        # In O*NET 31.0, scale could be IM, or value can be in Data Value / Importance
        soc = r.get("O*NET-SOC Code", "")
        if soc:
            skills_by_soc.setdefault(soc, []).append(r)

    tech_by_soc: Dict[str, List[dict]] = {}
    for r in tech_rows_all:
        soc = r.get("O*NET-SOC Code", "")
        if soc:
            tech_by_soc.setdefault(soc, []).append(r)

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    imported_count = 0
    now = datetime.now(timezone.utc).isoformat()

    print(f"Importing {len(occupations)} occupations into {DATA_DIR}...")

    used_slugs = set()

    for occ in occupations:
        soc_code = occ["O*NET-SOC Code"]
        occupation_title = occ["Title"]
        description = occ.get("Description", "")

        base_slug = _slugify(occupation_title)
        if not base_slug:
            continue
        career_slug = base_slug
        counter = 1
        while career_slug in used_slugs:
            career_slug = f"{base_slug}-{counter}"
            counter += 1
        used_slugs.add(career_slug)

        s_rows = skills_by_soc.get(soc_code, [])
        t_rows = tech_by_soc.get(soc_code, [])

        existing_weights: Dict[str, dict] = {}
        onet_confirmed_slugs = set()

        for row in t_rows:
            tech_name = row.get("Example", "") or row.get("Software", "")
            slug = _match_taxonomy_slug(tech_name)
            if slug:
                onet_confirmed_slugs.add(slug)

        for row in s_rows:
            elem_name = row.get("Element Name", "") or row.get("Skill", "")
            slug = _match_taxonomy_slug(elem_name)
            try:
                val_str = row.get("Data Value", "") or row.get("Importance", "") or "3.0"
                value = float(val_str)
            except (TypeError, ValueError):
                value = 3.0

            if slug:
                # Normalize 1-5 scale or default to 0.5
                importance = round(max(0.0, min(1.0, (value - 1) / 4)), 3) if value > 1 else 0.5
                existing_weights[slug] = {
                    "skill_slug": slug,
                    "market_frequency": importance,
                    "market_importance": importance,
                    "source": "onet_bulk_database",
                    "onet_confirmed": True,
                }

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

        output = {
            "slug": career_slug,
            "name": occupation_title,
            "description": description,
            "onet": {
                "soc_code": soc_code,
                "occupation_title": occupation_title,
                "note": "Imported from O*NET 31.0 Database.",
                "source_url": f"https://www.onetonline.org/link/summary/{soc_code}",
                "last_synced": now,
                "sync_method": "onet_bulk_database",
            },
            "skills": list(existing_weights.values()),
        }

        file_path = DATA_DIR / f"{career_slug}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)

        imported_count += 1

    print(f"\n🎉 Successfully imported all {imported_count} occupations into {DATA_DIR}!")


def main():
    parser = argparse.ArgumentParser(description="Import career models from the O*NET bulk database download.")
    parser.add_argument("--db-dir", required=True, help="Path to the unzipped O*NET database folder")
    parser.add_argument("--list-occupations", action="store_true", help="List all SOC codes/titles and exit")
    parser.add_argument("--import-all", action="store_true", help="Import all 1000+ occupations from O*NET at once")
    parser.add_argument("--soc-code", help="O*NET-SOC code, e.g. 15-1221.00")
    parser.add_argument("--career-slug", help="Career slug, e.g. ml-engineer")
    parser.add_argument("--career-name", default=None, help="Display name")
    parser.add_argument("--description", default="", help="Short career description")
    args = parser.parse_args()

    db_dir = Path(args.db_dir).expanduser()

    if args.list_occupations:
        list_occupations(db_dir)
        return

    if args.import_all:
        import_all_careers(db_dir)
        return


if __name__ == "__main__":
    main()
