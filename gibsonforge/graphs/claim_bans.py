# Copyright (c) 2026 Martial Systems LLC. All rights reserved.
"""Invoice claim bans. Other scanners stay on pytest."""

from __future__ import annotations

from typing import Any

from gibsonforge.graphs._common import binary_graph

_FLAGS = (
    "casualty",
    "climate_attr",
    "pop_at_risk",
    "logistics_opt",
    "truck_routing",
    "next_year_forecast",
)


def _evaluate(state: dict[str, Any]) -> dict[str, Any]:
    v = [k for k in _FLAGS if state.get(k)]
    return {"violations": v, "events": [{"node": "evaluate", "ok": not v}]}


def build_graph():
    return binary_graph(name="gibson.claim_bans", evaluate=_evaluate, extra=[*_FLAGS])
