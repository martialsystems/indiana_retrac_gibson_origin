# Copyright (c) 2026 Martial Systems LLC
"""Facility coordinates: GIS name match, else host-county centroid from ID prefix."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from gibson.counties import alphabetical_codes
from gibson.errors import FetchError
from gibson.geo import crs_name, require_lonlat_crs


def _norm_fac(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", " ", (name or "").lower()).strip()
    for tok in (
        "llc",
        "inc",
        "ltd",
        "corp",
        "corporation",
        "facility",
        "landfill",
        "transfer station",
        "recycling",
        "disposal",
        "of indiana",
    ):
        s = s.replace(tok, " ")
    return re.sub(r"\s+", " ", s).strip()


def load_gis(path: Path) -> dict[str, tuple[float, float]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    require_lonlat_crs(crs_name(data.get("crs")))
    out: dict[str, tuple[float, float]] = {}
    for feat in data.get("features") or []:
        props = feat.get("properties") or {}
        geom = feat.get("geometry") or {}
        coords = geom.get("coordinates") or []
        if len(coords) < 2:
            continue
        lon, lat = float(coords[0]), float(coords[1])
        n = _norm_fac(str(props.get("facility_name") or ""))
        if n and n not in out:
            out[n] = (lat, lon)
    if not out:
        raise FetchError("empty facility GIS")
    return out


def locate(
    *,
    facility_id: str,
    facility_name: str,
    gis: dict[str, tuple[float, float]],
    counties: dict[str, dict[str, Any]],
    codes: dict[str, str],
) -> tuple[float, float, str]:
    n = _norm_fac(facility_name)
    if n in gis:
        lat, lon = gis[n]
        return lat, lon, "point"
    prefix = facility_id.split("-")[0].zfill(2)
    rev = {v: k for k, v in codes.items()}
    host = rev.get(prefix)
    if host is None:
        raise FetchError(f"no coordinates for facility {facility_id} {facility_name}")
    rec = counties[host]
    return float(rec["lat"]), float(rec["lon"]), "centroid"


def locate_all(
    rows: list[dict[str, Any]],
    *,
    gis: dict[str, tuple[float, float]],
    counties: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    codes = alphabetical_codes(counties)
    out: dict[str, dict[str, Any]] = {}
    for r in rows:
        fid = r["facility_id"]
        if fid in out:
            continue
        lat, lon, how = locate(
            facility_id=fid,
            facility_name=r["facility_name"],
            gis=gis,
            counties=counties,
            codes=codes,
        )
        out[fid] = {"lat": lat, "lon": lon, "how": how, "name": r["facility_name"]}
    return out
