# Copyright (c) 2026 Martial Systems LLC

import json
from pathlib import Path

from gibson.config import QUESTION, SHEET_HOLDOUT, SHEET_LOCK
from gibson.errors import FigureCapError
from gibson.figure import _cap
from gibson.pipeline import stage0_fixture


def test_fixture_two_figures(tmp_path: Path) -> None:
    report = stage0_fixture(tmp_path)
    assert report["question"] == QUESTION
    assert report["figures"] == ["scatter.png"]
    assert (tmp_path / "scatter.png").is_file()
    assert not (tmp_path / "dest_rank.png").is_file()
    assert not (tmp_path / "fixture_sheet.pdf").is_file()
    assert report["contestant"] == "last_year"
    assert report["ridge"] is False
    assert report["live_retrac_login"] is False
    assert report["winter_page_hero"] is False
    assert report["confirm_in_train"] is False
    assert report["confirm_in_j"] is False
    assert report["origin_pop_cancels"] is True
    assert report["last_year_beats_bar"] is True
    assert report["origin_key"] == "gibson"
    hold = report["holdout"]
    assert hold["last_year"]["rmse_tons"] < hold["bar"]["rmse_tons"]
    assert hold["origin_total"]["bar_rmse"] == 0.0
    assert hold["origin_total"]["last_year_rmse"] > hold["origin_total"]["bar_rmse"]
    assert "Do not average" in hold["cover"]
    assert (tmp_path / "stage0_report.json").is_file()
    payload = json.loads((tmp_path / "stage0_report.json").read_text(encoding="utf-8"))
    assert "obs_ly" not in payload["holdout"]
    assert payload["holdout"]["cells"]
    assert payload["parent_lock"] == "5800fc3"
    assert payload["sheet_lock"] == SHEET_LOCK


def test_live_holdout_split() -> None:
    path = Path(__file__).resolve().parents[1] / "logs" / "in_live" / "stage_c_report.json"
    live = json.loads(path.read_text(encoding="utf-8"))
    assert live["contestant"] == "last_year"
    assert live["live_retrac_login"] is False
    assert live["ridge"] is False
    assert live["confirm_in_j"] is False
    assert live["confirm_in_train"] is False
    assert live["origin_pop_cancels"] is True
    assert live["holdout_years"] == [2024]
    assert live["confirm_years"] == [2025]
    assert live["origin_key"] == "gibson"
    assert live["n_holdout"] > 0
    assert live["n_confirm"] > 0
    hold = live["holdout"]
    assert hold["n_last_year"] > 0
    assert hold["origin_total"]["bar_rmse"] == 0.0
    assert "rmse_tons" in hold["last_year"]
    assert "rmse_tons" in hold["bar"]
    assert live["last_year_beats_bar"] == (hold["last_year"]["rmse_tons"] < hold["bar"]["rmse_tons"])
    assert round(hold["last_year"]["rmse_tons"], 1) == SHEET_HOLDOUT["last_year_rmse"]
    assert round(hold["bar"]["rmse_tons"], 1) == SHEET_HOLDOUT["bar_rmse"]
    assert round(hold["origin_total"]["last_year_rmse"], 1) == SHEET_HOLDOUT["origin_total_last_year_rmse"]
    assert hold["n_last_year"] == SHEET_HOLDOUT["n_intersection"]
    assert hold["n_cells"] == SHEET_HOLDOUT["n_cells"]
    assert "scatter.png" in live["figures"]
    assert (path.parent / "scatter.png").is_file()
    assert not (path.parent / "dest_rank.png").is_file()
    assert live["fetch_meta"]["n_counties"] == 1
    assert live["fetch_meta"]["live_retrac_login"] is False
    assert live["n_point"] >= 1
    assert live["n_centroid"] >= 0
    assert live["fetch_meta"]["crs"]["facilities_geojson"] == "EPSG:4326"
    assert live["fetch_meta"]["crs"]["warp"] == "none"
    assert hold["bar_all"]["n"] == hold["n_cells"]
    assert hold["n_last_year"] != hold["n_cells"] or hold["n_skip_last_year"] == 0
    cells = hold["cells"]
    assert len(cells) == hold["n_cells"]
    assert all(c["year"] == 2024 for c in cells)


def test_third_figure_refused() -> None:
    try:
        _cap(2)
        raise AssertionError("cap allowed 2")
    except FigureCapError:
        pass
