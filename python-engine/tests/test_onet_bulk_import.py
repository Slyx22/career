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
    assert by_slug["docker"]["onet_confirmed"] is True
    assert by_slug["tensorflow"]["onet_confirmed"] is True
    # TensorFlow only appears in the Technology Skills fixture (no
    # Skills.txt/Knowledge.txt Importance row for it), so it correctly
    # gets the "technology list only" source, not a real Importance score.
    assert by_slug["tensorflow"]["source"] == "onet_technology_list_only"
    # "Statistics" has a real Importance row (3.62 on a 1-5 scale) and
    # matches our taxonomy - it should get the real numeric source and
    # correctly normalized value: (3.62-1)/4 = 0.655.
    assert by_slug["statistics"]["source"] == "onet_bulk_database"
    assert abs(by_slug["statistics"]["market_importance"] - 0.655) < 1e-6
    # "Active Learning" (IM=3.20) is unmatched by our taxonomy (no
    # skill named "Active Learning"), so it should not appear at all.
    assert "active_learning" not in by_slug


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
