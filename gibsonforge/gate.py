# Copyright (c) 2026 Martial Systems LLC. All rights reserved.
"""Call sites for refuse laws."""

from __future__ import annotations

from typing import Any

from gibsonforge._bootstrap import ensure_paths

ensure_paths()

from graphforge.product_law import require_law

from gibsonforge.graphs.buyer_pdf_only import build_graph as build_buyer
from gibsonforge.graphs.claim_bans import build_graph as build_claims
from gibsonforge.graphs.locks import build_graph as build_locks
from gibsonforge.graphs.readme_no_rows import build_graph as build_readme
from gibsonforge.graphs.stage0_before_live import build_graph as build_stage0
from gibsonforge.graphs.two_answers import build_graph as build_two


def require_stage0(**flags: Any) -> None:
    thread_id = str(flags.pop("thread_id", "gibson_stage0"))
    state = {"stage0_ok": False}
    state.update(flags)
    require_law(
        build_stage0(),
        state,
        allow_decisions=["allow"],
        law_id="gibson.stage0_before_live",
        thread_id=thread_id,
        raise_error=True,
    )


def require_two_answers(**flags: Any) -> None:
    thread_id = str(flags.pop("thread_id", "gibson_two"))
    state = {"answers_averaged": False}
    state.update(flags)
    require_law(
        build_two(),
        state,
        allow_decisions=["allow"],
        law_id="gibson.two_answers",
        thread_id=thread_id,
        raise_error=True,
    )


def require_readme_no_rows(**flags: Any) -> None:
    thread_id = str(flags.pop("thread_id", "gibson_readme"))
    state = {"readme_has_county_rows": False}
    state.update(flags)
    require_law(
        build_readme(),
        state,
        allow_decisions=["allow"],
        law_id="gibson.readme_no_rows",
        thread_id=thread_id,
        raise_error=True,
    )


def require_buyer_pdf_only(**flags: Any) -> None:
    thread_id = str(flags.pop("thread_id", "gibson_buyer"))
    state = {"gibson_table_outside_pdf": False, "buyer_pdf_missing": False}
    state.update(flags)
    require_law(
        build_buyer(),
        state,
        allow_decisions=["allow"],
        law_id="gibson.buyer_pdf_only",
        thread_id=thread_id,
        raise_error=True,
    )


def require_locks(**flags: Any) -> None:
    thread_id = str(flags.pop("thread_id", "gibson_locks"))
    state = {
        "parent_restamped": False,
        "sheet_restamped": False,
        "overwrite_frozen_sheet": False,
    }
    state.update(flags)
    require_law(
        build_locks(),
        state,
        allow_decisions=["allow"],
        law_id="gibson.locks",
        thread_id=thread_id,
        raise_error=True,
    )


def require_claims(**flags: Any) -> None:
    thread_id = str(flags.pop("thread_id", "gibson_claims"))
    state = {
        "casualty": False,
        "climate_attr": False,
        "pop_at_risk": False,
        "logistics_opt": False,
        "truck_routing": False,
        "next_year_forecast": False,
    }
    state.update(flags)
    require_law(
        build_claims(),
        state,
        allow_decisions=["allow"],
        law_id="gibson.claim_bans",
        thread_id=thread_id,
        raise_error=True,
    )


def require_observed(obs: dict[str, Any], *, fixture: bool, thread_id: str) -> None:
    require_two_answers(answers_averaged=obs["answers_averaged"], thread_id=f"{thread_id}.two")
    require_readme_no_rows(
        readme_has_county_rows=obs["readme_has_county_rows"],
        thread_id=f"{thread_id}.readme",
    )
    require_claims(
        casualty=obs["casualty"],
        climate_attr=obs["climate_attr"],
        pop_at_risk=obs["pop_at_risk"],
        logistics_opt=obs["logistics_opt"],
        truck_routing=obs["truck_routing"],
        next_year_forecast=obs["next_year_forecast"],
        thread_id=f"{thread_id}.claims",
    )
    if fixture:
        return
    require_stage0(stage0_ok=obs["stage0_ok"], thread_id=f"{thread_id}.stage0")
    require_buyer_pdf_only(
        gibson_table_outside_pdf=obs["gibson_table_outside_pdf"],
        buyer_pdf_missing=obs["buyer_pdf_missing"],
        thread_id=f"{thread_id}.buyer",
    )
    require_locks(
        parent_restamped=obs["parent_restamped"],
        sheet_restamped=obs["sheet_restamped"],
        overwrite_frozen_sheet=obs["overwrite_frozen_sheet"],
        thread_id=f"{thread_id}.locks",
    )
