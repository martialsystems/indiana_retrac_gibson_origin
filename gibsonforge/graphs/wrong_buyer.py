# Copyright (c) 2026 Martial Systems LLC. All rights reserved.
"""This lock is all reported tons. It is not a Gibson SWMD MSW product."""

from __future__ import annotations

from typing import Any

from gibsonforge.graphs._common import binary_graph


def _evaluate(state: dict[str, Any]) -> dict[str, Any]:
    v: list[str] = []
    if state.get("addressed_to_swmd"):
        v.append("addressed_to_swmd")
    if state.get("district_msw_pitch"):
        v.append("district_msw_pitch")
    return {"violations": v, "events": [{"node": "evaluate", "ok": not v}]}


def build_graph():
    return binary_graph(
        name="gibson.wrong_buyer",
        evaluate=_evaluate,
        extra=["addressed_to_swmd", "district_msw_pitch"],
    )
