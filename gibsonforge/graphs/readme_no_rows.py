# Copyright (c) 2026 Martial Systems LLC. All rights reserved.
"""README may not ship Gibson county rows."""

from __future__ import annotations

from typing import Any

from gibsonforge.graphs._common import binary_graph


def _evaluate(state: dict[str, Any]) -> dict[str, Any]:
    v: list[str] = []
    if state.get("readme_has_county_rows"):
        v.append("readme_has_county_rows")
    return {"violations": v, "events": [{"node": "evaluate", "ok": not v}]}


def build_graph():
    return binary_graph(
        name="gibson.readme_no_rows",
        evaluate=_evaluate,
        extra=["readme_has_county_rows"],
    )
