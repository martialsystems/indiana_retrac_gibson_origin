# Copyright (c) 2026 Martial Systems LLC. All rights reserved.

import csv
import json
from pathlib import Path

from pypdf import PdfReader

from gibson.config import PACKET_FOOTNOTE, SHEET_HOLDOUT
from gibson.sheet import CSV_FIELDS, cover_email_text, cover_letter_text, packet_copy, sort_cells

REPO = Path(__file__).resolve().parents[1]


def test_buyer_pdf_has_cover_and_rows() -> None:
    live = json.loads((REPO / "logs" / "in_live" / "stage_c_report.json").read_text(encoding="utf-8"))
    path = REPO / "delivery" / "gibson_origin_2024_sheet.pdf"
    assert path.is_file()
    reader = PdfReader(str(path))
    assert len(reader.pages) == 4
    text = "\n".join((p.extract_text() or "") for p in reader.pages)
    flat = " ".join(text.split())
    body_after_date = text.split("Origin only.", 1)[-1]
    assert not body_after_date.lstrip().startswith("On Gibson")
    assert PACKET_FOOTNOTE in flat or "Method question" in text
    hold = live["holdout"]
    assert "15,596.8" in text
    assert "35,014.7" in text
    assert "45,939.1" in text
    assert "What this is" in text
    assert "Restricted Waste Site Type I" in flat
    assert "not MSW" in flat
    assert "What happened" in text
    assert "Two answers, not averaged" in text
    assert "How to read a row" in text
    assert "not last year’s share applied to this year’s total" in flat or "not last year's share" in flat
    assert "habit" not in text.lower()
    assert "What is missing" not in text
    assert "Out-of-state" not in text
    q3 = next(c for c in hold["cells"] if c["facility_id"] == "26-06" and c["quarter"] == 3)
    assert q3["residual_tons"] == q3["tons"] - q3["tons_prior"]
    assert abs(q3["residual_tons"] - 83255.0) < 0.1
    assert "+83,255" in text
    assert "IDEM public quarterly reports" in text
    assert "Gibson Generating Station" in text
    assert "Warrick Processing Center" in text
    assert "26-06 (the 98% plant) is a centroid" in flat
    assert "not truck routing" in flat
    assert "Gibson 2024 reported cells" in text
    assert "Figure 1" in text
    assert "Figure 2" in text
    assert "monopoly" in text.lower()
    assert "Revisions" not in text
    assert "\u2014" not in text
    assert "What it is not" not in text
    assert "tip fee" not in text.lower()
    assert "Vermillion" not in text
    assert "SFHA" not in text
    assert "forecast" not in text.lower() or "not a forecast" in text.lower()
    assert "logistics" not in text.lower()
    names = {c["facility_name"] for c in hold["cells"]}
    readme = (REPO / "README.md").read_text(encoding="utf-8")
    for name in names:
        assert name not in readme
    copy = packet_copy(live)
    assert "15,596.8" in copy["answers"]
    assert "35,014.7" in copy["answers"]


def test_table_sort_and_2024_only_blanks() -> None:
    live = json.loads((REPO / "logs" / "in_live" / "stage_c_report.json").read_text(encoding="utf-8"))
    ordered = sort_cells(live["holdout"]["cells"])
    assert len(ordered) == 48
    assert [c["facility_id"] for c in ordered[:4]] == ["26-06"] * 4
    assert [c["quarter"] for c in ordered[:4]] == [1, 2, 3, 4]
    assert [c["facility_id"] for c in ordered[4:8]] == ["63-04"] * 4
    warrick = next(c for c in ordered if c["facility_id"] == "87-13")
    assert warrick["tons_prior"] is None
    assert warrick["residual_tons"] is None
    path = REPO / "delivery" / "gibson_origin_2024_cells.csv"
    with path.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert list(rows[0].keys()) == list(CSV_FIELDS)
    assert len(rows) == 48
    assert [r["ID"] for r in rows[:4]] == ["26-06"] * 4
    assert [r["Q"] for r in rows[:4]] == ["1", "2", "3", "4"]
    w = next(r for r in rows if r["ID"] == "87-13")
    assert w["2023 tons"] == ""
    assert w["2023 share"] == ""
    assert w["2024 tons"] == "833.4"
    assert w["Residual"] == ""
    assert w["Bar share"] == ""
    assert w["Loc"] == "centroid"
    vinc = next(r for r in rows if r["ID"] == "42-09")
    assert vinc["Facility"] == "Vincennes Transfer Station"
    by_key = {(r["ID"], int(r["Q"])): r for r in rows}
    for cell in live["holdout"]["cells"]:
        rec = by_key[(cell["facility_id"], cell["quarter"])]
        assert rec["Loc"] == cell["how"]


def test_cover_email_is_five_lines() -> None:
    text = (REPO / "delivery" / "cover_email.txt").read_text(encoding="utf-8")
    assert text == cover_email_text()
    lines = [ln for ln in text.splitlines() if ln]
    assert len(lines) == 5
    assert "Restricted Waste Site Type I" in lines[1]
    assert "Do not send this PDF to the county SWMD" in lines[3]
    assert "c89de5b" in lines[4]
    assert "Attn: Binhack" not in text
    assert "\u2014" not in text
    assert "Vermillion" not in text


def test_cover_letter_is_a_letter() -> None:
    text = (REPO / "delivery" / "cover_letter.txt").read_text(encoding="utf-8")
    assert text == cover_letter_text()
    assert "Attn: Binhack" not in text
    assert "Do not send to Gibson County Solid Waste Management District" in text
    assert "Restricted Waste Site Type I" in text
    assert "97.8%" in text
    assert "15,596.8" in text
    assert "35,014.7" in text
    assert "not averaged" in text
    assert "centroid" in text
    assert "do not sneak it into c89de5b" in text.lower()
    assert "habit" not in text.lower()
    assert "logistics" not in text.lower()
    assert "safe" not in text.lower()
    assert "Vermillion" not in text
    assert "\u2014" not in text
    assert "What it is not" not in text
