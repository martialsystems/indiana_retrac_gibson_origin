#!/usr/bin/env python3
# Copyright (c) 2026 Martial Systems LLC. All rights reserved.
"""Live IDEM quarterly XLSX, Gibson origin only. Empty cores stop. Stage 0 first."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPO), str(REPO / "src")]

from gibson.errors import FetchError, StageOrderError  # noqa: E402
from gibson.pipeline import run_live  # noqa: E402


def main() -> int:
    dest = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO / "logs" / "in_live"
    cache = Path(sys.argv[2]) if len(sys.argv) > 2 else REPO / "data" / "raw"
    try:
        report = run_live(dest, cache_dir=cache)
    except (FetchError, StageOrderError) as exc:
        dest.mkdir(parents=True, exist_ok=True)
        (dest / "fetch_stop.txt").write_text(str(exc) + "\n", encoding="utf-8")
        print(exc)
        return 2
    print(report["question"])
    hold = report["holdout"]
    print(
        "last-year RMSE",
        round(hold["last_year"]["rmse_tons"], 3),
        "bar",
        round(hold["bar"]["rmse_tons"], 3),
        "beats",
        report["last_year_beats_bar"],
    )
    print(
        "origin-total last-year RMSE",
        hold["origin_total"]["last_year_rmse"],
        "bar",
        hold["origin_total"]["bar_rmse"],
    )
    print("n_point", report["n_point"], "n_centroid", report["n_centroid"])
    print(report["figures"], report.get("delivery"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
