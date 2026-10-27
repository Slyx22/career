"""South African titles, checklist and qualifications."""
from app.scoring.sa_requirements import sa_requirements_for
from app.scoring.sa_titles import resolve_sa_title, sa_titles_for_listing
from app.scoring.career_model import list_careers


def _titles():
    listed = {c["slug"] for c in list_careers()}
    return {t["t"].lower(): t["s"] for t in sa_titles_for_listing(listed)}


def test_common_sa_titles_link_to_the_right_career():
    t = _titles()
    assert len(t) > 800
    expected = {
        "general accountant": "accountants-and-auditors",
        "accounts clerk": "bookkeeping-accounting-and-auditing-clerks",
        "software developer": "software-developers",
        "electrician": "electricians",
        "registered nurse (medical)": "registered-nurses",
        "enrolled nurse": "licensed-practical-and-licensed-vocational-nurses",
        "foundation phase school teacher": "elementary-school-teachers-except-special-education",
        "diesel mechanic": "bus-and-truck-mechanics-and-diesel-engine-specialists",
        "bricklayer": "brickmasons-and-blockmasons",
        "dairy farmer": "farmers-ranchers-and-other-agricultural-managers",
    }
    for title, slug in expected.items():
        assert t.get(title) == slug, title


def test_every_sa_title_points_to_a_listed_career():
    listed = {c["slug"] for c in list_careers()}
    assert all(s in listed for s in _titles().values())


def test_only_linked_titles_can_appear_on_certificates():
    assert resolve_sa_title("registered-nurses", "registered nurse (medical)") == "Registered Nurse (Medical)"
    assert resolve_sa_title("registered-nurses", "Chief Hacker Supreme") is None
    assert resolve_sa_title("electricians", "Registered Nurse (Medical)") is None


def test_requirements_checklist():
    reqs = sa_requirements_for("29-1141.00", "Professional nurse, registered with SANC.")
    assert [r["key"] for r in reqs] == ["sanc"]
    assert reqs[0]["found_in_cv"] is True
    reqs = sa_requirements_for("47-2111.00", "Electrician with 5 years experience")
    assert reqs[0]["key"] == "wireman" and reqs[0]["found_in_cv"] is False
    assert sa_requirements_for("15-1252.00", "Software developer") == []


def test_sa_qualifications_count_for_education():
    from app.nlp.education_detector import EducationLevel, detect_education_level

    assert detect_education_level("Passed trade test (Red Seal)").level == EducationLevel.DIPLOMA
    assert detect_education_level("N6 Electrical Engineering").level == EducationLevel.DIPLOMA
    assert detect_education_level("Higher Certificate in IT").level == EducationLevel.ASSOCIATE
    assert detect_education_level("BCom Accounting").level == EducationLevel.BACHELOR
