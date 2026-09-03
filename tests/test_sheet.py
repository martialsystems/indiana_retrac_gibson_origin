# Copyright (c) 2026 Martial Systems LLC. All rights reserved.

import json
from pathlib import Path

from pypdf import PdfReader

from gibson.config import PARENT_LOCK, QUESTION

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
    assert f"{hold['origin_total']['last_year_rmse']:.1f}" in text
    assert "Do not average" in text
    assert PARENT_LOCK in text
    assert "EPSG:4326" in text
    assert "n_point=18" in text
    assert "n_centroid=9" in text
    names = {c["facility_name"] for c in hold["cells"]}
    assert any(n in text for n in names)
    assert "Gibson 2024 reported cells" in text
    assert "Figure 1" in text
    assert "Figure 2" in text
    assert "\u2014" not in text
    assert "What it is not" not in text
    readme = (REPO / "README.md").read_text(encoding="utf-8")
    for name in names:
        assert name not in readme
