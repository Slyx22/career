"""
Tests for the O*NET integration:
  1. The data-driven career model loader (reads JSON from app/data/career_models/).
  2. The O*NET sync script's parsing/mapping logic, using response shapes
     that match O*NET Web Services' documented JSON format
     (https://services.onetcenter.org/reference/online/occupation/details/skills),
     mocked so these tests run offline without real API credentials.
"""
import json

from app.scoring.career_model import (
    clear_career_model_cache,
    get_career_model,
    list_careers,
)


def test_ml_engineer_career_model_loads_from_json():
    clear_career_model_cache()
    model = get_career_model("ml-engineer")
    assert model.name == "ML Engineer"
    assert len(model.skills) > 20
    assert model.onet is not None
    assert model.onet.soc_code == "15-1221.00"


def test_all_four_phase2_careers_load_with_real_onet_soc_codes():
    """
    Confirms the career catalog now covers Data Scientist, Software
    Engineer, and English Teacher alongside ML Engineer - and that each
    one is mapped to a real, cited O*NET-SOC code, not a placeholder.
    """
    clear_career_model_cache()
    expected = {
        "ml-engineer": "15-1221.00",
        "data-scientist": "15-2051.00",
        "software-engineer": "15-1252.00",
        "english-teacher": "25-2031.00",
    }
    for slug, soc_code in expected.items():
        model = get_career_model(slug)
        assert model.onet is not None
        assert model.onet.soc_code == soc_code
        assert model.onet.source_url and model.onet.source_url.startswith("https://www.onetonline.org")
        assert len(model.skills) >= 10


def test_english_teacher_uses_education_taxonomy_not_tech_skills():
    """English Teacher should score against education-specific skills,
    not the ML/software taxonomy - confirms the taxonomy genuinely
    generalizes beyond tech careers."""
    clear_career_model_cache()
    model = get_career_model("english-teacher")
    slugs = {s.skill_slug for s in model.skills}
    assert "lesson_planning" in slugs
    assert "classroom_management" in slugs
    assert "grammar_composition" in slugs
    # Should not be scored against ML/software-specific skills.
    assert "pytorch" not in slugs
    assert "kubernetes" not in slugs


def test_english_teacher_cv_scores_end_to_end():
    """Full pipeline test: a genuine English-teacher CV, scored against
    the english-teacher career model, produces sensible results - proof
    the whole system (extraction, evidence, scoring) generalizes beyond
    tech careers, not just the data layer."""
    from app.extractors.cv_extractor import extract_from_text
    from app.nlp.skill_extractor import extract_skill_evidence
    from app.scoring.scorer import score_career_readiness

    cv_text = """
    Dana Whitfield
    High School English Teacher

    Experience
    English Teacher, Riverside High School (2019 - 2026)
    - Designed and delivered lesson plans for grades 9-12 English Language Arts.
    - Built and enforced a positive classroom management system across five sections.
    - Developed a curriculum unit on American literature aligned to state standards.
    - Used differentiated instruction to support English language learners (ELL) in mixed-level classes.
    - Communicated regularly with parents about student progress at conferences.
    - Designed rubrics and assessments for essays and grammar/composition units.

    Education
    BA English Literature, 2018
    """
    clear_career_model_cache()
    cv = extract_from_text(cv_text)
    evidence = extract_skill_evidence(cv)
    career_model = get_career_model("english-teacher")
    result = score_career_readiness(evidence, career_model)

    assert 0 <= result.overall_score <= 100
    # A CV this well-matched to the career should show meaningful,
    # non-zero readiness with real strengths detected - proof the
    # taxonomy/matching genuinely works for a non-tech career, not that
    # it silently no-ops and returns 0.
    assert result.overall_score >= 25
    assert len(result.strengths) >= 3
    assert evidence["lesson_planning"].present
    assert evidence["classroom_management"].present
    assert evidence["differentiated_instruction"].present


def test_list_careers_reflects_data_directory():
    clear_career_model_cache()
    careers = list_careers()
    slugs = [c["slug"] for c in careers]
    assert "ml-engineer" in slugs


def test_onet_confirmed_skills_are_flagged():
    clear_career_model_cache()
    model = get_career_model("ml-engineer")
    confirmed = {s.skill_slug for s in model.skills if s.onet_confirmed}
    # These were independently verified in O*NET OnLine's public
    # Technology Skills report for 15-1221.00 (see app/data/career_models/ml-engineer.json).
    assert "docker" in confirmed
    assert "kubernetes" in confirmed
    assert "tensorflow" in confirmed


def test_unmatched_skills_keep_benchmark_estimate_source():
    clear_career_model_cache()
    model = get_career_model("ml-engineer")
    by_slug = {s.skill_slug: s for s in model.skills}
    # A skill not yet synced from the real API should stay clearly
    # labeled as an estimate, never silently presented as sourced data.
    assert by_slug["mongodb"].source == "benchmark_estimate"
    assert by_slug["mongodb"].onet_confirmed is False


# ---------------------------------------------------------------------
# O*NET sync script - offline parsing tests (no network calls made)
# ---------------------------------------------------------------------

MOCK_ONET_SKILLS_RESPONSE = {
    "code": "15-1221.00",
    "report": "details",
    "element": [
        {
            "id": "2.B.5.a",
            "name": "Programming",
            "description": "Writing computer programs for various purposes.",
            "score": {"scale": "Importance", "important": True, "value": 91},
        },
        {
            "id": "2.A.2.a",
            "name": "Active Learning",
            "description": "Understanding the implications of new information.",
            "score": {"scale": "Importance", "important": True, "value": 40},
        },
    ],
}

MOCK_ONET_TECH_SKILLS_RESPONSE = {
    "code": "15-1221.00",
    "report": "summary",
    "category": [
        {
            "title": {"name": "Application server software"},
            "example": [
                {"name": "Docker", "hot_technology": True},
                {"name": "Kubernetes", "hot_technology": True},
            ],
        },
        {
            "title": {"name": "Analytical or scientific software"},
            "example": [
                {"name": "TensorFlow", "hot_technology": True},
                {"name": "SAS", "hot_technology": False},
            ],
        },
    ],
}


def test_match_taxonomy_slug_finds_known_skills():
    from scripts.onet_sync import _match_taxonomy_slug

    assert _match_taxonomy_slug("Docker") == "docker"
    assert _match_taxonomy_slug("TensorFlow") == "tensorflow"
    assert _match_taxonomy_slug("Kubernetes") == "kubernetes"
    assert _match_taxonomy_slug("Some Totally Unrelated Tool") is None


def test_sync_career_model_parses_mocked_onet_responses(tmp_path, monkeypatch):
    """
    Exercises the full sync_career_model() flow with the network calls
    replaced by fixtures shaped exactly like O*NET's documented JSON
    response format, so we verify the parsing/mapping logic without
    needing live O*NET credentials in CI or this sandbox.
    """
    import scripts.onet_sync as onet_sync

    monkeypatch.setattr(onet_sync, "DATA_DIR", tmp_path)
    monkeypatch.setattr(onet_sync, "fetch_skills", lambda soc: MOCK_ONET_SKILLS_RESPONSE["element"])
    monkeypatch.setattr(onet_sync, "fetch_knowledge", lambda soc: [])
    monkeypatch.setattr(
        onet_sync, "fetch_technology_skills", lambda soc: MOCK_ONET_TECH_SKILLS_RESPONSE["category"]
    )

    result = onet_sync.sync_career_model(
        soc_code="15-1221.00",
        career_slug="test-career",
        career_name="Test Career",
        description="A career used only for testing.",
    )

    by_slug = {s["skill_slug"]: s for s in result["skills"]}

    # "Programming" (value 91) should map to our "python"... actually it
    # doesn't match any taxonomy alias directly, so nothing should crash -
    # the important behaviour is that Docker/Kubernetes/TensorFlow (which
    # DO match) get real numeric-sourced or confirmed entries.
    assert by_slug["docker"]["onet_confirmed"] is True
    assert by_slug["kubernetes"]["onet_confirmed"] is True
    assert by_slug["tensorflow"]["onet_confirmed"] is True

    output_file = tmp_path / "test-career.json"
    assert output_file.exists()
    with open(output_file) as f:
        written = json.load(f)
    assert written["onet"]["soc_code"] == "15-1221.00"
    assert written["onet"]["sync_method"] == "onet_web_services_api"
