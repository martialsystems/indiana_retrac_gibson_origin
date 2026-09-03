# Copyright (c) 2026 Martial Systems LLC
"""Frozen 2020 county population and centroids. Name aliases for IDEM spellings."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from gibson.config import ORIGIN_KEY
from gibson.errors import FetchError

_ALIASES = {
    "dekalb": "dekalb",
    "de kalb": "dekalb",
    "stjoseph": "stjoseph",
    "st joseph": "stjoseph",
    "saintjoseph": "stjoseph",
    "laporte": "laporte",
    "la porte": "laporte",
    "lagrange": "lagrange",
    "la grange": "lagrange",
}


def key_name(name: str) -> str:
    s = re.sub(r"[^a-z0-9]+", " ", (name or "").lower()).strip()
    s = s.replace(" county", "").strip()
    compact = s.replace(" ", "")
    return _ALIASES.get(s, _ALIASES.get(compact, compact))


def load_counties(path: Path) -> dict[str, dict[str, Any]]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, dict[str, Any]] = {}
    for rec in rows:
        k = key_name(str(rec["name"]))
        lat = rec.get("lat")
        lon = rec.get("lon")
        if lat is None or lon is None:
            raise FetchError(f"missing county centroid CRS coordinates for {rec.get('name')}")
        out[k] = {
            "name": rec["name"],
            "fips": rec["fips"],
            "lat": float(lat),
            "lon": float(lon),
            "pop_2020": int(rec["pop_2020"]),
            "key": k,
        }
    if len(out) != 92:
        raise FetchError(f"expected 92 Indiana counties, got {len(out)}")
    if ORIGIN_KEY not in out:
        raise FetchError("Gibson county missing from frozen county file")
    return out


def alphabetical_codes(counties: dict[str, dict[str, Any]]) -> dict[str, str]:
    ordered = sorted(counties.values(), key=lambda r: r["name"])
    return {rec["key"]: f"{i+1:02d}" for i, rec in enumerate(ordered)}
