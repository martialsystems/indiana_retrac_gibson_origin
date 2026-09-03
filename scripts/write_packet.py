#!/usr/bin/env python3
# Copyright (c) 2026 Martial Systems LLC. All rights reserved.
"""Write the buyer packet from the frozen live JSON. Does not rescore. Does not restamp c89de5b."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPO), str(REPO / "src")]

from gibson.config import SHEET_HOLDOUT, SHEET_LOCK  # noqa: E402
from gibson.sheet import write_packet  # noqa: E402
from gibsonforge.observe import sheet_drifted  # noqa: E402


def main() -> int:
    live_dir = REPO / "logs" / "in_live"
    report_path = live_dir / "stage_c_report.json"
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if sheet_drifted(report):
        print(f"refusing packet: live JSON drifted from sheet lock {SHEET_LOCK}")
        return 2
    hold = report["holdout"]
    if int(hold["n_cells"]) != SHEET_HOLDOUT["n_cells"]:
        print("refusing packet: cell count drifted")
        return 2
    paths = write_packet(report=report, log_dir=live_dir, dest_dir=REPO / "delivery")
    print(report["question"])
    print("sheet lock", SHEET_LOCK)
    print(paths)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
