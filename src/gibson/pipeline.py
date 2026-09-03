# Copyright (c) 2026 Martial Systems LLC
"""Stage 0 fixture. Live fetch-or-stop. One figure. Last year vs inverse-miles."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from gibson.claims import require_clean, require_paths_clean
from gibson.config import PARENT_CITATION, PARENT_LOCK, QUESTION, REPO_ROOT, SHEET_LOCK
from gibson.errors import StageOrderError
from gibson.fetch import fetch_live
from gibson.figure import write_two
from gibson.fixture import build_fixture
from gibson.skill import score
from gibson.split import assert_split
from gibsonforge.gate import require_observed, require_two_answers
from gibsonforge.observe import answers_averaged, observe

_ARRAY_KEYS = ("obs_ly", "pred_ly", "obs_bar", "pred_bar")


def _public_block(block: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in block.items() if k not in _ARRAY_KEYS}


def _jsonable(report: dict[str, Any]) -> dict[str, Any]:
    out = dict(report)
    if isinstance(out.get("holdout"), dict):
        out["holdout"] = _public_block(out["holdout"])
    if isinstance(out.get("confirm"), dict):
        out["confirm"] = _public_block(out["confirm"])
    return out


def _run(
    log_dir: Path,
    *,
    rows: list[dict[str, Any]],
    counties: dict[str, dict[str, Any]],
    facilities: dict[str, dict[str, Any]],
    fixture: bool,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    require_clean(QUESTION, source="question")
    fit = score(rows, counties=counties, facilities=facilities)
    assert_split(
        confirm_in_train=bool(fit["confirm_in_train"]),
        confirm_in_j=bool(fit["confirm_in_j"]),
        random_split=bool(fit["random_split"]),
    )
    readme_text = ""
    readme_path = REPO_ROOT / "README.md"
    if readme_path.is_file():
        readme_text = readme_path.read_text(encoding="utf-8")
    require_two_answers(
        answers_averaged=answers_averaged(
            fit["holdout"],
            bool(fit["last_year_beats_bar"]),
            str(fit["holdout"].get("cover") or "") + "\n" + readme_text,
        ),
        thread_id="two_mem",
    )
    locked_live = (REPO_ROOT / "logs" / "in_live").resolve()
    overwrite = (not fixture) and log_dir.resolve() == locked_live
    obs = observe(
        REPO_ROOT,
        fixture=fixture,
        overwrite_frozen_sheet=overwrite,
    )
    require_observed(obs, fixture=fixture, thread_id="run")
    paths = write_two(log_dir, fit=fit, live=not fixture)
    log_dir.mkdir(parents=True, exist_ok=True)
    report: dict[str, Any] = {
        "stage": "0" if fixture else "C",
        "fixture": fixture,
        "question": QUESTION,
        "contestant": "last_year",
        "bar": "mileage_plus_population",
        "ridge": False,
        "hgb": False,
        "sklearn_contestant": False,
        "live_retrac_login": False,
        "winter_page_hero": False,
        "xlsx_ok": True,
        "coords_ok": True,
        "parent_lock": PARENT_LOCK,
        "sheet_lock": SHEET_LOCK,
        "parent_citation": PARENT_CITATION,
        "units": {"skill": "rmse_tons"},
        "figures": paths,
        **{k: fit[k] for k in (
            "n_rows",
            "n_train",
            "n_holdout",
            "n_confirm",
            "n_facilities_j",
            "n_holdout_only_facilities",
            "n_point",
            "n_centroid",
            "holdout",
            "confirm",
            "confirm_in_train",
            "confirm_in_j",
            "confirm_reverses_holdout",
            "random_split",
            "train_years",
            "holdout_years",
            "confirm_years",
            "origin_pop_cancels",
            "last_year_beats_bar",
            "origin_key",
            "origin_name",
            "facility_set_j",
        )},
    }
    if extra:
        report.update(extra)
    payload = _jsonable(report)
    require_clean(payload["question"], source="report_question")
    require_clean(payload["holdout"]["cover"], source="report_cover")
    dest = log_dir / ("stage0_report.json" if fixture else "stage_c_report.json")
    dest.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    readme = REPO_ROOT / "README.md"
    require_paths_clean([readme, dest] if readme.is_file() else [dest])
    return report


def stage0_fixture(log_dir: Path) -> dict[str, Any]:
    rows, counties, facilities = build_fixture()
    return _run(log_dir, rows=rows, counties=counties, facilities=facilities, fixture=True)


def run_live(log_dir: Path, *, cache_dir: Path) -> dict[str, Any]:
    stage0 = REPO_ROOT / "logs" / "stage0_fixture" / "stage0_report.json"
    locked_live = (REPO_ROOT / "logs" / "in_live").resolve()
    obs = observe(
        REPO_ROOT,
        fixture=False,
        overwrite_frozen_sheet=log_dir.resolve() == locked_live,
        stage0_ok=stage0.is_file(),
    )
    require_observed(obs, fixture=False, thread_id="live")
    if not stage0.is_file():
        raise StageOrderError("Stage 0 fixture before live")
    rows, counties, facilities, meta = fetch_live(cache_dir=cache_dir)
    return _run(
        log_dir,
        rows=rows,
        counties=counties,
        facilities=facilities,
        fixture=False,
        extra={"fetch_meta": meta},
    )
