#!/usr/bin/env python3
# Copyright (c) 2026 Martial Systems LLC. All rights reserved.
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPO), str(REPO / "src")]

from gibson.pipeline import stage0_fixture  # noqa: E402


def main() -> int:
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "logs" / "stage0_fixture"
    report = stage0_fixture(dest)
    print(report["question"])
    hold = report["holdout"]
    print(
        "last-year RMSE",
        hold["last_year"]["rmse_tons"],
        "bar",
        hold["bar"]["rmse_tons"],
        "beats",
        report["last_year_beats_bar"],
    )
    print("origin-total", hold["origin_total"])
    print(report["figures"], report.get("sheet"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
