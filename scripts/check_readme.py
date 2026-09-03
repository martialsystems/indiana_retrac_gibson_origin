#!/usr/bin/env python3
# Copyright (c) 2026 Martial Systems LLC
"""README is question-first, JSON-numbered, three sentences, type table, 48 rows."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(REPO), str(REPO / "src")]

from gibson.readme_lock import check_readme  # noqa: E402


def main() -> int:
    text = (REPO / "README.md").read_text(encoding="utf-8")
    live = json.loads((REPO / "logs" / "in_live" / "stage_c_report.json").read_text(encoding="utf-8"))
    errors = check_readme(text, live, repo=REPO)
    if errors:
        print("\n".join(errors))
        return 1
    print("readme ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
