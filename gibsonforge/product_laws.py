# Copyright (c) 2026 Martial Systems LLC
"""Refuse laws. Verify-before-done is the finish gate."""

from __future__ import annotations

from typing import Any


def laws() -> list[dict[str, Any]]:
    from gibsonforge.graphs.claim_bans import build_graph as claim_bans
    from gibsonforge.graphs.locks import build_graph as locks
    from gibsonforge.graphs.rws_disclosure import build_graph as rws_disclosure
    from gibsonforge.graphs.stage0_before_live import build_graph as stage0_before_live
    from gibsonforge.graphs.two_answers import build_graph as two_answers

    return [
        {
            "id": "gibson.stage0_before_live",
            "build": stage0_before_live,
            "state": {"stage0_ok": True},
            "allow_decisions": ["allow"],
        },
        {
            "id": "gibson.two_answers",
            "build": two_answers,
            "state": {"answers_averaged": False},
            "allow_decisions": ["allow"],
        },
        {
            "id": "gibson.rws_disclosure",
            "build": rws_disclosure,
            "state": {"rws_missing": False},
            "allow_decisions": ["allow"],
        },
        {
            "id": "gibson.locks",
            "build": locks,
            "state": {
                "parent_restamped": False,
                "sheet_restamped": False,
                "overwrite_frozen_sheet": False,
            },
            "allow_decisions": ["allow"],
        },
        {
            "id": "gibson.claim_bans",
            "build": claim_bans,
            "state": {
                "casualty": False,
                "climate_attr": False,
                "pop_at_risk": False,
                "logistics_opt": False,
                "truck_routing": False,
                "next_year_forecast": False,
            },
            "allow_decisions": ["allow"],
        },
    ]
