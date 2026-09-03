# Copyright (c) 2026 Martial Systems LLC
"""Display names and GIS type labels. Does not rescore."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from gibson.config import REPO_ROOT, TYPE_OVERRIDE

LEAD_PLANTS = ("26-06", "63-04")
ONLY_2024_ORDER = (
    "87-13",
    "10-01",
    "42-09",
    "84-06",
    "32-02",
    "53-009",
    "49-066",
    "45-47",
)
_KEEP_CAPS = {"LLC", "INC", "LTD", "LP", "RWS", "CD", "EQ"}


def display_name(name: str) -> str:
    s = (name or "").strip()
    if not (s.isupper() and len(s.split()) >= 3):
        return s
    return " ".join(tok if tok in _KEEP_CAPS else tok.title() for tok in s.split())


def type_label(facility_id: str, gis_type: str | None) -> str:
    if facility_id in TYPE_OVERRIDE:
        return TYPE_OVERRIDE[facility_id]
    return (gis_type or "").strip() or "untyped in GIS"


def fmt_tons(val: float | None) -> str:
    if val is None:
        return ""
    return f"{float(val):,.1f}"


def load_gis_types(repo: Path | None = None) -> dict[str, str | None]:
    root = repo or REPO_ROOT
    path = root / "data" / "raw" / "facilities.geojson"
    if not path.is_file():
        return {}
    geo = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, str | None] = {}
    for feat in geo.get("features") or []:
        props = feat.get("properties") or {}
        fid = props.get("sw_program_id")
        if fid:
            out[str(fid)] = props.get("facility_type")
    return out


def sort_holdout_cells(cells: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_fid: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for cell in cells:
        by_fid[str(cell["facility_id"])].append(cell)
    plant_tons = {fid: sum(float(r["tons"]) for r in rows) for fid, rows in by_fid.items()}
    has_prior = {
        fid: any(r.get("tons_prior") is not None for r in rows) for fid, rows in by_fid.items()
    }

    def key(fid: str) -> tuple[int, object, str]:
        if fid in LEAD_PLANTS:
            return (0, LEAD_PLANTS.index(fid), fid)
        if has_prior[fid] and plant_tons[fid] >= 100:
            return (1, -plant_tons[fid], fid)
        if has_prior[fid]:
            return (2, -plant_tons[fid], fid)
        if fid in ONLY_2024_ORDER:
            return (3, ONLY_2024_ORDER.index(fid), fid)
        return (4, -plant_tons[fid], fid)

    ordered: list[dict[str, Any]] = []
    for fid in sorted(by_fid, key=key):
        ordered.extend(sorted(by_fid[fid], key=lambda r: int(r["quarter"])))
    return ordered


def dest_type_rows(
    cells: list[dict[str, Any]], gis: dict[str, str | None]
) -> list[dict[str, str]]:
    by: dict[str, dict[str, Any]] = defaultdict(
        lambda: {"tons": 0.0, "name": "", "how": ""}
    )
    for cell in cells:
        rec = by[str(cell["facility_id"])]
        rec["tons"] += float(cell["tons"])
        rec["name"] = cell.get("facility_name") or rec["name"]
        rec["how"] = cell.get("how") or rec["how"]
    total = sum(r["tons"] for r in by.values()) or 1.0
    rows = []
    for fid, rec in sorted(by.items(), key=lambda kv: -kv[1]["tons"]):
        rows.append(
            {
                "id": fid,
                "facility": display_name(str(rec["name"])),
                "type": type_label(fid, gis.get(fid)),
                "tons": fmt_tons(rec["tons"]),
                "share": f"{100.0 * rec['tons'] / total:.1f}%",
                "loc": str(rec["how"] or ""),
            }
        )
    return rows


def cell_table_rows(
    cells: list[dict[str, Any]], gis: dict[str, str | None]
) -> list[dict[str, str]]:
    rows = []
    for cell in sort_holdout_cells(cells):
        fid = str(cell["facility_id"])
        rows.append(
            {
                "q": str(cell["quarter"]),
                "id": fid,
                "facility": display_name(str(cell.get("facility_name") or "")),
                "type": type_label(fid, gis.get(fid)),
                "prior": fmt_tons(cell.get("tons_prior")),
                "tons": fmt_tons(cell.get("tons")),
                "residual": fmt_tons(cell.get("residual_tons")),
                "loc": str(cell.get("how") or ""),
            }
        )
    return rows
