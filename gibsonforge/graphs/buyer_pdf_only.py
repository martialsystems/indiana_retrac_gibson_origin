# Copyright (c) 2026 Martial Systems LLC. All rights reserved.
"""Buyer packet (PDF plus one delivery CSV) is the only Gibson cell table."""

from __future__ import annotations

from typing import Any

from gibsonforge.graphs._common import binary_graph


def _evaluate(state: dict[str, Any]) -> dict[str, Any]:
    v: list[str] = []
    if state.get("gibson_table_outside_pdf"):
        v.append("gibson_table_outside_pdf")
    if state.get("buyer_pdf_missing"):
        v.append("buyer_pdf_missing")
    return {"violations": v, "events": [{"node": "evaluate", "ok": not v}]}


def build_graph():
    return binary_graph(
        name="gibson.buyer_pdf_only",
        evaluate=_evaluate,
        extra=["gibson_table_outside_pdf", "buyer_pdf_missing"],
    )
