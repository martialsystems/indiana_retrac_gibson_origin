#!/usr/bin/env python3
# Copyright (c) 2026 Martial Systems LLC. All rights reserved.
"""README may cite 5800fc3 and the two-answer rule. It may not ship county rows."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPO), str(REPO / "src")]

from gibson.claims import scan_text  # noqa: E402
from gibson.config import INDEX_GIST, PARENT_LOCK, QUESTION  # noqa: E402


def main() -> int:
    text = (REPO / "README.md").read_text(encoding="utf-8")
    body = "\n".join(text.splitlines()[1:]).lstrip()
    errors: list[str] = []
    if not body.startswith(QUESTION):
        errors.append("README body does not open with QUESTION")
    if PARENT_LOCK not in text:
        errors.append("missing parent lock SHA")
    if "Two answers" not in text:
        errors.append("missing two-answer rule")
    if "Do not average" not in text:
        errors.append("missing do-not-average")
    if INDEX_GIST not in text:
        errors.append("missing research index footer")
    if "Open_the_research_console" in text or "labelColor" in text:
        errors.append("console button leaked")
    if "indiana_wx_pages" in text:
        errors.append("winter pages leaked")
    if "What it is not" in text:
        errors.append("What it is not heading")
    if "\u2014" in text:
        errors.append("decorative em dash")
    if scan_text(text):
        errors.append(f"banned claims {scan_text(text)}")
    live_path = REPO / "logs" / "in_live" / "stage_c_report.json"
    if live_path.is_file():
        live = json.loads(live_path.read_text(encoding="utf-8"))
        ly = live["holdout"]["last_year"]["rmse_tons"]
        bar = live["holdout"]["bar"]["rmse_tons"]
        if f"{ly:.1f}" not in text or f"{bar:.1f}" not in text:
            errors.append("README missing JSON intersection RMSE")
        tot = live["holdout"]["origin_total"]["last_year_rmse"]
        if tot is not None and f"{tot:.1f}" not in text:
            errors.append("README missing JSON origin-total RMSE")
        for cell in live["holdout"]["cells"]:
            name = cell["facility_name"]
            if name and name in text:
                errors.append(f"README shipped county row {name}")
            fid = cell["facility_id"]
            if re.search(rf"\b{re.escape(fid)}\b", text):
                errors.append(f"README shipped facility id {fid}")
        if "Vermillion" in text or "Sullivan" in text or "Floyd" in text:
            if "statewide" not in text.lower():
                errors.append("other origins named without statewide citation")
    if errors:
        print("\n".join(errors))
        return 1
    print("readme ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
