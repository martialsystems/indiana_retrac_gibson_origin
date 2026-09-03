# Copyright (c) 2026 Martial Systems LLC. All rights reserved.
"""Two figures: holdout scatter, destination rank (2023 share vs 2024 share)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from gibson.claims import require_clean
from gibson.config import (
    FIXTURE_RANK_SUBTITLE,
    FIXTURE_SCATTER_SUBTITLE,
    LIVE_RANK_SUBTITLE,
    LIVE_SCATTER_SUBTITLE,
    MAX_FIGURES,
    PACKET_RANK_SUBTITLE,
    PACKET_RANK_TITLE,
    PACKET_SCATTER_SUBTITLE,
    PACKET_SCATTER_TITLE,
)
from gibson.errors import FigureCapError


def _cap(n: int) -> None:
    if n > MAX_FIGURES:
        raise FigureCapError(f"this tree stops at {MAX_FIGURES} figures")


def write_scatter(dest: Path, *, fit: dict[str, Any], title: str, subtitle: str) -> Path:
    require_clean(title, source="fig1_title")
    require_clean(subtitle, source="fig1_sub")
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    h = fit["holdout"]
    fig, ax = plt.subplots(figsize=(6.4, 6.2))
    obs_ly = np.array(h["obs_ly"], dtype=float)
    pred_ly = np.array(h["pred_ly"], dtype=float)
    obs_bar = np.array(h["obs_bar"], dtype=float)
    pred_bar = np.array(h["pred_bar"], dtype=float)
    ax.scatter(obs_bar, pred_bar, s=18, c="#64748b", alpha=0.55, label="mileage-plus-population")
    ax.scatter(obs_ly, pred_ly, s=22, c="#b45309", alpha=0.8, marker="x", label="last year")
    hi = float(
        np.nanmax(
            [
                obs_bar.max() if obs_bar.size else 0,
                pred_bar.max() if pred_bar.size else 0,
                obs_ly.max() if obs_ly.size else 0,
                pred_ly.max() if pred_ly.size else 0,
            ]
            or [1.0]
        )
    )
    ax.plot([0, hi], [0, hi], color="#0f172a", lw=1.0, label="1:1")
    ax.set_xlabel("observed tons")
    ax.set_ylabel("predicted tons")
    ax.legend(fontsize=7, loc="upper left")
    fig.suptitle(title, fontsize=11)
    fig.subplots_adjust(bottom=0.18, top=0.90)
    fig.text(0.5, 0.04, subtitle, ha="center", fontsize=8)
    dest.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(dest, dpi=130, bbox_inches="tight", pad_inches=0.18)
    plt.close(fig)
    return dest


def write_rank(dest: Path, *, fit: dict[str, Any], title: str, subtitle: str) -> Path:
    require_clean(title, source="fig2_title")
    require_clean(subtitle, source="fig2_sub")
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    rows = [
        r
        for r in fit["holdout"]["destinations"]
        if r.get("share") is not None and r.get("share_prior") is not None
    ]
    fig, ax = plt.subplots(figsize=(6.4, 6.2))
    x = np.array([r["share_prior"] for r in rows], dtype=float)
    y = np.array([r["share"] for r in rows], dtype=float)
    ax.scatter(x, y, s=28, c="#b45309", alpha=0.85, zorder=3)
    hi = float(np.nanmax([x.max() if x.size else 0, y.max() if y.size else 0, 0.05]))
    ax.plot([0, hi], [0, hi], color="#0f172a", lw=1.0, label="1:1")
    labeled = [
        r
        for r in rows
        if max(float(r["share"] or 0), float(r["share_prior"] or 0)) >= 0.05
    ]
    for r in labeled:
        ax.annotate(
            r["facility_id"],
            (r["share_prior"], r["share"]),
            textcoords="offset points",
            xytext=(6, -4),
            fontsize=8,
        )
    ax.set_xlabel("2023 share")
    ax.set_ylabel("2024 share")
    ax.legend(fontsize=7, loc="upper left")
    fig.suptitle(title, fontsize=11)
    fig.subplots_adjust(bottom=0.18, top=0.90)
    fig.text(0.5, 0.04, subtitle, ha="center", fontsize=8)
    dest.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(dest, dpi=130, bbox_inches="tight", pad_inches=0.18)
    plt.close(fig)
    return dest


def write_two(log_dir: Path, *, fit: dict[str, Any], live: bool) -> list[str]:
    _cap(2)
    log_dir.mkdir(parents=True, exist_ok=True)
    a = write_scatter(
        log_dir / "scatter.png",
        fit=fit,
        title="Gibson holdout origin-facility-quarter tons",
        subtitle=LIVE_SCATTER_SUBTITLE if live else FIXTURE_SCATTER_SUBTITLE,
    )
    b = write_rank(
        log_dir / "dest_rank.png",
        fit=fit,
        title="Gibson destination rank, 2023 share vs 2024 share",
        subtitle=LIVE_RANK_SUBTITLE if live else FIXTURE_RANK_SUBTITLE,
    )
    paths = [a, b]
    _cap(len(paths))
    return [p.name for p in paths]


def _fit_from_frozen_cells(hold: dict[str, Any]) -> dict[str, Any]:
    ix = [c for c in hold.get("cells") or [] if c.get("intersection") and c.get("tons_prior") is not None]
    return {
        "holdout": {
            "obs_ly": [float(c["tons"]) for c in ix],
            "pred_ly": [float(c["tons_prior"]) for c in ix],
            "obs_bar": [float(c["tons"]) for c in ix],
            "pred_bar": [float(c["bar_tons"]) for c in ix],
            "destinations": list(hold.get("destinations") or []),
        }
    }


def write_packet_figures(dest_dir: Path, hold: dict[str, Any]) -> list[str]:
    """Rebuild packet figures from frozen cells. Does not call score()."""
    fit = _fit_from_frozen_cells(hold)
    _cap(2)
    dest_dir.mkdir(parents=True, exist_ok=True)
    a = write_scatter(
        dest_dir / "scatter.png",
        fit=fit,
        title=PACKET_SCATTER_TITLE,
        subtitle=PACKET_SCATTER_SUBTITLE,
    )
    b = write_rank(
        dest_dir / "dest_rank.png",
        fit=fit,
        title=PACKET_RANK_TITLE,
        subtitle=PACKET_RANK_SUBTITLE,
    )
    _cap(2)
    return [a.name, b.name]
