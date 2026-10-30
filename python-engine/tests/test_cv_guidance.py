"""CV guidance: suggestions are CV-only actions, privacy warnings never keep
the value, weak lines aren't quoted, and the SA checklist separates legal
requirements from what employers usually ask for."""
import re

from app.extractors.cv_extractor import extract_from_text
from app.nlp.onet_elements import ONET_ELEMENTS
from app.recommendations.cv_checks import (
    _valid_sa_id,
    cv_basics,
    cv_steps,
    privacy_warnings,
    weak_lines,
    work_link_step,
)
from app.scoring.sa_requirements import sa_requirements_for


def _valid_id():
    for d in "0123456789":
        if _valid_sa_id("920215080008" + d):
            return "920215080008" + d


def test_skill_advice_is_only_about_the_cv():
    banned = re.compile(r"\b(build|take a|complete a|do a|give a|portfolio|github|samples?|try a)\b", re.I)
    offenders = [e.slug for e in ONET_ELEMENTS if banned.search(e.action)]
    assert offenders == []


def test_people_skills_go_under_skills():
    by_slug = {e.slug: e.action for e in ONET_ELEMENTS}
    for slug in ("active_listening", "critical_thinking", "negotiation", "judgment_decision_making"):
        assert "under Skills" in by_slug[slug]


def test_weak_lines_report_the_opener_not_the_cv_wording():
    cv = extract_from_text(
        "Experience\nClerk, ABC, 2021 - 2024\nResponsible for creditors at Mabena\n"
        "Duties included capturing invoices\nReconciled 200 accounts monthly\n"
    )
    assert weak_lines(cv) == ["Responsible for", "Duties included"]
    step = cv_steps(cv)[0]
    assert "Mabena" not in step and "capturing invoices" not in step
    assert step.startswith("2 job lines start with")


def test_privacy_warnings_find_details_but_never_return_them():
    valid = _valid_id()
    cv = extract_from_text(f"Name\n{valid}\nDate of Birth: 15 Feb 1992\nRace: Black\nMarital status: single")
    warnings = privacy_warnings(cv)
    labels = [w["label"] for w in warnings]
    assert labels == ["ID number", "date of birth or age", "race or population group", "marital status"]
    assert valid not in repr(warnings) and "1992" not in repr(warnings)


def test_phone_numbers_are_not_id_numbers():
    assert privacy_warnings(extract_from_text("Cell: 0821234567\nRef 1234567890123")) == []


def test_work_link_only_for_careers_that_show_work_and_only_without_a_link():
    plain = extract_from_text("Experience\nDesigner 2022 - 2025")
    assert work_link_step("27-1024.00", plain) is not None  # graphic designer
    assert work_link_step("29-1141.00", plain) is None  # registered nurse
    linked = extract_from_text("Experience\nDesigner\nhttps://behance.net/me")
    assert work_link_step("27-1024.00", linked) is None


def test_basics_never_ask_for_personal_details():
    keys = {b.key for b in cv_basics(extract_from_text("Hello"))}
    assert keys == {"skills_section", "experience_section", "education_section", "dates", "languages", "length"}


def test_sa_checklist_separates_required_and_usual():
    nurse = sa_requirements_for("29-1141.00", "")
    assert [r["kind"] for r in nurse] == ["required"]
    clerk = sa_requirements_for("43-3031.00", "Matric 2010. Sage Pastel.")
    assert {r["key"]: r["found_in_cv"] for r in clerk} == {
        "matric": True,
        "accounting_software": True,
        "computer_literacy": False,
    }
    assert all(r["kind"] == "usual" for r in clerk)


def test_writing_articles_is_not_accounting_articles():
    reqs = sa_requirements_for("13-2011.00", "I wrote articles for the school newspaper")
    body = [r for r in reqs if r["key"] == "accounting_body"][0]
    assert body["found_in_cv"] is False
