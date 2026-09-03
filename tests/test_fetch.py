# Copyright (c) 2026 Martial Systems LLC. All rights reserved.

from datetime import date
from pathlib import Path

import pytest

from gibson.config import TON_COLS
from gibson.errors import FetchError, StageOrderError
from gibson.facilities import load_gis
from gibson.fetch import fetch_live
from gibson.geo import load_crs_sidecar
from gibson.pipeline import run_live
from gibson.xlsx import parse_received


def test_empty_xlsx_stops(tmp_path: Path) -> None:
    (tmp_path / "reporting_sw_quarterly_report_2025.xlsx").write_bytes(b"")
    (tmp_path / "facilities.geojson").write_text(
        '{"type":"FeatureCollection","crs":{"type":"name","properties":{"name":"EPSG:4326"}},"features":[]}\n',
        encoding="utf-8",
    )
    (tmp_path / "indiana_counties.json").write_text("[]\n", encoding="utf-8")
    (tmp_path / "crs.json").write_text(
        '{"facilities_geojson":"EPSG:4326","counties":"EPSG:4326","warp":"none","gis_query_outSR":4326}\n',
        encoding="utf-8",
    )
    with pytest.raises(FetchError, match="empty IDEM quarterly XLSX"):
        fetch_live(cache_dir=tmp_path)


def test_unmatched_origin_stops(tmp_path: Path) -> None:
    import openpyxl

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Start Date", "ID Number", "Facility Name", "Origin State", "Origin County", *TON_COLS])
    ws.append([date(2021, 1, 1), "01-01", "North Fill", "Indiana", "NotACounty", *([1] * len(TON_COLS))])
    path = tmp_path / "tiny.xlsx"
    wb.save(path)
    counties = {"gibson": {"name": "Gibson", "lat": 38.3, "lon": -87.6, "pop_2020": 1, "fips": "18051", "key": "gibson"}}
    with pytest.raises(FetchError, match="unmatched origin counties"):
        parse_received(path, counties=counties)


def test_gis_missing_crs_stops(tmp_path: Path) -> None:
    path = tmp_path / "facilities.geojson"
    path.write_text('{"type":"FeatureCollection","features":[]}\n', encoding="utf-8")
    with pytest.raises(FetchError, match="missing CRS"):
        load_gis(path)


def test_crs_sidecar_required(tmp_path: Path) -> None:
    with pytest.raises(FetchError, match="missing CRS sidecar"):
        load_crs_sidecar(tmp_path / "crs.json")
    (tmp_path / "crs.json").write_text(
        '{"facilities_geojson":"EPSG:4326","counties":"EPSG:4326","warp":"","gis_query_outSR":4326}\n',
        encoding="utf-8",
    )
    with pytest.raises(FetchError, match="missing CRS warp log"):
        load_crs_sidecar(tmp_path / "crs.json")


def test_live_refuses_without_stage0(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from gibson import pipeline

    monkeypatch.setattr(pipeline, "REPO_ROOT", tmp_path)
    with pytest.raises(StageOrderError, match="Stage 0"):
        run_live(tmp_path / "out", cache_dir=tmp_path)
