# Copyright (c) 2026 Martial Systems LLC. All rights reserved.

import json
import re
from pathlib import Path

from gibson.claims import scan_text
from gibson.config import INDEX_GIST, PARENT_LOCK, QUESTION

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
    assert "Two answers" in text
    assert "Do not average" in text
    assert PARENT_LOCK in text
    assert "6504.7" in text
    assert "16633.0" in text
    assert "origin pop cancels" in text.lower() or "origin population cancels" in text.lower()
    if live["last_year_beats_bar"]:
        assert "wins Gibson assignment" in text or "wins assignment" in text
    else:
        assert "loses Gibson assignment" in text or "loses assignment" in text
    if live["confirm_reverses_holdout"]:
        assert "revers" in text.lower()
    else:
        assert "does not reopen" in text
    assert ".venv/bin/python -m pytest" in text
    assert "Open_the_research_console" not in text
    assert "labelColor" not in text
    assert "indiana_wx_pages" not in text
    assert scan_text(text) == []
    assert "\u2014" not in text
    assert "What it is not" not in text
    assert INDEX_GIST in text
    assert "METHODOLOGY.md" in text
    assert "delivery/gibson_origin_2024_sheet.pdf" in text
    for cell in live["holdout"]["cells"]:
        assert cell["facility_name"] not in text
        assert not re.search(rf"\b{re.escape(cell['facility_id'])}\b", text)
    assert "All rights reserved" in text or "private" in text.lower()
