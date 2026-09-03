# Copyright (c) 2026 Martial Systems LLC

import json
from pathlib import Path

from gibson.claims import scan_text
from gibson.config import PARENT_LOCK, QUESTION, SHEET_LOCK, THREE_SENTENCES
from gibson.labels import cell_table_rows, dest_type_rows, load_gis_types

REPO = Path(__file__).resolve().parents[1]


def test_readme_opens_with_the_question() -> None:
    text = (REPO / "README.md").read_text(encoding="utf-8")
    body = "\n".join(text.splitlines()[1:]).lstrip()
    assert body.startswith(QUESTION)
    live = json.loads((REPO / "logs" / "in_live" / "stage_c_report.json").read_text(encoding="utf-8"))
    ly = live["holdout"]["last_year"]["rmse_tons"]
    bar = live["holdout"]["bar"]["rmse_tons"]
    assert f"{ly:.1f}" in text
    assert f"{bar:.1f}" in text
    tot = live["holdout"]["origin_total"]["last_year_rmse"]
    assert f"{tot:.1f}" in text
    for sentence in THREE_SENTENCES:
        assert sentence in text
    assert "Do not average" in text
    assert PARENT_LOCK in text
    assert SHEET_LOCK in text
    assert "gibsonforge/" in text
    assert "6504.7" in text
    assert "16633.0" in text
    assert "15597" in text
    assert "76281" in text
    assert "origin pop cancels" in text.lower() or "origin population cancels" in text.lower()
    assert "wins assignment" in text or "wins the cell-by-cell assignment" in text
    assert "loses the quarterly totals" in text
    if live["confirm_reverses_holdout"]:
        assert "revers" in text.lower()
    else:
        assert "does not reopen" in text
    assert "scatter.png" in text
    assert "dest_rank.png" not in text
    assert "Left: full scale" in text
    assert ".venv/bin/python -m pytest" in text
    assert "Open_the_research_console" not in text
    assert "labelColor" not in text
    assert "indiana_wx_pages" not in text
    assert "delivery/" not in text
    assert "All rights reserved" not in text
    assert "Binhack" not in text
    assert "county garbage" not in text.lower()
    assert scan_text(text) == []
    assert "\u2014" not in text
    assert "What it is not" not in text
    assert "METHODOLOGY.md" in text
    assert "26-06 is a centroid" in text
    gis = load_gis_types(REPO)
    cells = live["holdout"]["cells"]
    types = dest_type_rows(cells, gis)
    assert types[0]["id"] == "26-06"
    assert "Duke CCR" in types[0]["type"]
    assert types[0]["share"] == "97.8%"
    assert any(r["id"] == "63-04" and "Municipal Solid Waste Landfill" in r["type"] for r in types)
    assert len(cell_table_rows(cells, gis)) == 48


def test_omitting_third_sentence_fails_check() -> None:
    from gibson.readme_lock import check_readme

    text = (REPO / "README.md").read_text(encoding="utf-8")
    live = json.loads((REPO / "logs" / "in_live" / "stage_c_report.json").read_text(encoding="utf-8"))
    assert check_readme(text, live, repo=REPO) == []
    cut = text.replace(THREE_SENTENCES[2], "")
    errors = check_readme(cut, live, repo=REPO)
    assert any("missing required sentence" in e for e in errors)
