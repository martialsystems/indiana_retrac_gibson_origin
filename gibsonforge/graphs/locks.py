# Copyright (c) 2026 Martial Systems LLC. All rights reserved.
"""Parent 5800fc3 and sheet lock c89de5b stay frozen."""

from __future__ import annotations

from typing import Any

from gibsonforge.graphs._common import binary_graph


def _evaluate(state: dict[str, Any]) -> dict[str, Any]:
    v: list[str] = []
    if state.get("parent_restamped"):
        v.append("parent_restamped")
    if state.get("sheet_restamped"):
        v.append("sheet_restamped")
    if state.get("overwrite_frozen_sheet"):
        v.append("overwrite_frozen_sheet")
    return {"violations": v, "events": [{"node": "evaluate", "ok": not v}]}


def build_graph():
    return binary_graph(
        name="gibson.locks",
        evaluate=_evaluate,
        extra=["parent_restamped", "sheet_restamped", "overwrite_frozen_sheet"],
    )
