"""
South African job titles (OFO 2021) linked to the careers the engine
scores against. Built by scripts/build_sa_occupations.py into
app/data/sa_occupations.json.

The SA title is what users pick and what appears on results and
certificates; the linked O*NET career supplies the skills that are scored.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional

SA_FILE = Path(__file__).resolve().parent.parent / "data" / "sa_occupations.json"


@lru_cache(maxsize=1)
def _load() -> List[dict]:
    if not SA_FILE.exists():
        return []
    with open(SA_FILE, encoding="utf-8") as f:
        return json.load(f).get("occupations", [])


def sa_titles_for_listing(listed_slugs: set) -> List[Dict]:
    """Compact list for the career search box: t=title, a=other names,
    s=career slug. Only titles whose career is listed in the app."""
    return [
        {"t": o["title"], "a": o.get("aliases", []), "s": o["career_slug"]}
        for o in _load()
        if o["career_slug"] in listed_slugs
    ]


@lru_cache(maxsize=1)
def _titles_by_slug() -> Dict[str, Dict[str, str]]:
    out: Dict[str, Dict[str, str]] = {}
    for o in _load():
        names = out.setdefault(o["career_slug"], {})
        names[o["title"].lower()] = o["title"]
    return out


def resolve_sa_title(career_slug: str, title: Optional[str]) -> Optional[str]:
    """Return the official SA title if `title` is one linked to this career,
    else None. Stops arbitrary text being printed on certificates."""
    if not title:
        return None
    return _titles_by_slug().get(career_slug, {}).get(title.strip().lower())
