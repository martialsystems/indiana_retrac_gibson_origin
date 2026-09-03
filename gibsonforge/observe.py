# Copyright (c) 2026 Martial Systems LLC. All rights reserved.
"""Read the invoice surfaces. GraphForge consumes the flags, not the RMSE theater."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from gibson.claims import scan_text
from gibson.config import (
    PARENT_CITATION,
    PARENT_LOCK,
    REPO_ROOT,
    SHEET_HOLDOUT,
    SHEET_LOCK,
)
from gibson.sheet import PACKET_CSV

_CLAIM_FLAGS = (
    "casualty",
    "climate_attr",
    "pop_at_risk",
    "logistics_opt",
    "truck_routing",
    "next_year_forecast",
)

def _cells(live: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not live:
        return []
    hold = live.get("holdout") or {}
    rows = hold.get("cells") or []
    return [r for r in rows if isinstance(r, dict)]


def has_facility_identities(text: str, cells: list[dict[str, Any]]) -> bool:
    for cell in cells:
        name = str(cell.get("facility_name") or "")
        fid = str(cell.get("facility_id") or "")
        if name and name in text:
            return True
        if fid and re.search(rf"\b{re.escape(fid)}\b", text):
            return True
    return False


def readme_has_county_rows(text: str, cells: list[dict[str, Any]]) -> bool:
    if has_facility_identities(text, cells):
        return True
    if re.search(r"Gibson 2024 reported cells", text) and "|" in text and "2024 tons" in text:
        return True
    return False


def extra_cell_tables(repo: Path, cells: list[dict[str, Any]]) -> bool:
    skip = {".venv", ".git", "__pycache__", ".pytest_cache"}

    def _files():
        for child in repo.iterdir():
            if child.name in skip:
                continue
            if child.is_file():
                yield child
                continue
            if child.is_dir():
                for path in child.rglob("*"):
                    if any(part in skip for part in path.parts):
                        continue
                    if path.is_file():
                        yield path

    allowed_csv = {(repo / "delivery" / PACKET_CSV).resolve()}
    for path in _files():
        if path.suffix.lower() == ".csv":
            if path.resolve() in allowed_csv:
                continue
            return True
        if path.suffix.lower() == ".md" and path.name not in {
            "README.md",
            "AGENTS.md",
            "CHECKLIST.md",
            "METHODOLOGY.md",
        }:
            body = path.read_text(encoding="utf-8")
            if has_facility_identities(body, cells):
                return True
    return False


def answers_averaged(hold: dict[str, Any], beats: bool, prose: str) -> bool:
    ly = hold.get("last_year") or {}
    bar = hold.get("bar") or {}
    try:
        ly_rmse = float(ly["rmse_tons"])
        bar_rmse = float(bar["rmse_tons"])
    except (KeyError, TypeError, ValueError):
        return True
    cell_win = ly_rmse < bar_rmse
    if bool(beats) != cell_win:
        return True
    if hold.get("overall_rmse") is not None or hold.get("average_rmse") is not None:
        return True
    ot = hold.get("origin_total") or {}
    if "bar_rmse" in ot and float(ot["bar_rmse"]) != 0.0:
        return True
    if "Do not average" not in prose:
        return True
    if "wins" in prose and "loses" not in prose and "lose" not in prose:
        if cell_win:
            return True
    return False


def sheet_drifted(live: dict[str, Any] | None) -> bool:
    if not live:
        return True
    hold = live.get("holdout") or {}
    ly = hold.get("last_year") or {}
    bar = hold.get("bar") or {}
    ot = hold.get("origin_total") or {}
    try:
        if round(float(ly["rmse_tons"]), 1) != SHEET_HOLDOUT["last_year_rmse"]:
            return True
        if round(float(bar["rmse_tons"]), 1) != SHEET_HOLDOUT["bar_rmse"]:
            return True
        if round(float(ot["last_year_rmse"]), 1) != SHEET_HOLDOUT["origin_total_last_year_rmse"]:
            return True
        if float(ot["bar_rmse"]) != SHEET_HOLDOUT["origin_total_bar_rmse"]:
            return True
        if int(hold["n_last_year"]) != SHEET_HOLDOUT["n_intersection"]:
            return True
        if int(hold["n_cells"]) != SHEET_HOLDOUT["n_cells"]:
            return True
        if int(ot["n"]) != SHEET_HOLDOUT["n_origin_total"]:
            return True
    except (KeyError, TypeError, ValueError):
        return True
    return False


def parent_restamped(text: str, live: dict[str, Any] | None) -> bool:
    if PARENT_LOCK not in text:
        return True
    cite = PARENT_CITATION
    if f"{cite['intersection_last_year_rmse']}" not in text:
        return True
    if f"{cite['intersection_bar_rmse']}" not in text:
        return True
    if live is not None and str(live.get("parent_lock") or "") not in ("", PARENT_LOCK):
        return True
    return False


def addressed_to_swmd(letter: str, email: str) -> bool:
    head = (letter or "").split("Re:", 1)[0]
    if re.search(r"Attn:\s*Binhack", head, re.I):
        return True
    if "gcsw@" in head.lower():
        return True
    first = (email or "").splitlines()[:1]
    if first and "gcsw@" in first[0].lower():
        return True
    return False


def district_msw_pitch(*texts: str) -> bool:
    blob = "\n".join(texts)
    for sent in re.split(r"(?<=[.!?])\s+", blob):
        low = sent.lower()
        if "district finding" in low and "do not call" not in low:
            return True
        if "gibson county waste" in low and "do not email" not in low and "do not send" not in low:
            return True
    return False


def claim_flags(*texts: str) -> dict[str, bool]:
    hits: set[str] = set()
    for text in texts:
        hits.update(scan_text(text or ""))
    return {k: k in hits for k in _CLAIM_FLAGS}


def load_live(repo: Path) -> dict[str, Any] | None:
    path = repo / "logs" / "in_live" / "stage_c_report.json"
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def observe(
    repo: Path | None = None,
    *,
    live: dict[str, Any] | None = None,
    fixture: bool = False,
    overwrite_frozen_sheet: bool = False,
    stage0_ok: bool | None = None,
) -> dict[str, Any]:
    root = repo or REPO_ROOT
    readme_path = root / "README.md"
    readme = readme_path.read_text(encoding="utf-8") if readme_path.is_file() else ""
    frozen = live if live is not None else load_live(root)
    cells = _cells(frozen)
    hold = (frozen or {}).get("holdout") or {}
    cover = str(hold.get("cover") or "")
    prose = cover + "\n" + readme
    pdf = root / "delivery" / "gibson_origin_2024_sheet.pdf"
    letter_p = root / "delivery" / "cover_letter.txt"
    email_p = root / "delivery" / "cover_email.txt"
    letter = letter_p.read_text(encoding="utf-8") if letter_p.is_file() else ""
    email = email_p.read_text(encoding="utf-8") if email_p.is_file() else ""
    stage0 = root / "logs" / "stage0_fixture" / "stage0_report.json"
    flags = {
        "stage0_ok": stage0.is_file() if stage0_ok is None else bool(stage0_ok),
        "answers_averaged": answers_averaged(
            hold,
            bool((frozen or {}).get("last_year_beats_bar")),
            prose,
        )
        if hold
        else (not fixture),
        "readme_has_county_rows": readme_has_county_rows(readme, cells),
        "gibson_table_outside_pdf": extra_cell_tables(root, cells) or readme_has_county_rows(readme, cells),
        "buyer_pdf_missing": (not fixture) and (not pdf.is_file()),
        "parent_restamped": parent_restamped(readme, frozen),
        "sheet_restamped": (not fixture) and sheet_drifted(frozen),
        "overwrite_frozen_sheet": bool(overwrite_frozen_sheet),
        "addressed_to_swmd": addressed_to_swmd(letter, email),
        "district_msw_pitch": district_msw_pitch(letter, email, cover, readme),
        "sheet_lock": SHEET_LOCK,
        "parent_lock": PARENT_LOCK,
    }
    flags.update(claim_flags(readme, cover))
    return flags
