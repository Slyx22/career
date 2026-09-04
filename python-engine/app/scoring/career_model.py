"""
Career models define, per career, which skills matter and how much.

Career models are now DATA, not Python code: each career lives in its own
JSON file under app/data/career_models/*.json. Adding a new career later
is a matter of dropping in a new JSON file with the same shape - no code
changes required here.

IMPORTANT - what "market_frequency" / "market_importance" mean:
Each skill weight is tagged with a `source`:
  - "onet_api"            : a real, numeric Importance score pulled from
                             the O*NET Web Services API (0-100 scale,
                             normalized to 0-1 here). Run
                             scripts/onet_sync.py with your own free
                             O*NET Web Services credentials to populate
                             these.
  - "benchmark_estimate"   : NOT yet sourced from O*NET or any verified
                             job-market dataset. This is an initial
                             estimate seeded by the product team. Do not
                             present these to users as verified market
                             statistics - the frontend/API label them
                             accordingly.
Additionally, `onet_confirmed` is true when the *skill itself* (not
necessarily its exact importance number) was independently confirmed to
be listed in O*NET's public Technology Skills report for the mapped
occupation - see each career JSON's "onet" block for the SOC code and
source URL.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "career_models"


@dataclass(frozen=True)
class CareerSkillWeight:
    skill_slug: str
    market_frequency: float  # 0-1
    market_importance: float  # 0-1
    source: str = "benchmark_estimate"  # "onet_api" | "benchmark_estimate"
    onet_confirmed: bool = False


@dataclass(frozen=True)
class OnetInfo:
    soc_code: Optional[str]
    occupation_title: Optional[str]
    note: Optional[str]
    source_url: Optional[str]
    last_synced: Optional[str]
    sync_method: Optional[str]


@dataclass(frozen=True)
class CareerModel:
    slug: str
    name: str
    description: str
    skills: List[CareerSkillWeight]
    onet: Optional[OnetInfo] = None

    @property
    def is_fully_onet_sourced(self) -> bool:
        return bool(self.skills) and all(s.source == "onet_api" for s in self.skills)

    @property
    def onet_confirmed_skill_count(self) -> int:
        return sum(1 for s in self.skills if s.onet_confirmed)


def _load_career_file(path: Path) -> CareerModel:
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    onet_raw = raw.get("onet")
    onet = (
        OnetInfo(
            soc_code=onet_raw.get("soc_code"),
            occupation_title=onet_raw.get("occupation_title"),
            note=onet_raw.get("note"),
            source_url=onet_raw.get("source_url"),
            last_synced=onet_raw.get("last_synced"),
            sync_method=onet_raw.get("sync_method"),
        )
        if onet_raw
        else None
    )

    skills = [
        CareerSkillWeight(
            skill_slug=s["skill_slug"],
            market_frequency=s["market_frequency"],
            market_importance=s["market_importance"],
            source=s.get("source", "benchmark_estimate"),
            onet_confirmed=s.get("onet_confirmed", False),
        )
        for s in raw.get("skills", [])
    ]

    return CareerModel(
        slug=raw["slug"],
        name=raw["name"],
        description=raw.get("description", ""),
        skills=skills,
        onet=onet,
    )


@lru_cache(maxsize=1)
def _load_all_career_models() -> Dict[str, CareerModel]:
    models: Dict[str, CareerModel] = {}
    if not DATA_DIR.exists():
        return models
    for path in sorted(DATA_DIR.glob("*.json")):
        model = _load_career_file(path)
        models[model.slug] = model
    return models


def get_career_model(slug: str) -> CareerModel:
    models = _load_all_career_models()
    if slug not in models:
        raise KeyError(f"Unknown career: {slug}")
    return models[slug]


def list_careers() -> List[Dict]:
    models = _load_all_career_models()
    return [
        {"slug": m.slug, "name": m.name, "description": m.description}
        for m in models.values()
    ]


def clear_career_model_cache() -> None:
    """Used by scripts/tests after writing/updating a career JSON file."""
    _load_all_career_models.cache_clear()
