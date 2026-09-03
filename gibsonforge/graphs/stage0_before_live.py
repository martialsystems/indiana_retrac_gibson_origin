# Copyright (c) 2026 Martial Systems LLC
"""Stage 0 fixture must exist before live."""

from __future__ import annotations

from typing import Any

from gibsonforge.graphs._common import binary_graph


def _evaluate(state: dict[str, Any]) -> dict[str, Any]:
    v: list[str] = []
    if not state.get("stage0_ok"):
        v.append("stage0_missing")
    return {"violations": v, "events": [{"node": "evaluate", "ok": not v}]}


def build_graph():
    return binary_graph(name="gibson.stage0_before_live", evaluate=_evaluate, extra=["stage0_ok"])
