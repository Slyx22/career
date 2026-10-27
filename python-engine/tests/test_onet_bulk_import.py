"""
Tests for scripts/onet_bulk_import.py against realistic fixtures shaped
exactly like the real O*NET Database bulk-download text files (tab
delimited, same column names as Occupation Data.txt / Skills.txt /
Knowledge.txt / Technology Skills.txt), so the parsing logic is verified
without needing the actual multi-hundred-MB database download in CI or
this sandbox.
"""
import csv

import pytest


def _write_tsv(path, rows, fieldnames):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, delimiter="\t", fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture
def fake_onet_db(tmp_path):
    db_dir = tmp_path / "db_29_1_text"
    db_dir.mkdir()

    _write_tsv(
        db_dir / "Occupation Data.txt",
        [{"O*NET-SOC Code": "15-1221.00", "Title": "Computer and Information Research Scientists", "Description": "..."}],
        ["O*NET-SOC Code", "Title", "Description"],
    )

    skills_fields = [
        "O*NET-SOC Code", "Element ID", "Element Name", "Scale ID", "Data Value",
        "N", "Standard Error", "Lower CI Bound", "Upper CI Bound",
        "Recommend Suppress", "Not Relevant", "Date", "Domain Source",
    ]
    _write_tsv(
        db_dir / "Skills.txt",
        [
            {**{k: "" for k in skills_fields}, "O*NET-SOC Code": "15-1221.00", "Element Name": "Programming", "Scale ID": "IM", "Data Value": "4.62"},
            {**{k: "" for k in skills_fields}, "O*NET-SOC Code": "15-1221.00", "Element Name": "Programming", "Scale ID": "LV", "Data Value": "6.10"},
            {**{k: "" for k in skills_fields}, "O*NET-SOC Code": "15-1221.00", "Element Name": "Active Learning", "Scale ID": "IM", "Data Value": "3.20"},
            {**{k: "" for k in skills_fields}, "O*NET-SOC Code": "15-1221.00", "Element Name": "Statistics", "Scale ID": "IM", "Data Value": "3.62"},
            # A different occupation's row that must NOT leak in.
            {**{k: "" for k in skills_fields}, "O*NET-SOC Code": "99-9999.00", "Element Name": "Programming", "Scale ID": "IM", "Data Value": "1.00"},
        ],
        skills_fields,
    )
    _write_tsv(db_dir / "Knowledge.txt", [], skills_fields)

    tech_fields = ["O*NET-SOC Code", "Example", "Commodity Code", "Commodity Title", "Hot Technology", "In Demand"]
    _write_tsv(
        db_dir / "Technology Skills.txt",
        [
            {"O*NET-SOC Code": "15-1221.00", "Example": "Docker", "Commodity Code": "43232304", "Commodity Title": "Application server software", "Hot Technology": "Y", "In Demand": "N"},
            {"O*NET-SOC Code": "15-1221.00", "Example": "TensorFlow", "Commodity Code": "43232304", "Commodity Title": "Analytical or scientific software", "Hot Technology": "Y", "In Demand": "Y"},
        ],
        tech_fields,
    )

    return db_dir


def test_import_career_model_parses_real_shaped_tsv_files(fake_onet_db, tmp_path, monkeypatch):
    import scripts.onet_bulk_import as bulk

    monkeypatch.setattr(bulk, "DATA_DIR", tmp_path / "career_models")

    result = bulk.import_career_model(
        db_dir=fake_onet_db,
        soc_code="15-1221.00",
        career_slug="test-bulk-career",
        career_name=None,
        description="test",
    )

    assert result["name"] == "Computer and Information Research Scientists"
    assert result["onet"]["sync_method"] == "onet_bulk_database"

    by_slug = {s["skill_slug"]: s for s in result["skills"]}
    # O*NET "Programming" (IM 4.62) maps exactly to our "programming" skill:
    # (4.62 - 1) / 4 = 0.905. The LV row must not overwrite it.
    assert by_slug["programming"]["source"] == "onet_bulk_database"
    assert abs(by_slug["programming"]["market_importance"] - 0.905) < 1e-6
    assert by_slug["programming"]["onet_element"] == "Programming"
    # "Active Learning" is a real O*NET skill and now maps exactly.
    assert abs(by_slug["active_learning"]["market_importance"] - 0.55) < 1e-6
    # "Statistics" is not an O*NET element name, so it is not guessed at.
    assert "statistics" not in by_slug
    # Technology Skills examples map to software skills by whole words.
    assert by_slug["docker"]["source"] == "onet_technology_skills"
    assert by_slug["tensorflow"]["market_importance"] == 0.55  # Hot + In Demand
    assert by_slug["docker"]["market_importance"] == 0.45     # Hot only


def _row(soc, elem_id, name, value, fields):
    return {**{k: "" for k in fields}, "O*NET-SOC Code": soc, "Element ID": elem_id,
            "Element Name": name, "Scale ID": "IM", "Data Value": str(value)}


def test_no_loose_matches_for_general_skills():
    """Regression test for the bug that gave 910 careers the same skills:
    'Reading Comprehension' became 'Literacy instruction' and 'Therapy and
    Counseling' (contains 'py') became 'Python'."""
    import scripts.onet_bulk_import as bulk

    fields = ["O*NET-SOC Code", "Element ID", "Element Name", "Scale ID", "Data Value", "Recommend Suppress"]
    rows = [
        _row("29-1141.00", "2.A.1.a", "Reading Comprehension", 4.0, fields),
        _row("29-1141.00", "2.A.1.c", "Writing", 3.5, fields),
        _row("29-1141.00", "2.A.1.d", "Speaking", 4.1, fields),
        _row("29-1141.00", "2.C.5.b", "Therapy and Counseling", 4.2, fields),
        _row("29-1141.00", "2.C.7.a", "English Language", 3.9, fields),
        _row("29-1141.00", "2.C.5.a", "Medicine and Dentistry", 4.5, fields),
    ]
    model = bulk._build_career_model("29-1141.00", "Registered Nurses", "registered-nurses", "",
                                     rows, [], "2026-01-01T00:00:00+00:00")
    slugs = {s["skill_slug"] for s in model["skills"]}
    assert slugs == {"reading_comprehension", "writing", "speaking", "therapy_counseling",
                     "english_language", "medicine"}
    for wrong in ("literacy_instruction", "python", "typescript", "esl_instruction",
                  "grammar_composition", "public_speaking", "model_monitoring"):
        assert wrong not in slugs


def test_low_importance_and_suppressed_elements_are_dropped():
    import scripts.onet_bulk_import as bulk

    fields = ["O*NET-SOC Code", "Element ID", "Element Name", "Scale ID", "Data Value", "Recommend Suppress"]
    rows = [_row("1", f"2.A.1.{c}", n, 4.0, fields) for c, n in
            zip("abcd", ["Reading Comprehension", "Active Listening", "Writing", "Speaking"])]
    rows.append(_row("1", "2.A.2.a", "Critical Thinking", 4.0, fields))
    rows.append(_row("1", "2.B.3.l", "Repairing", 1.5, fields))          # not important
    suppressed = _row("1", "2.B.3.e", "Programming", 4.9, fields)
    suppressed["Recommend Suppress"] = "Y"
    rows.append(suppressed)
    model = bulk._build_career_model("1", "X", "x", "", rows, [], "now")
    slugs = {s["skill_slug"] for s in model["skills"]}
    assert "repairing" not in slugs
    assert "programming" not in slugs
    assert len(slugs) == 5


def test_tech_matching_uses_whole_words_and_software_only():
    import scripts.onet_bulk_import as bulk

    assert bulk._match_tech_slug("Microsoft Excel") == "microsoft_excel"
    assert bulk._match_tech_slug("Python") == "python"
    assert bulk._match_tech_slug("Oracle Java") == "java"
    assert bulk._match_tech_slug("JavaScript") == "javascript"
    assert bulk._match_tech_slug("Microsoft Power BI") == "power_bi"
    assert bulk._match_tech_slug("R") == "r_language"
    assert bulk._match_tech_slug("C++") == "cpp"
    assert bulk._match_tech_slug("Autodesk AutoCAD") == "autocad"
    # Not software skills, and no partial-word matches.
    assert bulk._match_tech_slug("Therapy scheduling software") is None
    assert bulk._match_tech_slug("Epic Systems") is None
    assert bulk._match_tech_slug("Spyware detection") is None


def test_import_all_skips_unrated_and_keeps_hand_made(fake_onet_db, tmp_path, monkeypatch):
    import json
    import scripts.onet_bulk_import as bulk

    out = tmp_path / "career_models"
    out.mkdir()
    (out / "ml-engineer.json").write_text(json.dumps({"slug": "ml-engineer", "name": "ML", "skills": [],
                                                      "onet": {"sync_method": "manual_public_lookup"}}))
    (out / "old-career.json").write_text(json.dumps({"slug": "old-career", "name": "Old", "skills": [],
                                                     "onet": {"sync_method": "onet_bulk_database"}}))
    monkeypatch.setattr(bulk, "DATA_DIR", out)
    monkeypatch.setattr(bulk, "REPORT_PATH", tmp_path / "report.json")

    report = bulk.import_all_careers(fake_onet_db)

    assert (out / "ml-engineer.json").exists()          # hand-made career kept
    assert not (out / "old-career.json").exists()       # stale bulk file removed
    # The fixture occupation has only 2 rated elements + 2 tech skills -> 4 < 5, so it is skipped.
    assert report["careers_written"] == 0
    assert report["careers_skipped_too_few_rated_skills"] == 1
    assert report["unmapped_onet_elements"] == {"Statistics": 1}


def test_only_importance_scale_rows_are_used_not_level(fake_onet_db, tmp_path, monkeypatch):
    """Skills.txt contains both 'IM' (Importance, 1-5) and 'LV' (Level,
    0-7) rows for the same element - only IM should be used, and the 1-5
    scale must be normalized correctly to 0-1."""
    import scripts.onet_bulk_import as bulk

    monkeypatch.setattr(bulk, "DATA_DIR", tmp_path / "career_models")

    # "Programming" isn't in our taxonomy directly, but let's check via a
    # taxonomy skill that does match: none of Skills.txt names match
    # "python" here, so instead verify the SOC-code filtering directly.
    rows = bulk._read_tsv(fake_onet_db / "Skills.txt")
    im_rows = bulk._importance_rows_for_soc(rows, "15-1221.00")
    assert all(r["Scale ID"] == "IM" for r in im_rows)
    assert all(r["O*NET-SOC Code"] == "15-1221.00" for r in im_rows)
    # The LV row and the other occupation's row must both be excluded.
    assert len(im_rows) == 3


def test_list_occupations_reads_all_rows(fake_onet_db, capsys):
    import scripts.onet_bulk_import as bulk

    bulk.list_occupations(fake_onet_db)
    captured = capsys.readouterr()
    assert "15-1221.00" in captured.out
    assert "Computer and Information Research Scientists" in captured.out


def test_missing_file_raises_helpful_error(tmp_path):
    import scripts.onet_bulk_import as bulk

    with pytest.raises(SystemExit, match="not found"):
        bulk._read_tsv(tmp_path / "Skills.txt")


def test_unknown_soc_code_raises_helpful_error(fake_onet_db, tmp_path, monkeypatch):
    import scripts.onet_bulk_import as bulk

    monkeypatch.setattr(bulk, "DATA_DIR", tmp_path / "career_models")

    with pytest.raises(SystemExit, match="not found in Occupation Data"):
        bulk.import_career_model(
            db_dir=fake_onet_db,
            soc_code="00-0000.00",
            career_slug="nonexistent",
            career_name=None,
            description="",
        )
