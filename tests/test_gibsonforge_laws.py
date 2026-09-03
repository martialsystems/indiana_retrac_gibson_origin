# Copyright (c) 2026 Martial Systems LLC. All rights reserved.

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from gibsonforge._bootstrap import ensure_paths

ensure_paths()

from graphforge.product_law import LawBlockedError

from gibson.config import PARENT_LOCK, SHEET_LOCK
from gibsonforge.gate import (
    require_buyer_pdf_only,
    require_claims,
    require_locks,
    require_observed,
    require_readme_no_rows,
    require_stage0,
    require_two_answers,
)
from gibsonforge.observe import observe
from gibsonforge.product_laws import laws


def test_laws_allow_and_block() -> None:
    require_stage0(stage0_ok=True, thread_id="t.s.ok")
    with pytest.raises(LawBlockedError):
        require_stage0(stage0_ok=False, thread_id="t.s.missing")
    require_two_answers(thread_id="t.a.ok")
    with pytest.raises(LawBlockedError):
        require_two_answers(answers_averaged=True, thread_id="t.a.avg")
    require_readme_no_rows(thread_id="t.r.ok")
    with pytest.raises(LawBlockedError):
        require_readme_no_rows(readme_has_county_rows=True, thread_id="t.r.rows")
    require_buyer_pdf_only(thread_id="t.b.ok")
    with pytest.raises(LawBlockedError):
        require_buyer_pdf_only(gibson_table_outside_pdf=True, thread_id="t.b.table")
    with pytest.raises(LawBlockedError):
        require_buyer_pdf_only(buyer_pdf_missing=True, thread_id="t.b.pdf")
    require_locks(thread_id="t.l.ok")
    with pytest.raises(LawBlockedError):
        require_locks(parent_restamped=True, thread_id="t.l.parent")
    with pytest.raises(LawBlockedError):
        require_locks(sheet_restamped=True, thread_id="t.l.sheet")
    with pytest.raises(LawBlockedError):
        require_locks(overwrite_frozen_sheet=True, thread_id="t.l.over")
    require_claims(thread_id="t.c.ok")
    with pytest.raises(LawBlockedError):
        require_claims(casualty=True, thread_id="t.c.cas")
    with pytest.raises(LawBlockedError):
        require_claims(climate_attr=True, thread_id="t.c.clim")
    with pytest.raises(LawBlockedError):
        require_claims(pop_at_risk=True, thread_id="t.c.pop")
    with pytest.raises(LawBlockedError):
        require_claims(logistics_opt=True, thread_id="t.c.log")
    with pytest.raises(LawBlockedError):
        require_claims(truck_routing=True, thread_id="t.c.truck")
    with pytest.raises(LawBlockedError):
        require_claims(next_year_forecast=True, thread_id="t.c.nxt")
    assert {row["id"] for row in laws()} == {
        "gibson.stage0_before_live",
        "gibson.two_answers",
        "gibson.readme_no_rows",
        "gibson.buyer_pdf_only",
        "gibson.locks",
        "gibson.claim_bans",
    }


def test_frozen_invoice_observes_clean() -> None:
    obs = observe(REPO, fixture=False, overwrite_frozen_sheet=False)
    assert obs["stage0_ok"] is True
    assert obs["answers_averaged"] is False
    assert obs["readme_has_county_rows"] is False
    assert obs["gibson_table_outside_pdf"] is False
    assert obs["buyer_pdf_missing"] is False
    assert obs["parent_restamped"] is False
    assert obs["sheet_restamped"] is False
    assert obs["sheet_lock"] == SHEET_LOCK
    assert obs["parent_lock"] == PARENT_LOCK
    require_observed(obs, fixture=False, thread_id="t.obs")


def test_overwrite_frozen_live_blocked() -> None:
    from gibson.pipeline import run_live

    with pytest.raises(LawBlockedError):
        run_live(REPO / "logs" / "in_live", cache_dir=REPO / "data" / "raw")
