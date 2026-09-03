# Copyright (c) 2026 Martial Systems LLC. All rights reserved.
"""Two answers. Do not average cell assignment with the quarterly total."""

from __future__ import annotations

from typing import Any

from gibsonforge.graphs._common import binary_graph


def _evaluate(state: dict[str, Any]) -> dict[str, Any]:
    v: list[str] = []
    if state.get("answers_averaged"):
        v.append("answers_averaged")
    return {"violations": v, "events": [{"node": "evaluate", "ok": not v}]}


def build_graph():
    return binary_graph(name="gibson.two_answers", evaluate=_evaluate, extra=["answers_averaged"])
