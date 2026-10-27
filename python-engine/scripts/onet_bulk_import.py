"""
Import career models from the free O*NET Database bulk download (no API
key, no cost). Download the "text" version of the database from
https://www.onetcenter.org/database.html, unzip it, and run:

    python scripts/onet_bulk_import.py --db-dir "path/to/db_xx_x_text" --import-all

How skills are matched (exact, not guessed):
  * O*NET Skills and Knowledge rows are mapped through the reviewed table
    in app/nlp/onet_elements.py, by Element ID (or exact Element Name).
  * O*NET Technology Skills examples (e.g. "Microsoft Excel", "Python")
    are matched to software/tool skills in our taxonomy by whole words
    only, and only to software categories, never to soft skills.
  * Only elements O*NET rates as at least "important" (3.0 or more on its
    1-5 Importance scale) are used, so each career is described by what
    actually matters for it.
  * Occupations with fewer than MIN_SKILLS usable skills are skipped
    (mostly the "All Other" catch-all occupations that O*NET doesn't rate).

The O*NET Database is (c) USDOL/ETA and licensed under CC BY 4.0.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

DATA_DIR = Path(__file__).resolve().parent.parent / "app" / "data" / "career_models"
REPORT_PATH = Path(__file__).resolve().parent / "last_import_report.json"

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app.nlp.onet_elements import KNOW, element_for  # noqa: E402
from app.nlp.taxonomy import SKILL_TAXONOMY  # noqa: E402

SYNC_METHOD = "onet_bulk_database"

# Importance 3.0 on O*NET's 1-5 scale = "important" = 0.5 normalized.
MIN_IMPORTANCE = 0.5
MAX_SKILL_ELEMENTS = 12
MAX_KNOWLEDGE_ELEMENTS = 8
MAX_TECH_SKILLS = 5
MIN_SKILLS = 5

# Only these taxonomy categories can be matched from Technology Skills.
TECH_CATEGORIES = {
    "Programming", "Data", "Machine Learning", "Deep Learning", "Deployment", "Cloud",
    "MLOps", "Databases", "Statistics", "Software Engineering", "Workplace software",
}
# Conceptual skills that a software product name should never imply.
TECH_EXCLUDE = {
    "machine_learning", "supervised_learning", "unsupervised_learning", "model_evaluation",
    "feature_engineering", "deep_learning", "neural_networks", "data_preprocessing",
    "data_pipelines", "probability", "hypothesis_testing", "model_monitoring",
    "experiment_tracking", "model_deployment", "data_structures_algorithms", "system_design",
    "object_oriented_design", "unit_testing", "agile_scrum", "cicd",
}


def _slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text.strip("-")


def _build_tech_patterns() -> List[Tuple[re.Pattern, str, int]]:
    patterns = []
    for skill in SKILL_TAXONOMY:
        if skill.category not in TECH_CATEGORIES or skill.slug in TECH_EXCLUDE:
            continue
        for term in [skill.canonical] + list(skill.aliases):
            term = term.lower().strip()
            # Very short aliases ("py", "ts", "js") match inside unrelated
            # names; real product names are always longer.
            if len(term) < 3 and term not in ("c#", "r"):
                continue
            pat = re.compile(r"(?<![a-z0-9])" + re.escape(term) + r"(?![a-z0-9+#])")
            patterns.append((pat, skill.slug, len(term)))
    # Longest term first, so "microsoft power bi" wins over "power bi".
    patterns.sort(key=lambda p: p[2], reverse=True)
    return patterns


_TECH_PATTERNS = _build_tech_patterns()


def _match_tech_slug(example: str) -> Optional[str]:
    name = (example or "").lower().strip()
    if not name:
        return None
    if name == "r":
        return "r_language"
    for pat, slug, term_len in _TECH_PATTERNS:
        if term_len == 1:
            continue  # single letters only match by the exact check above
        if pat.search(name):
            return slug
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

    Skills/Knowledge files also carry Level (LV, 0-7) rows for the same
    elements; mixing them in would let a Level value overwrite the
    Importance score. Rows with no Scale ID column are kept.
    """
    return [
        r for r in rows
        if r.get("O*NET-SOC Code") == soc_code and r.get("Scale ID", "IM") in ("IM", "")
    ]


def _skill_rows(db_dir: Path) -> List[dict]:
    rows: List[dict] = []
    for name in ("Skills.txt", "Knowledge.txt", "Essential Skills.txt", "Transferable Skills.txt"):
        rows += _read_tsv_optional(db_dir / name)
    return rows


def _tech_rows(db_dir: Path) -> List[dict]:
    return (
        _read_tsv_optional(db_dir / "Technology Skills.txt")
        + _read_tsv_optional(db_dir / "Software Skills.txt")
    )


def _tech_example(row: dict) -> str:
    """The software/tool name in a Technology (or Software) Skills row.
    Column names have varied between O*NET releases."""
    for key in ("Workplace Example", "Example", "Software", "Software Name", "Technology", "Tool"):
        if row.get(key):
            return row[key]
    return ""


def _is_yes(value: Optional[str]) -> bool:
    return (value or "").strip().upper() in ("Y", "YES", "TRUE", "1")


def _build_career_model(
    soc_code: str,
    occupation_title: str,
    career_slug: str,
    description: str,
    importance_rows: List[dict],
    tech_rows: List[dict],
    now: str,
    unmapped: Optional[Dict[str, int]] = None,
) -> dict:
    # --- Skills and Knowledge: exact element mapping ---
    by_slug: Dict[str, dict] = {}
    for row in importance_rows:
        if _is_yes(row.get("Recommend Suppress")):
            continue
        elem_id = row.get("Element ID", "")
        elem_name = row.get("Element Name", "") or row.get("Skill", "")
        element = element_for(elem_id, elem_name)
        if element is None:
            if unmapped is not None and elem_name:
                unmapped[elem_name] = unmapped.get(elem_name, 0) + 1
            continue
        try:
            value = float(row.get("Data Value", "") or "")
        except (TypeError, ValueError):
            continue
        importance = round(max(0.0, min(1.0, (value - 1) / 4)), 3)
        prev = by_slug.get(element.slug)
        if prev and prev["market_importance"] >= importance:
            continue  # Mathematics is both a Skill and a Knowledge area; keep the higher
        by_slug[element.slug] = {
            "skill_slug": element.slug,
            "market_frequency": importance,
            "market_importance": importance,
            "source": SYNC_METHOD,
            "onet_confirmed": True,
            "_knowledge": element.category == KNOW,
            "_onet_element": elem_name,
        }

    ranked = sorted(by_slug.values(), key=lambda s: s["market_importance"], reverse=True)
    important = [s for s in ranked if s["market_importance"] >= MIN_IMPORTANCE]
    chosen = (
        [s for s in important if not s["_knowledge"]][:MAX_SKILL_ELEMENTS]
        + [s for s in important if s["_knowledge"]][:MAX_KNOWLEDGE_ELEMENTS]
    )
    if len(chosen) < MIN_SKILLS:
        # Fall back to the top-rated elements so a sparsely rated
        # occupation still gets a usable model.
        chosen = [s for s in ranked if s["market_importance"] > 0][:MIN_SKILLS]

    skills = []
    for s in sorted(chosen, key=lambda s: s["market_importance"], reverse=True):
        s = dict(s)
        s.pop("_knowledge", None)
        skills.append(s)

    # --- Technology Skills: whole-word match to software skills only ---
    tech: Dict[str, dict] = {}
    for row in tech_rows:
        slug = _match_tech_slug(_tech_example(row))
        if not slug or any(s["skill_slug"] == slug for s in skills):
            continue
        hot = _is_yes(row.get("Hot Technology"))
        in_demand = _is_yes(row.get("In Demand"))
        weight = 0.55 if (hot and in_demand) else 0.45 if (hot or in_demand) else 0.35
        if slug not in tech or tech[slug]["market_importance"] < weight:
            tech[slug] = {
                "skill_slug": slug,
                "market_frequency": weight,
                "market_importance": weight,
                "source": "onet_technology_skills",
                "onet_confirmed": True,
                "_onet_element": row.get("Example", ""),
            }
    skills += sorted(tech.values(), key=lambda s: s["market_importance"], reverse=True)[:MAX_TECH_SKILLS]

    return {
        "slug": career_slug,
        "name": occupation_title,
        "description": description,
        "onet": {
            "soc_code": soc_code,
            "occupation_title": occupation_title,
            "note": "Imported from the O*NET Database (USDOL/ETA, CC BY 4.0) with exact skill mapping.",
            "source_url": f"https://www.onetonline.org/link/summary/{soc_code}",
            "last_synced": now,
            "sync_method": SYNC_METHOD,
        },
        "skills": [_public_skill(s) for s in skills],
    }


def _public_skill(s: dict) -> dict:
    """Drop internal keys; keep which O*NET element each skill came from,
    so anyone can audit the mapping in the JSON file."""
    out = {k: v for k, v in s.items() if not k.startswith("_")}
    out["onet_element"] = s.get("_onet_element", "")
    return out


def _write_model(model: dict) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    file_path = DATA_DIR / f"{model['slug']}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(model, f, indent=2)
        f.write("\n")
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


def _remove_previous_bulk_imports() -> int:
    """Delete career files written by earlier bulk imports, so careers that
    are now skipped don't linger with old data. Hand-made careers (any
    other sync_method) are kept."""
    removed = 0
    if not DATA_DIR.exists():
        return 0
    for path in DATA_DIR.glob("*.json"):
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue
        if (data.get("onet") or {}).get("sync_method") == SYNC_METHOD:
            path.unlink()
            removed += 1
    return removed


def import_all_careers(db_dir: Path) -> dict:
    print("Reading O*NET database files into memory...")
    occupations = _read_tsv(db_dir / "Occupation Data.txt")

    skills_by_soc: Dict[str, List[dict]] = {}
    for r in _skill_rows(db_dir):
        soc = r.get("O*NET-SOC Code", "")
        if soc and r.get("Scale ID", "IM") in ("IM", ""):
            skills_by_soc.setdefault(soc, []).append(r)

    tech_rows_all = _tech_rows(db_dir)
    tech_columns = list(tech_rows_all[0].keys()) if tech_rows_all else []
    tech_unmatched: Dict[str, int] = {}
    tech_matched: Dict[str, int] = {}
    for r in tech_rows_all:
        name = _tech_example(r)
        bucket = tech_matched if _match_tech_slug(name) else tech_unmatched
        bucket[name] = bucket.get(name, 0) + 1
    tech_by_soc: Dict[str, List[dict]] = {}
    for r in tech_rows_all:
        soc = r.get("O*NET-SOC Code", "")
        if soc:
            tech_by_soc.setdefault(soc, []).append(r)

    removed = _remove_previous_bulk_imports()
    # Hand-made careers that remain keep their slugs.
    protected = {p.stem for p in DATA_DIR.glob("*.json")} if DATA_DIR.exists() else set()

    now = datetime.now(timezone.utc).isoformat()
    print(f"Importing {len(occupations)} occupations into {DATA_DIR} (removed {removed} old files)...")

    used_slugs = set(protected)
    unmapped: Dict[str, int] = {}
    imported, skipped = 0, []
    for occ in occupations:
        soc_code = occ["O*NET-SOC Code"]
        base_slug = _slugify(occ["Title"])
        if not base_slug:
            continue
        model = _build_career_model(
            soc_code=soc_code,
            occupation_title=occ["Title"],
            career_slug=base_slug,
            description=occ.get("Description", ""),
            importance_rows=skills_by_soc.get(soc_code, []),
            tech_rows=tech_by_soc.get(soc_code, []),
            now=now,
            unmapped=unmapped,
        )
        if len(model["skills"]) < MIN_SKILLS:
            skipped.append(f"{soc_code} {occ['Title']}")
            continue
        career_slug = base_slug
        counter = 1
        while career_slug in used_slugs:
            career_slug = f"{base_slug}-{counter}"
            counter += 1
        used_slugs.add(career_slug)
        model["slug"] = career_slug
        _write_model(model)
        imported += 1

    report = {
        "generated_at": now,
        "db_dir": db_dir.name,
        "occupations_in_database": len(occupations),
        "careers_written": imported,
        "careers_skipped_too_few_rated_skills": len(skipped),
        "skipped_examples": skipped[:25],
        "unmapped_onet_elements": dict(sorted(unmapped.items(), key=lambda kv: -kv[1])),
        "technology_rows": len(tech_rows_all),
        "technology_columns": tech_columns,
        "technology_matched_top": dict(sorted(tech_matched.items(), key=lambda kv: -kv[1])[:40]),
        "technology_unmatched_top": dict(sorted(tech_unmatched.items(), key=lambda kv: -kv[1])[:60]),
    }
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
        f.write("\n")
    print(f"\nImported {imported} careers, skipped {len(skipped)}. Report: {REPORT_PATH}")
    if unmapped:
        print(f"Unmapped O*NET elements (check app/nlp/onet_elements.py): {list(unmapped)[:10]}")
    return report


def main():
    parser = argparse.ArgumentParser(description="Import career models from the O*NET bulk database download.")
    parser.add_argument("--db-dir", required=True, help="Path to the unzipped O*NET database folder")
    parser.add_argument("--list-occupations", action="store_true", help="List all SOC codes/titles and exit")
    parser.add_argument("--import-all", action="store_true", help="Import all occupations from O*NET at once")
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

    parser.print_help()


if __name__ == "__main__":
    main()
