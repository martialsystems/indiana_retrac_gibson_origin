# Copyright (c) 2026 Martial Systems LLC
"""README lock: question first, three sentences, JSON numbers, type table."""

from __future__ import annotations

from typing import Any

from gibson.claims import scan_text
from gibson.config import PARENT_LOCK, QUESTION, SHEET_LOCK, THREE_SENTENCES


def check_readme(text: str, live: dict[str, Any], *, repo) -> list[str]:
    del repo
    errors: list[str] = []
    body = "\n".join(text.splitlines()[1:]).lstrip()
    if not body.startswith(QUESTION):
        errors.append("README body does not open with QUESTION")
    for sentence in THREE_SENTENCES:
        if sentence not in text:
            errors.append(f"missing required sentence: {sentence}")
    if PARENT_LOCK not in text:
        errors.append("missing parent lock SHA")
    if SHEET_LOCK not in text:
        errors.append("missing science lock SHA")
    if "Do not average" not in text:
        errors.append("missing do-not-average")
    if "scatter.png" not in text or "dest_rank.png" not in text:
        errors.append("missing two figures")
    if "26-06 is a centroid" not in text:
        errors.append("missing residual: 26-06 is a centroid")
    if "great-circle" not in text:
        errors.append("missing residual: great-circle miles")
    if "Out-of-state" not in text:
        errors.append("missing residual: out-of-state dropped")
    if "Open_the_research_console" in text or "labelColor" in text:
        errors.append("console button leaked")
    if "indiana_wx_pages" in text:
        errors.append("winter pages leaked")
    if "What it is not" in text:
        errors.append("What it is not heading")
    if "\u2014" in text:
        errors.append("decorative em dash")
    if "All rights reserved" in text:
        errors.append("All rights reserved leaked")
    if "delivery/" in text:
        errors.append("delivery/ leaked")
    if "Binhack" in text:
        errors.append("Binhack leaked")
    if "4,500" in text or "$4500" in text:
        errors.append("price leaked")
    if "county garbage" in text.lower():
        errors.append("called it county garbage")
    if scan_text(text):
        errors.append(f"banned claims {scan_text(text)}")
    hold = live["holdout"]
    ly = hold["last_year"]["rmse_tons"]
    bar = hold["bar"]["rmse_tons"]
    if f"{ly:.1f}" not in text or f"{bar:.1f}" not in text:
        errors.append("README missing JSON intersection RMSE")
    tot = hold["origin_total"]["last_year_rmse"]
    if tot is not None and f"{tot:.1f}" not in text:
        errors.append("README missing JSON origin-total RMSE")
    if "Restricted Waste Site Type I" not in text:
        errors.append("missing Restricted Waste Site Type I")
    if "Duke CCR" not in text:
        errors.append("missing Duke CCR")
    if "not an MSW landfill" not in text and "not MSW" not in text:
        errors.append("missing not-MSW type line")
    if "63-04" not in text or "Blackfoot" not in text:
        errors.append("missing Blackfoot MSW row")
    if "1,507,685.0" not in text:
        errors.append("missing 26-06 2024 tons")
    if "97.8%" not in text:
        errors.append("missing 97.8% share")
    if "15597" not in text or "76281" not in text:
        errors.append("missing parent Gibson-row citation")
    if ".venv/bin/python -m pytest" not in text:
        errors.append("missing venv pytest")
    return errors
