"""
Build app/data/sa_occupations.json: South African job titles (OFO 2021)
linked to the O*NET-based careers the engine scores against.

Chain:  OFO occupation (6-digit)  ->  OFO unit group (4-digit)
        ->  ISCO-08 unit group     (matched by title; OFO is built on ISCO-08
                                     but renumbers some groups, e.g. trades)
        ->  2010 SOC codes         (BLS ISCO-08 <-> 2010 SOC crosswalk)
        ->  2018 SOC codes         (BLS 2010 -> 2018 SOC crosswalk)
        ->  O*NET careers          (career files' onet.soc_code)
Within those candidate careers, the one whose name best matches the SA
title (and its OFO specialisations) is chosen. If the chain gives no
candidates, a strong direct title match is used instead, otherwise the SA
title is left out rather than guessed.

Source files (all free) live in app/data/sources/ and are fetched by the
"Fetch South African occupation sources" GitHub workflow:
  ofo_2021.xlsx                     - OFO 2021 (via HWSETA)
  isco08_soc2010_crosswalk.xls      - U.S. BLS
  soc2010_to_soc2018_crosswalk.xlsx - U.S. BLS
  onet_job_titles.tsv               - O*NET job titles (USDOL/ETA, CC BY 4.0)

Run:  python scripts/build_sa_occupations.py   (needs openpyxl and xlrd)
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple

ROOT = Path(__file__).resolve().parent.parent
SOURCES = ROOT / "app" / "data" / "sources"
CAREERS_DIR = ROOT / "app" / "data" / "career_models"
OUT = ROOT / "app" / "data" / "sa_occupations.json"

STOP = {
    "and", "or", "the", "of", "a", "an", "n", "e", "c", "not", "elsewhere", "classified",
    "related", "other", "in", "nec", "all", "for", "to", "except", "including", "n/a",
}
# Words that differ between SA/UK and US spelling or naming.
SYNONYMS = {
    "paediatric": "pediatric", "paediatrics": "pediatric", "anaesthetist": "anesthesiologist",
    "anaesthesiologist": "anesthesiologist", "orthopaedic": "orthopedic", "gynaecologist": "gynecologist",
    "labour": "labor", "organisation": "organization", "programme": "program", "centre": "center",
    "draughtsperson": "drafter", "draughtsman": "drafter", "lorry": "truck", "chemist": "chemist",
    "attorney": "lawyer", "advocate": "lawyer", "educator": "teacher", "practitioner": "practitioner",
    "salesperson": "sales", "shopkeeper": "retail", "bricklayer": "brickmason", "turner": "machinist",
}


# South African phrases with a US equivalent (school phases, etc.).
PHRASES = {
    "foundation phase": "kindergarten elementary",
    "intermediate phase": "elementary",
    "senior phase": "middle",
    "fet phase": "secondary",
    "grade r": "kindergarten",
    "contact centre": "call center customer service",
    "call centre": "call center customer service",
    "enrolled nurse": "licensed practical nurse",
    "staff nurse": "licensed practical nurse",
    "chartered accountant": "accountant",
    "fitter and turner": "machinist",
    "accounts clerk": "bookkeeping accounting clerk",
    "police official": "police patrol officer",
    "general worker": "laborer",
    "domestic worker": "maid housekeeping cleaner",
}


# SA titles whose words mean something different in US job names.
REPLACE = {
    "caretaker": "janitor",
}

# Words that say little about which job it is on their own.
GENERIC = {
    "manager", "worker", "officer", "technician", "assistant", "operator", "specialist",
    "professional", "practitioner", "supervisor", "controller", "administrator", "consultant",
    "agent", "attendant", "helper", "associate", "senior", "junior", "chief", "head", "service",
    "general", "official", "coordinator", "director", "executive", "advisor", "adviser",
}

# Reviewed fixes where word matching alone picks the wrong career.
# Keys are OFO titles (lower case) or a regex on the title; values are career slugs.
OVERRIDES = {
    "accounts clerk": "bookkeeping-accounting-and-auditing-clerks",
    "director (enterprise / organisation)": "chief-executives",
}
OVERRIDE_PATTERNS = [
    (re.compile(r"(call|contact) centre .*(agent|consultant|advisor)", re.I), "customer-service-representatives"),
    (re.compile(r"call centre team leader", re.I), "first-line-supervisors-of-office-and-administrative-support-workers"),
    (re.compile(r"^passenger coach driver$", re.I), "bus-drivers-transit-and-intercity"),
    (re.compile(r"^(?!.*(worker|assistant|manager|foreman)).*\bfarmer$", re.I), "farmers-ranchers-and-other-agricultural-managers"),
]


def _apply_phrases(text: str) -> str:
    low = (text or "").lower()
    for k, v in REPLACE.items():
        low = low.replace(k, v)
    for k, v in PHRASES.items():
        low = low.replace(k, f"{k} {v}")
    return low


def toks(text: str) -> Set[str]:
    words = re.findall(r"[a-z]+", _apply_phrases(text))
    out = set()
    for w in words:
        if w in STOP:
            continue
        w = SYNONYMS.get(w, w)
        if len(w) > 4 and w.endswith("ies"):
            w = w[:-3] + "y"
        elif len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
            w = w[:-1]
        out.add(w)
    return out


def sim(a: str, b: str) -> float:
    A, B = toks(a), toks(b)
    if not A or not B:
        return 0.0
    return len(A & B) / len(A | B)


def overlap(a: str, b: str) -> float:
    """Share of the SA title's words found in the career name."""
    A, B = toks(a), toks(b)
    return len(A & B) / len(A) if A else 0.0


def _ofo_rows(sheet) -> List[Tuple[str, str]]:
    rows = []
    for r in list(sheet.iter_rows(values_only=True))[3:]:
        if r and r[0] and r[1] and str(r[0]).startswith("2021-"):
            rows.append((str(r[0])[5:].strip(), str(r[1]).strip()))
    return rows


def load_ofo():
    import openpyxl

    wb = openpyxl.load_workbook(SOURCES / "ofo_2021.xlsx", read_only=True)
    units = dict(_ofo_rows(wb["Unit Groups"]))
    occupations = _ofo_rows(wb["Occupations"])
    alt: Dict[str, List[str]] = defaultdict(list)
    for sheet in ("Specialisations", "Alternate Title"):
        for code, title in _ofo_rows(wb[sheet]):
            # Keep each entry whole: splitting on "/" breaks entries like
            # "Engineer (Applications / Ecommerce)" into meaningless pieces.
            title = re.sub(r"\s+", " ", title).strip()
            if len(title) > 2 and title.lower() != "test":
                alt[code].append(title)
    return units, occupations, alt


def load_isco_to_soc2010():
    import xlrd

    sheet = xlrd.open_workbook(SOURCES / "isco08_soc2010_crosswalk.xls").sheet_by_name("ISCO-08 to 2010 SOC")
    titles: Dict[str, str] = {}
    to_soc: Dict[str, Set[str]] = defaultdict(set)
    for i in range(sheet.nrows):
        v = sheet.row_values(i)
        code = str(v[0]).strip()
        if not re.fullmatch(r"\d{4}", code):
            continue
        titles[code] = str(v[1]).strip()
        soc = str(v[3]).strip()
        if re.fullmatch(r"\d\d-\d{4}", soc):
            to_soc[code].add(soc)
    return titles, to_soc


def load_soc2010_to_2018() -> Dict[str, Set[str]]:
    import openpyxl

    wb = openpyxl.load_workbook(SOURCES / "soc2010_to_soc2018_crosswalk.xlsx", read_only=True)
    ws = wb.worksheets[0]
    out: Dict[str, Set[str]] = defaultdict(set)
    for r in ws.iter_rows(values_only=True):
        if r and r[0] and r[2] and re.fullmatch(r"\d\d-\d{4}", str(r[0]).strip()):
            out[str(r[0]).strip()].add(str(r[2]).strip())
    return out


def _strip_except(name: str) -> str:
    # "Refractory Materials Repairers, Except Brickmasons" must not match brickmasons.
    return re.split(r",?\s+except\s+", name, flags=re.I)[0]


def load_careers():
    titles_by_soc: Dict[str, List[str]] = defaultdict(list)
    path = SOURCES / "onet_job_titles.tsv"
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines()[1:]:
            soc, _, title = line.partition("\t")
            title = re.sub(r"\s*\(.*?\)", "", title).strip()
            if title and title.lower() != "n/a":
                titles_by_soc[soc].append(title)
    careers = []
    for p in sorted(CAREERS_DIR.glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        if len(d.get("skills", [])) < 5:
            continue  # not listed in the app
        full_soc = (d.get("onet") or {}).get("soc_code") or ""
        careers.append({
            "slug": d["slug"],
            "name": d["name"],
            "soc": full_soc[:7],
            # (title, weight): the career's own name counts most
            "titles": [(_strip_except(d["name"]), 1.0)] + [(t, 0.9) for t in titles_by_soc.get(full_soc, [])],
        })
    return careers


def match_unit_to_isco(unit_title: str, unit_code: str, isco_titles: Dict[str, str]) -> Tuple[str, float]:
    best_code, best = "", 0.0
    for code, title in isco_titles.items():
        s = sim(unit_title, title)
        if code == unit_code:
            s += 0.05  # same number breaks ties
        if s > best:
            best_code, best = code, s
    return best_code, best


def build() -> dict:
    units, occupations, alt = load_ofo()
    isco_titles, isco_to_soc = load_isco_to_soc2010()
    soc10_to_18 = load_soc2010_to_2018()
    careers = load_careers()
    careers_by_soc: Dict[str, List[dict]] = defaultdict(list)
    for c in careers:
        careers_by_soc[c["soc"]].append(c)

    unit_to_isco = {}
    for code, title in units.items():
        isco_code, score = match_unit_to_isco(title, code, isco_titles)
        if score >= 0.5:
            unit_to_isco[code] = isco_code

    # Precompute token sets once (this is the slow part otherwise).
    for c in careers:
        c["name_toks"] = toks(c["titles"][0][0])
        c["title_toks"] = [(toks(t), w) for t, w in c["titles"]]
    by_name_token: Dict[str, Set[int]] = defaultdict(set)
    for i, c in enumerate(careers):
        for w in c["name_toks"]:
            by_name_token[w].add(i)

    def title_score(sa_toks_list, career) -> float:
        """How well the SA title (and its OFO alternative titles) match the
        career's name or any of its O*NET job titles."""
        best = 0.0
        for nt, nw in sa_toks_list:
            for tt, tw in career["title_toks"]:
                inter = len(nt & tt)
                if not inter:
                    continue
                exact = 1.0 if nt == tt else 0.0
                best = max(best, (inter / len(nt) + 0.5 * inter / len(nt | tt) + exact) * nw * tw)
        return best

    def coverage(main_toks, career) -> float:
        """Share of the SA title's distinctive words (not 'manager',
        'worker', ...) that appear in the career's own name."""
        key = (main_toks - GENERIC) or main_toks
        return len(key & career["name_toks"]) / len(key) if key else 0.0

    results, unmatched = [], []
    stats = defaultdict(int)
    for code, title in occupations:
        unit = code[:4]
        crosswalk: Dict[str, dict] = {}
        isco = unit_to_isco.get(unit)
        if isco:
            for soc10 in isco_to_soc.get(isco, ()):
                for soc18 in soc10_to_18.get(soc10, {soc10}):
                    for c in careers_by_soc.get(soc18, []):
                        crosswalk[c["slug"]] = c

        main = re.sub(r"\s*\(.*?\)", "", title)  # "(General)", "(Grades 10-12)" don't define the job
        main_toks = toks(main)
        sa_toks_list = [(toks(title), 1.0)] + [(toks(a), 0.7) for a in alt.get(code, []) if toks(a)]

        # Candidates: every crosswalk career, plus any career whose own
        # name contains ALL the words of the SA title (e.g. "Diesel
        # Mechanic" -> "Bus and Truck Mechanics and Diesel Engine Specialists",
        # which the crosswalk files place in a different group).
        pool = dict(crosswalk)
        if main_toks:
            ids = set.intersection(*(by_name_token.get(w, set()) for w in main_toks))
            for i in ids:
                pool[careers[i]["slug"]] = careers[i]

        ranked = sorted(
            pool.values(),
            key=lambda c: (round(coverage(main_toks, c), 3), c["slug"] in crosswalk, title_score(sa_toks_list, c)),
            reverse=True,
        )
        chosen, how = None, ""
        override = OVERRIDES.get(title.strip().lower())
        if not override:
            override = next((slug for pat, slug in OVERRIDE_PATTERNS if pat.search(title.strip())), None)
        if override:
            chosen = next((c for c in careers if c["slug"] == override), None)
            how = "reviewed"
        if not chosen and ranked:
            top = ranked[0]
            cov, ts = coverage(main_toks, top), title_score(sa_toks_list, top)
            if top["slug"] in crosswalk and (cov >= 0.5 or ts >= 1.0):
                chosen, how = top, "crosswalk"
            elif top["slug"] not in crosswalk and cov >= 1.0:
                chosen, how = top, "title"
        if not chosen and main_toks:
            # Nothing in the crosswalk fits: accept a career whose name shares
            # the SA title's key words AND has a matching O*NET job title.
            ids = set().union(*(by_name_token.get(w, set()) for w in main_toks))
            fallback = sorted(
                (careers[i] for i in ids),
                key=lambda c: (round(coverage(main_toks, c), 3), title_score(sa_toks_list, c)),
                reverse=True,
            )
            if fallback:
                f = fallback[0]
                cov, ts = coverage(main_toks, f), title_score(sa_toks_list, f)
                if cov >= 1.0 or (cov >= 0.5 and ts >= 1.0):  # distinctive words
                    chosen, how = f, "title"
        if not chosen:
            unmatched.append(f"{code} {title}")
            stats["unmatched"] += 1
            continue
        stats[how] += 1
        aliases = sorted({a for a in alt.get(code, []) if a.lower() != title.lower()})
        results.append({
            "ofo_code": code,
            "title": title.strip(),
            "aliases": aliases,
            "career_slug": chosen["slug"],
            "career_name": chosen["name"],
            "match": how,
        })

    return {
        "source": "OFO 2021 (South Africa) linked to O*NET careers via ISCO-08 and SOC crosswalks",
        "counts": dict(stats),
        "occupations": results,
        "unmatched": unmatched,
    }


def main():
    data = build()
    OUT.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUT}: {data['counts']}")


if __name__ == "__main__":
    sys.exit(main())
