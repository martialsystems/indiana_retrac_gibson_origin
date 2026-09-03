# Copyright (c) 2026 Martial Systems LLC. All rights reserved.
"""RMSE tons. Last year vs mileage-plus-population. Origin pop cancels."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

import numpy as np

from gibson.config import MILE_EPS, ORIGIN_KEY, ORIGIN_NAME
from gibson.geo import miles
from gibson.split import CONFIRM, HOLDOUT, TRAIN, role


def _rmse(err: np.ndarray) -> float:
    if err.size == 0:
        return float("nan")
    return float(np.sqrt(np.mean(np.square(err))))


def _mae(err: np.ndarray) -> float:
    if err.size == 0:
        return float("nan")
    return float(np.mean(np.abs(err)))


def _finite(x: float) -> bool:
    return bool(np.isfinite(x))


def _share(part: float | None, total: float | None) -> float | None:
    if part is None or total is None or total == 0:
        return None
    return float(part) / float(total)


def cover_paragraph(hold: dict[str, Any]) -> str:
    ly = hold["last_year"]["rmse_tons"]
    bar = hold["bar"]["rmse_tons"]
    n = hold["n_last_year"]
    ot = hold["origin_total"]
    if hold["last_year_beats_bar"]:
        a = (
            f"Last year wins Gibson assignment on the intersection: RMSE {ly:.1f} tons "
            f"against mileage-plus-population {bar:.1f} (n={n})."
        )
    else:
        a = (
            f"Last year loses Gibson assignment on the intersection: RMSE {ly:.1f} tons "
            f"against mileage-plus-population {bar:.1f} (n={n})."
        )
    ly_tot = ot["last_year_rmse"]
    bar_tot = ot["bar_rmse"]
    if ly_tot is not None and _finite(ly_tot) and ly_tot > bar_tot:
        b = (
            f"Last year loses the observed Gibson quarterly total: RMSE {ly_tot:.1f} "
            f"against bar {bar_tot:.1f} (n={ot['n']})."
        )
    elif ly_tot is not None and _finite(ly_tot) and ly_tot < bar_tot:
        b = (
            f"Last year wins the observed Gibson quarterly total: RMSE {ly_tot:.1f} "
            f"against bar {bar_tot:.1f} (n={ot['n']})."
        )
    else:
        b = (
            f"Gibson quarterly-total last-year RMSE is {ly_tot} against bar {bar_tot} "
            f"(n={ot['n']})."
        )
    c = (
        "The bar is scaled to the observed Gibson quarterly total, so origin-total "
        "bar RMSE is 0 by construction. Do not average the two answers. Origin "
        "population cancels inside one origin’s shares."
    )
    return f"{a} {b} {c}"


def score(
    rows: list[dict[str, Any]],
    *,
    counties: dict[str, dict[str, Any]],
    facilities: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    keys = {r["origin_key"] for r in rows}
    if keys != {ORIGIN_KEY}:
        raise ValueError(f"this tree scores {ORIGIN_NAME} only, got {sorted(keys)}")
    origin = counties[ORIGIN_KEY]
    train = [r for r in rows if role(r["year"]) == TRAIN]
    hold = [r for r in rows if role(r["year"]) == HOLDOUT]
    confirm = [r for r in rows if role(r["year"]) == CONFIRM]
    j = {r["facility_id"] for r in train}
    confirm_in_train = any(role(r["year"]) == CONFIRM for r in train)
    confirm_in_j = confirm_in_train

    miles_w: dict[str, float] = {}
    pop_w: dict[str, float] = {}
    for fid in j:
        fac = facilities[fid]
        d = miles(origin["lat"], origin["lon"], fac["lat"], fac["lon"])
        miles_w[fid] = 1.0 / (d + MILE_EPS)
        pop_w[fid] = float(origin["pop_2020"]) / (d + MILE_EPS)
    miles_den = sum(miles_w.values())
    pop_den = sum(pop_w.values())
    shares_miles = {fid: (w / miles_den if miles_den else 0.0) for fid, w in miles_w.items()}
    shares_pop = {fid: (w / pop_den if pop_den else 0.0) for fid, w in pop_w.items()}
    origin_pop_cancels = all(abs(shares_pop[fid] - shares_miles[fid]) <= 1e-12 for fid in j)

    by_cell: dict[tuple[str, int, int], float] = {}
    origin_tot: dict[tuple[int, int], float] = defaultdict(float)
    names: dict[str, str] = {}
    for r in rows:
        by_cell[(r["facility_id"], r["year"], r["quarter"])] = r["tons"]
        origin_tot[(r["year"], r["quarter"])] += r["tons"]
        names[r["facility_id"]] = r["facility_name"]

    def _block(subset: list[dict[str, Any]]) -> dict[str, Any]:
        obs_ly: list[float] = []
        pred_ly: list[float] = []
        obs_bar_ix: list[float] = []
        pred_bar_ix: list[float] = []
        obs_bar: list[float] = []
        pred_bar: list[float] = []
        origin_obs: list[float] = []
        origin_ly: list[float] = []
        cells: list[dict[str, Any]] = []
        n_skip_ly = 0
        for r in subset:
            obs = float(r["tons"])
            fid = r["facility_id"]
            year = int(r["year"])
            q = int(r["quarter"])
            prev = by_cell.get((fid, year - 1, q))
            t_iq = origin_tot[(year, q)]
            t_prev = origin_tot.get((year - 1, q))
            w = pop_w.get(fid, 0.0)
            den = pop_den
            bar_share = (w / den) if den and fid in j else 0.0
            bar = t_iq * bar_share
            obs_bar.append(obs)
            pred_bar.append(bar)
            fac = facilities[fid]
            d = miles(origin["lat"], origin["lon"], fac["lat"], fac["lon"])
            cell = {
                "facility_id": fid,
                "facility_name": names.get(fid, fid),
                "year": year,
                "quarter": q,
                "tons_prior": float(prev) if prev is not None else None,
                "share_prior": _share(prev, t_prev),
                "tons": obs,
                "share": _share(obs, t_iq),
                "residual_tons": (obs - float(prev)) if prev is not None else None,
                "bar_share": bar_share if prev is not None else None,
                "bar_tons": bar,
                "miles": d,
                "how": fac["how"],
                "in_j": fid in j,
                "intersection": prev is not None,
            }
            cells.append(cell)
            if prev is None:
                n_skip_ly += 1
                continue
            obs_ly.append(obs)
            pred_ly.append(float(prev))
            obs_bar_ix.append(obs)
            pred_bar_ix.append(bar)

        seen_q: set[tuple[int, int]] = set()
        for r in subset:
            key = (int(r["year"]), int(r["quarter"]))
            if key in seen_q:
                continue
            seen_q.add(key)
            tot = origin_tot[key]
            prev_tot = origin_tot.get((key[0] - 1, key[1]))
            origin_obs.append(tot)
            origin_ly.append(float(prev_tot) if prev_tot is not None else float("nan"))

        ly_err = np.array(obs_ly, dtype=float) - np.array(pred_ly, dtype=float) if obs_ly else np.array([])
        bar_ix_err = (
            np.array(obs_bar_ix, dtype=float) - np.array(pred_bar_ix, dtype=float) if obs_bar_ix else np.array([])
        )
        bar_err = np.array(obs_bar, dtype=float) - np.array(pred_bar, dtype=float) if obs_bar else np.array([])
        o_obs = np.array(origin_obs, dtype=float)
        o_ly = np.array(origin_ly, dtype=float)
        mask = np.isfinite(o_ly) if o_ly.size else np.array([], dtype=bool)
        ly_rmse = _rmse(ly_err)
        bar_ix_rmse = _rmse(bar_ix_err)
        cells.sort(key=lambda c: (-c["tons"], c["quarter"], c["facility_id"]))
        dest = _destination_rank(subset, by_cell=by_cell, names=names)
        return {
            "n_cells": len(subset),
            "n_last_year": int(ly_err.size),
            "n_skip_last_year": n_skip_ly,
            "last_year": {"rmse_tons": ly_rmse, "mae_tons": _mae(ly_err)},
            "bar": {"rmse_tons": bar_ix_rmse, "mae_tons": _mae(bar_ix_err)},
            "bar_all": {"rmse_tons": _rmse(bar_err), "mae_tons": _mae(bar_err), "n": int(bar_err.size)},
            "origin_total": {
                "last_year_rmse": _rmse(o_obs[mask] - o_ly[mask]) if mask.size and mask.any() else None,
                "bar_rmse": 0.0,
                "n": int(mask.sum()) if mask.size else 0,
            },
            "last_year_beats_bar": bool(_finite(ly_rmse) and _finite(bar_ix_rmse) and ly_rmse < bar_ix_rmse),
            "cells": cells,
            "destinations": dest,
            "obs_ly": obs_ly,
            "pred_ly": pred_ly,
            "obs_bar": obs_bar_ix,
            "pred_bar": pred_bar_ix,
        }

    hold_s = _block(hold)
    conf_s = _block(confirm)
    hold_ids = {r["facility_id"] for r in hold}
    dest_set = {r["facility_id"] for r in rows}
    n_point = sum(1 for fid in dest_set if facilities[fid].get("how") == "point")
    n_centroid = sum(1 for fid in dest_set if facilities[fid].get("how") == "centroid")
    confirm_reverses = bool(hold_s["last_year_beats_bar"] != conf_s["last_year_beats_bar"])
    hold_s["cover"] = cover_paragraph(hold_s)
    return {
        "n_rows": len(rows),
        "n_train": len(train),
        "n_holdout": len(hold),
        "n_confirm": len(confirm),
        "n_facilities_j": len(j),
        "n_holdout_only_facilities": len(hold_ids - j),
        "n_point": n_point,
        "n_centroid": n_centroid,
        "holdout": hold_s,
        "confirm": conf_s,
        "confirm_in_train": confirm_in_train,
        "confirm_in_j": confirm_in_j,
        "confirm_reverses_holdout": confirm_reverses,
        "random_split": False,
        "train_years": [2021, 2022, 2023],
        "holdout_years": [2024],
        "confirm_years": [2025],
        "origin_pop_cancels": origin_pop_cancels,
        "last_year_beats_bar": hold_s["last_year_beats_bar"],
        "origin_key": ORIGIN_KEY,
        "origin_name": ORIGIN_NAME,
        "facility_set_j": sorted(j),
    }


def _destination_rank(
    subset: list[dict[str, Any]],
    *,
    by_cell: dict[tuple[str, int, int], float],
    names: dict[str, str],
) -> list[dict[str, Any]]:
    tons_now: dict[str, float] = defaultdict(float)
    years = {int(r["year"]) for r in subset}
    if not years:
        return []
    year = min(years)
    prior = year - 1
    for r in subset:
        tons_now[r["facility_id"]] += float(r["tons"])
    tot_now = sum(tons_now.values())
    tons_prior: dict[str, float] = defaultdict(float)
    for (fid, y, _q), tons in by_cell.items():
        if y == prior:
            tons_prior[fid] += float(tons)
    tot_prior = sum(tons_prior.values())
    fids = set(tons_now) | set(tons_prior)
    out = []
    for fid in fids:
        t = float(tons_now.get(fid, 0.0))
        tp = float(tons_prior.get(fid, 0.0))
        out.append(
            {
                "facility_id": fid,
                "facility_name": names.get(fid, fid),
                "tons": t,
                "share": _share(t, tot_now) if tot_now else None,
                "tons_prior": tp if fid in tons_prior else None,
                "share_prior": _share(tp, tot_prior) if fid in tons_prior and tot_prior else None,
            }
        )
    out.sort(key=lambda r: -r["tons"])
    return out
