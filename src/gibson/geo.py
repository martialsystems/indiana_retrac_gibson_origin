# Copyright (c) 2026 Martial Systems LLC. All rights reserved.
"""Great-circle miles. Road miles is a sequel. CRS is fail-closed."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from gibson.config import EARTH_MI, REQUIRED_CRS
from gibson.errors import FetchError

_OK_CRS = {
    "EPSG:4326",
    "epsg:4326",
    "urn:ogc:def:crs:EPSG::4326",
    "urn:ogc:def:crs:OGC:1.3:CRS84",
    "CRS84",
}


def miles(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return EARTH_MI * 2 * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1.0 - a)))


def crs_name(crs_obj: Any) -> str:
    if crs_obj is None:
        raise FetchError("missing CRS")
    if isinstance(crs_obj, str):
        name = crs_obj.strip()
    elif isinstance(crs_obj, dict):
        props = crs_obj.get("properties") or {}
        name = str(props.get("name") or crs_obj.get("name") or "").strip()
    else:
        raise FetchError(f"unreadable CRS {crs_obj!r}")
    if not name:
        raise FetchError("missing CRS")
    return name


def require_lonlat_crs(name: str) -> str:
    if name not in _OK_CRS:
        raise FetchError(f"refused CRS {name!r}; need {REQUIRED_CRS} or CRS84")
    return REQUIRED_CRS


def load_crs_sidecar(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FetchError("missing CRS sidecar")
    rec = json.loads(path.read_text(encoding="utf-8"))
    fac = require_lonlat_crs(str(rec.get("facilities_geojson") or ""))
    cty = require_lonlat_crs(str(rec.get("counties") or ""))
    warp = str(rec.get("warp") or "").strip()
    if not warp:
        raise FetchError("missing CRS warp log")
    out_sr = rec.get("gis_query_outSR")
    if out_sr is None:
        raise FetchError("missing gis_query_outSR")
    return {
        "facilities_geojson": fac,
        "counties": cty,
        "warp": warp,
        "gis_query_outSR": int(out_sr),
        "note": str(rec.get("note") or ""),
    }
