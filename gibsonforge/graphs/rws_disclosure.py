# Copyright (c) 2026 Martial Systems LLC
"""README must ship the RWS Type I / Duke CCR / not MSW line."""

from __future__ import annotations

from typing import Any

from gibsonforge.graphs._common import binary_graph


def _evaluate(state: dict[str, Any]) -> dict[str, Any]:
    v: list[str] = []
    if state.get("rws_missing"):
        v.append("rws_missing")
    return {"violations": v, "events": [{"node": "evaluate", "ok": not v}]}


def build_graph():
    return binary_graph(name="gibson.rws_disclosure", evaluate=_evaluate, extra=["rws_missing"])
