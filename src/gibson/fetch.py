# Copyright (c) 2026 Martial Systems LLC. All rights reserved.
"""Live IDEM XLSX + GIS. Empty Gibson rows, unmatched origin, or missing CRS stops."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from gibson.config import ORIGIN_KEY, REPO_ROOT
from gibson.counties import load_counties
from gibson.errors import FetchError
from gibson.facilities import load_gis, locate_all
from gibson.geo import load_crs_sidecar
from gibson.xlsx import parse_received


def fetch_live(
    *, cache_dir: Path
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]], dict[str, dict[str, Any]], dict[str, Any]]:
    cache_dir.mkdir(parents=True, exist_ok=True)
    xlsx = cache_dir / "reporting_sw_quarterly_report_2025.xlsx"
    gis_path = cache_dir / "facilities.geojson"
    cty_path = cache_dir / "indiana_counties.json"
    crs_path = cache_dir / "crs.json"
    raw = REPO_ROOT / "data" / "raw"
    if not xlsx.is_file():
        xlsx = raw / "reporting_sw_quarterly_report_2025.xlsx"
    if not gis_path.is_file():
        gis_path = raw / "facilities.geojson"
    if not cty_path.is_file():
        cty_path = raw / "indiana_counties.json"
    if not crs_path.is_file():
        crs_path = raw / "crs.json"
    if not xlsx.is_file() or xlsx.stat().st_size == 0:
        raise FetchError("empty IDEM quarterly XLSX")
    crs = load_crs_sidecar(crs_path)
    counties = load_counties(cty_path)
    rows, stats = parse_received(xlsx, counties=counties)
    gis = load_gis(gis_path)
    facilities = locate_all(rows, gis=gis, counties=counties)
    digest = hashlib.sha256(xlsx.read_bytes()).hexdigest()
    dest_how = [f["how"] for f in facilities.values()]
    meta = {
        "n_rows": len(rows),
        "n_counties": len({r["origin_key"] for r in rows}),
        "n_facilities": len(facilities),
        "origin_key": ORIGIN_KEY,
        "xlsx": str(xlsx),
        "xlsx_sha256": digest,
        "live_retrac_login": False,
        "crs": crs,
        "n_point": sum(1 for h in dest_how if h == "point"),
        "n_centroid": sum(1 for h in dest_how if h == "centroid"),
        **stats,
    }
    return rows, counties, facilities, meta
