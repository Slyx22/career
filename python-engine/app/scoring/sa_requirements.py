"""
"Required in South Africa": registrations, licences and trade tests that
South African employers check for some occupations.

These are shown next to the score as a checklist. They do NOT change the
score: the score measures skills; these are legal or professional
requirements a CV can only mention. Each item says whether the CV appears
to mention it, so the person knows what to add or still needs to get.

Occupations are matched by the career's SOC code (first characters), so
every career in that group gets the same checklist.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

TRADE_TEST = ("trade test", "red seal", "artisan", "namb", "qcto trade")


@dataclass(frozen=True)
class Requirement:
    key: str
    label: str
    detail: str
    soc_prefixes: Tuple[str, ...]
    keywords: Tuple[str, ...]
    kind: str = "required"  # "required" (law or registration) | "usual" (employers usually ask)


REQUIREMENTS: Sequence[Requirement] = (
    Requirement("sanc", "SANC registration",
                "Nurses and midwives must be registered with the South African Nursing Council (SANC).",
                ("29-1141", "29-1151", "29-1161", "29-1171", "29-2061"),
                ("sanc", "south african nursing council", "nursing council")),
    Requirement("hpcsa", "HPCSA registration",
                "Doctors, dentists, psychologists, therapists, radiographers, dietitians, optometrists and "
                "emergency care practitioners must be registered with the Health Professions Council of South Africa.",
                ("29-12", "29-1021", "29-1022", "29-1023", "29-1024", "29-1029", "19-303", "29-1122", "29-1123",
                 "29-1127", "29-1031", "29-1041", "29-2034", "29-2035", "29-2041", "29-2042", "29-2043",
                 "29-1292", "29-1129"),
                ("hpcsa", "health professions council")),
    Requirement("sapc", "SAPC registration",
                "Pharmacists and pharmacy support staff must be registered with the South African Pharmacy Council.",
                ("29-1051", "29-2052", "31-9095"),
                ("sapc", "pharmacy council")),
    Requirement("ecsa", "ECSA registration",
                "Engineering work usually needs registration with the Engineering Council of South Africa "
                "(for example Candidate or Professional Engineer, Technologist or Technician).",
                ("17-2", "17-3"),
                ("ecsa", "engineering council", "pr eng", "pr.eng", "pr tech", "pr.tech", "candidate engineer",
                 "candidate technologist", "candidate technician")),
    Requirement("accounting_body", "Professional accounting body",
                "Accountant and auditor roles usually ask for membership or articles with a recognised body, "
                "such as SAICA (CA(SA)), SAIPA, CIMA or ACCA. Registered auditors must also be registered with IRBA.",
                ("13-2011",),
                ("saica", "ca(sa)", "ca (sa)", "saipa", "cima", "acca", "irba", "articles of clerkship", "serving articles",
                 "articled clerk", "trainee accountant", "training contract",
                 "chartered accountant", "professional accountant")),
    Requirement("tax_practitioner", "Registered tax practitioner",
                "Paid tax work requires registration with SARS through a recognised controlling body (for example SAIT or SAIPA).",
                ("13-2082", "13-2081"),
                ("tax practitioner", "sait", "sars registered", "registered with sars")),
    Requirement("sace", "SACE registration",
                "Teachers must be registered with the South African Council for Educators.",
                ("25-1", "25-2", "25-3"),
                ("sace", "council for educators")),
    Requirement("lpc", "Admission and LPC enrolment",
                "Attorneys and advocates must be admitted by the High Court and enrolled with the Legal Practice Council.",
                ("23-1011",),
                ("admitted attorney", "admitted as an attorney", "admitted as attorney", "admitted advocate",
                 "legal practice council", "lpc", "candidate attorney", "articles of clerkship")),
    Requirement("psira", "PSIRA registration",
                "Security officers must be registered with the Private Security Industry Regulatory Authority (PSIRA), "
                "usually with a grade (E to A).",
                ("33-9032", "33-1091", "33-9031"),
                ("psira", "grade a", "grade b", "grade c", "grade d", "grade e")),
    Requirement("wireman", "Trade test and wireman's licence",
                "Electricians need a trade test (Red Seal); signing off installations also needs registration as an "
                "electrician with the Department of Employment and Labour (wireman's licence).",
                ("47-2111", "49-2095", "49-9051"),
                TRADE_TEST + ("wireman", "installation electrician", "master installation electrician")),
    Requirement("plumbing", "Trade test and PIRB registration",
                "Plumbers usually need a trade test (Red Seal); registration with the Plumbing Industry Registration Board "
                "(PIRB) is expected for compliance certificates.",
                ("47-2152",),
                TRADE_TEST + ("pirb", "plumbing industry registration")),
    Requirement("trade_test", "Trade test (Red Seal)",
                "Artisan jobs usually ask for a passed trade test (Red Seal certificate).",
                ("47-2011", "47-2021", "47-2031", "47-2044", "47-2051", "47-2061", "47-2081", "47-2141", "47-2181",
                 "47-2211", "49-3023", "49-3031", "49-3041", "49-3042", "49-9041", "49-9044", "49-9021",
                 "51-4041", "51-4111", "51-4121", "51-2041"),
                TRADE_TEST),
    Requirement("driver", "Correct driver's licence and PrDP",
                "Driving jobs need the right licence code (for example Code 10/C1 or Code 14/EC) and, for passengers or "
                "dangerous goods, a Professional Driving Permit (PrDP).",
                ("53-3032", "53-3033", "53-3052", "53-3053", "53-3054", "53-3011", "53-3099"),
                ("code 8", "code 10", "code 14", "code b", "code c1", "code ec", "code c", "prdp", "pdp",
                 "professional driving permit", "driver's licence", "drivers licence", "driver's license")),
    Requirement("forklift", "Forklift / machine operator certificate",
                "Forklift and lifting-machine operators need a valid operator certificate.",
                ("53-7051", "53-7021"),
                ("forklift licence", "forklift license", "forklift certificate", "operator certificate")),
    Requirement("sacssp", "SACSSP registration",
                "Social workers must be registered with the South African Council for Social Service Professions.",
                ("21-1021", "21-1022", "21-1023", "21-1029"),
                ("sacssp", "council for social service")),
    Requirement("sacap", "SACAP registration",
                "Architects must be registered with the South African Council for the Architectural Profession.",
                ("17-1011",),
                ("sacap", "architectural profession")),
    Requirement("sagc", "SAGC registration",
                "Land surveyors must be registered with the South African Geomatics Council.",
                ("17-1022",),
                ("sagc", "geomatics council", "professional land surveyor")),
    Requirement("ppra", "PPRA Fidelity Fund Certificate",
                "Estate agents need a Fidelity Fund Certificate from the Property Practitioners Regulatory Authority.",
                ("41-9021", "41-9022"),
                ("ppra", "fidelity fund", "ffc", "eaab", "property practitioner")),
    Requirement("fais", "FAIS fit and proper (RE5)",
                "Financial advisers and insurance representatives must meet FSCA fit-and-proper rules, including the RE5 exam.",
                ("13-2052", "41-3021", "41-3031"),
                ("re5", "re 5", "fais", "fsca", "fit and proper")),
    Requirement("savc", "SAVC registration",
                "Veterinarians and veterinary nurses/technicians must be registered with the South African Veterinary Council.",
                ("29-1131", "29-2056"),
                ("savc", "veterinary council")),
    Requirement("sacaa", "SACAA licence",
                "Pilots need a licence from the South African Civil Aviation Authority (for example CPL or ATPL).",
                ("53-2011", "53-2012"),
                ("sacaa", "atpl", "cpl", "commercial pilot licence", "commercial pilot license")),
)


# Not legal requirements: what South African employers usually ask for in
# adverts for these jobs. Shown separately as "Employers usually ask for",
# so nobody mistakes them for a law. Only careers where the ask is common
# get an item; most professional and tech roles get none.
_MATRIC_JOBS = ("31-", "33-", "35-", "37-", "39-", "41-", "43-", "45-", "47-", "49-", "51-", "53-")
USUAL_ASKS: Sequence[Requirement] = (
    Requirement("matric", "Matric (Grade 12)",
                "Most adverts for this kind of job ask for a matric certificate (NSC). If you have it, list it "
                "under Education with the year.",
                _MATRIC_JOBS,
                ("matric", "grade 12", "national senior certificate", "nsc", "senior certificate", "n3",
                 "national certificate (vocational)", "ncv", "nc(v)"),
                "usual"),
    Requirement("accounting_software", "Accounting software",
                "Bookkeeping and accounts jobs usually ask for experience with software such as Sage Pastel, Xero, "
                "QuickBooks, SAP or Syspro. If you've used one, name it under Skills.",
                ("43-3031", "43-3021", "43-3011", "43-3051", "13-2011", "13-2082"),
                ("pastel", "sage", "xero", "quickbooks", "quick books", "sap", "syspro", "caseware", "accpac"),
                "usual"),
    Requirement("computer_literacy", "Computer literacy (MS Office)",
                "Office and admin jobs usually ask for computer literacy, especially Word, Excel and Outlook. "
                "List the programs you can use under Skills.",
                ("43-", "13-1", "11-3011"),
                ("ms office", "microsoft office", "excel", "ms word", "microsoft word", "outlook", "office 365",
                 "microsoft 365", "computer literacy", "computer literate", "icdl", "google workspace",
                 "google sheets"),
                "usual"),
    Requirement("food_safety", "Food safety training",
                "Kitchens and food businesses usually ask for food handler or food safety training "
                "(R638 or HACCP). If you have it, list it under Certifications.",
                ("35-1", "35-2", "51-3"),
                ("food safety", "food handler", "food handling", "haccp", "r638", "r 638", "food hygiene",
                 "hygiene certificate"),
                "usual"),
    Requirement("first_aid", "First aid certificate",
                "Jobs caring for children, patients or the public usually ask for a first aid certificate. "
                "If you have one, list it under Certifications with its level and year.",
                ("39-9011", "25-2011", "39-9031", "39-9032", "31-1", "39-9041", "33-9", "53-3052", "29-2042"),
                ("first aid", "level 1 first aid", "level 2 first aid", "level 3 first aid", "cpr", "bls",
                 "basic life support"),
                "usual"),
    Requirement("drivers_licence", "Driver's licence",
                "Jobs that involve travelling to clients or sites usually ask for a valid driver's licence. "
                "If you have one, list it with its code (e.g. Code 08 / B).",
                ("41-4", "41-3", "49-20", "49-90", "47-21", "47-2152", "11-9021", "13-1031", "43-5021"),
                ("driver's licence", "drivers licence", "driver's license", "drivers license", "driving licence",
                 "code 08", "code 8", "code 10", "code 14", "code b", "code eb", "code c1", "own transport"),
                "usual"),
    Requirement("sabpp", "SABPP registration (often preferred)",
                "HR roles often prefer registration with the South African Board for People Practices. "
                "If you're registered, add it under Certifications.",
                ("13-1071", "13-1141", "13-1151", "11-3121", "11-3111", "43-4161"),
                ("sabpp", "board for people practices", "hr practitioner", "chartered hr"),
                "usual"),
)


def _mentions(text: str, keywords: Sequence[str]) -> bool:
    for k in keywords:
        if re.search(r"(?<![a-z0-9])" + re.escape(k) + r"(?![a-z0-9])", text):
            return True
    return False


def sa_requirements_for(soc_code: Optional[str], cv_text: str) -> List[dict]:
    soc = (soc_code or "")[:7]
    if not soc:
        return []
    text = (cv_text or "").lower()
    out = []
    for req in tuple(REQUIREMENTS) + tuple(USUAL_ASKS):
        if any(soc.startswith(p) for p in req.soc_prefixes):
            out.append({
                "key": req.key,
                "label": req.label,
                "detail": req.detail,
                "found_in_cv": _mentions(text, req.keywords),
                "kind": req.kind,
            })
    return out
