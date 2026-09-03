# Copyright (c) 2026 Martial Systems LLC. All rights reserved.

import csv
import json
from pathlib import Path

from pypdf import PdfReader

from gibson.config import QUESTION, SHEET_HOLDOUT
from gibson.sheet import CSV_FIELDS, cover_email_text, packet_copy

REPO = Path(__file__).resolve().parents[1]


def test_buyer_pdf_has_cover_and_rows() -> None:
    live = json.loads((REPO / "logs" / "in_live" / "stage_c_report.json").read_text(encoding="utf-8"))
    path = REPO / "delivery" / "gibson_origin_2024_sheet.pdf"
    assert path.is_file()
    reader = PdfReader(str(path))
    text = "\n".join((p.extract_text() or "") for p in reader.pages)
    assert QUESTION in text
    hold = live["holdout"]
    assert f"{hold['last_year']['rmse_tons']:.1f}" in text
    assert f"{hold['bar']['rmse_tons']:.1f}" in text
    assert "one origin" in text.lower()
    assert "Held-out 2024" in text
    assert "How to read a row" in text
    assert "2024 tons exceeded 2023 same-quarter tons at that plant" in text
    assert "habit" not in text.lower()
    q3 = next(c for c in hold["cells"] if c["facility_id"] == "26-06" and c["quarter"] == 3)
    assert q3["residual_tons"] == q3["tons"] - q3["tons_prior"]
    assert abs(q3["residual_tons"] - 83255.0) < 0.1
    assert "great-circle" in text
    assert "nine destinations" in text.lower() or "Nine destinations" in text
    assert "Out-of-state origins" in text
    assert "does not know 2024" in text
    assert "IDEM public quarterly reports" in text
    assert "Gibson Generating Station" in text
    assert "Gibson 2024 reported cells" in text
    assert "Figure 1" in text
    assert "Figure 2" in text
    assert "Revisions" not in text
    assert "\u2014" not in text
    assert "What it is not" not in text
    assert "tip fee" not in text.lower()
    assert "Vermillion" not in text
    assert "SFHA" not in text
    names = {c["facility_name"] for c in hold["cells"]}
    readme = (REPO / "README.md").read_text(encoding="utf-8")
    for name in names:
        assert name not in readme
    copy = packet_copy(live)
    assert "15596.8" in copy["cells"]
    assert "35014.7" in copy["cells"]


def test_buyer_csv_matches_pdf_columns() -> None:
    live = json.loads((REPO / "logs" / "in_live" / "stage_c_report.json").read_text(encoding="utf-8"))
    path = REPO / "delivery" / "gibson_origin_2024_cells.csv"
    with path.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert list(rows[0].keys()) == list(CSV_FIELDS)
    assert len(rows) == SHEET_HOLDOUT["n_cells"]
    cells = live["holdout"]["cells"]
    assert len(rows) == len(cells)
    for rec, cell in zip(rows, cells, strict=True):
        assert rec["Q"] == str(cell["quarter"])
        assert rec["ID"] == cell["facility_id"]
        assert rec["Facility"] == cell["facility_name"]
        assert rec["Loc"] == cell["how"]
        assert "miles" not in rec
        assert "bar_tons" not in rec
    extra = path.read_text(encoding="utf-8")
    assert "tip fee" not in extra.lower()


def test_cover_email_is_five_lines() -> None:
    text = (REPO / "delivery" / "cover_email.txt").read_text(encoding="utf-8")
    assert text == cover_email_text()
    lines = [ln for ln in text.splitlines() if ln]
    assert len(lines) == 5
    assert lines[0] == "Gibson 2024 vs 2023 same-quarter destinations."
    assert "subscription" in lines[4]
    assert "\u2014" not in text
    assert "Vermillion" not in text
