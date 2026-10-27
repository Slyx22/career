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


def _read_tsv(path: Path) -> List[dict]:
    """Like _read_tsv_optional, but a missing file is a hard error."""
    if not path.exists():
        raise SystemExit(f"{path.name} not found in {path.parent} - is --db-dir the unzipped O*NET text folder?")
    return _read_tsv_optional(path)


def _importance_rows_for_soc(rows: List[dict], soc_code: str) -> List[dict]:
    """Rows for one occupation on the Importance (IM, 1-5) scale only.

    Skills/Knowledge/Abilities files also carry Level (LV, 0-7) rows for the
    same elements; mixing them in lets a Level value overwrite the Importance
    score. Rows with no Scale ID column (newer O*NET layouts) are kept.
    """
    return [
        r for r in rows
        if r.get("O*NET-SOC Code") == soc_code and r.get("Scale ID", "IM") in ("IM", "")
    ]


def _skill_rows(db_dir: Path) -> List[dict]:
    # Support O*NET 31.0+ filenames as well as older O*NET filenames
    return (
        _read_tsv_optional(db_dir / "Essential Skills.txt")
        + _read_tsv_optional(db_dir / "Transferable Skills.txt")
        + _read_tsv_optional(db_dir / "Skills.txt")
        + _read_tsv_optional(db_dir / "Knowledge.txt")
        + _read_tsv_optional(db_dir / "Abilities.txt")
    )


def _tech_rows(db_dir: Path) -> List[dict]:
    return (
        _read_tsv_optional(db_dir / "Software Skills.txt")
        + _read_tsv_optional(db_dir / "Technology Skills.txt")
    )


def _build_career_model(
    soc_code: str,
    occupation_title: str,
    career_slug: str,
    description: str,
    importance_rows: List[dict],
    tech_rows: List[dict],
    now: str,
) -> dict:
    existing_weights: Dict[str, dict] = {}

    for row in importance_rows:
        elem_name = row.get("Element Name", "") or row.get("Skill", "")
        slug = _match_taxonomy_slug(elem_name)
        if not slug:
            continue
        try:
            value = float(row.get("Data Value", "") or row.get("Importance", "") or "3.0")
        except (TypeError, ValueError):
            value = 3.0
        # Normalize the 1-5 Importance scale to 0-1
        importance = round(max(0.0, min(1.0, (value - 1) / 4)), 3)
        prev = existing_weights.get(slug)
        if prev and prev["market_importance"] >= importance:
            continue  # several O*NET elements can map to one skill; keep the strongest
        existing_weights[slug] = {
            "skill_slug": slug,
            "market_frequency": importance,
            "market_importance": importance,
            "source": "onet_bulk_database",
            "onet_confirmed": True,
        }

    for row in tech_rows:
        slug = _match_taxonomy_slug(row.get("Example", "") or row.get("Software", ""))
        if slug and slug not in existing_weights:
            existing_weights[slug] = {
                "skill_slug": slug,
                "market_frequency": 0.5,
                "market_importance": 0.5,
                "source": "onet_technology_list_only",
                "onet_confirmed": True,
            }

    return {
        "slug": career_slug,
        "name": occupation_title,
        "description": description,
        "onet": {
            "soc_code": soc_code,
            "occupation_title": occupation_title,
            "note": "Imported from the O*NET Database bulk download.",
            "source_url": f"https://www.onetonline.org/link/summary/{soc_code}",
            "last_synced": now,
            "sync_method": "onet_bulk_database",
        },
        "skills": list(existing_weights.values()),
    }


def _write_model(model: dict) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    file_path = DATA_DIR / f"{model['slug']}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(model, f, indent=2)
    return file_path


def import_career_model(
    db_dir: Path,
    soc_code: str,
    career_slug: str,
    career_name: Optional[str] = None,
    description: str = "",
) -> dict:
    """Import a single occupation by SOC code and write its career model."""
    occupations = _read_tsv(db_dir / "Occupation Data.txt")
    occ = next((o for o in occupations if o.get("O*NET-SOC Code") == soc_code), None)
    if occ is None:
        raise SystemExit(f"SOC code {soc_code} not found in Occupation Data.txt")

    model = _build_career_model(
        soc_code=soc_code,
        occupation_title=career_name or occ["Title"],
        career_slug=career_slug,
        description=description or occ.get("Description", ""),
        importance_rows=_importance_rows_for_soc(_skill_rows(db_dir), soc_code),
        tech_rows=[r for r in _tech_rows(db_dir) if r.get("O*NET-SOC Code") == soc_code],
        now=datetime.now(timezone.utc).isoformat(),
    )
    path = _write_model(model)
    print(f"Imported {soc_code} -> {path} ({len(model['skills'])} skills)")
    return model


def list_occupations(db_dir: Path) -> None:
    rows = _read_tsv_optional(db_dir / "Occupation Data.txt")
    for row in rows:
        print(f"{row['O*NET-SOC Code']}\t{row['Title']}")
    print(f"\n{len(rows)} occupations total.")


def import_all_careers(db_dir: Path) -> None:
    print("Reading O*NET database files into memory...")
    occupations = _read_tsv(db_dir / "Occupation Data.txt")

    # Pre-group rows by SOC code (Importance scale only for skills)
    skills_by_soc: Dict[str, List[dict]] = {}
    for r in _skill_rows(db_dir):
        soc = r.get("O*NET-SOC Code", "")
        if soc and r.get("Scale ID", "IM") in ("IM", ""):
            skills_by_soc.setdefault(soc, []).append(r)

    tech_by_soc: Dict[str, List[dict]] = {}
    for r in _tech_rows(db_dir):
        soc = r.get("O*NET-SOC Code", "")
        if soc:
            tech_by_soc.setdefault(soc, []).append(r)

    now = datetime.now(timezone.utc).isoformat()
    print(f"Importing {len(occupations)} occupations into {DATA_DIR}...")

    used_slugs = set()
    imported_count = 0
    for occ in occupations:
        soc_code = occ["O*NET-SOC Code"]
        base_slug = _slugify(occ["Title"])
        if not base_slug:
            continue
        career_slug = base_slug
        counter = 1
        while career_slug in used_slugs:
            career_slug = f"{base_slug}-{counter}"
            counter += 1
        used_slugs.add(career_slug)

        model = _build_career_model(
            soc_code=soc_code,
            occupation_title=occ["Title"],
            career_slug=career_slug,
            description=occ.get("Description", ""),
            importance_rows=skills_by_soc.get(soc_code, []),
            tech_rows=tech_by_soc.get(soc_code, []),
            now=now,
        )
        _write_model(model)
        imported_count += 1

    print(f"\nSuccessfully imported {imported_count} occupations into {DATA_DIR}")


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

    if args.soc_code and args.career_slug:
        import_career_model(db_dir, args.soc_code, args.career_slug, args.career_name, args.description)
        return

    parser.error("use --list-occupations, --import-all, or --soc-code with --career-slug")


if __name__ == "__main__":
    main()
