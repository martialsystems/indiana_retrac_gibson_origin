# Copyright (c) 2026 Martial Systems LLC
"""One figure: holdout scatter, full scale plus zoom on the small cells."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
from matplotlib.patches import Rectangle

from gibson.claims import require_clean
from gibson.config import (
    FIXTURE_SCATTER_SUBTITLE,
    LIVE_SCATTER_SUBTITLE,
    MAX_FIGURES,
)
from gibson.errors import FigureCapError, GateError


def _cap(n: int) -> None:
    if n > MAX_FIGURES:
        raise FigureCapError(f"this tree stops at {MAX_FIGURES} figures")


def _arr(hold: dict[str, Any], key: str) -> np.ndarray:
    return np.array(hold.get(key) or [], dtype=float)


def scatter_limits(*arrs: np.ndarray) -> tuple[float, float]:
    """Full-axis hi, and a zoom hi below the largest gap when one exists."""
    chunks = [a[np.isfinite(a) & (a >= 0)] for a in arrs if a.size]
    if not chunks:
        return 1.0, 1.0
    vals = np.concatenate(chunks)
    hi = float(vals.max()) if vals.size else 1.0
    if hi <= 0:
        return 1.0, 1.0
    uniq = np.unique(vals)
    if uniq.size < 4:
        return hi, hi
    gaps = np.diff(uniq)
    i = int(np.argmax(gaps))
    if gaps[i] < max(float(uniq[i]) * 2.0, 1.0):
        return hi, hi
    zoom = float(uniq[i] * 1.15)
    if zoom >= 0.5 * hi:
        return hi, hi
    return hi, max(zoom, 1.0)


def fit_from_holdout(hold: dict[str, Any]) -> dict[str, Any]:
    """Rebuild plot arrays from frozen cells. Does not call score()."""
    ix = [
        c
        for c in hold.get("cells") or []
        if c.get("intersection") and c.get("tons_prior") is not None
    ]
    return {
        "holdout": {
            "obs_ly": [float(c["tons"]) for c in ix],
            "pred_ly": [float(c["tons_prior"]) for c in ix],
            "obs_bar": [float(c["tons"]) for c in ix],
            "pred_bar": [float(c["bar_tons"]) for c in ix],
            "destinations": list(hold.get("destinations") or []),
        }
    }


def _draw_panel(
    ax: Any,
    *,
    obs_ly: np.ndarray,
    pred_ly: np.ndarray,
    obs_bar: np.ndarray,
    pred_bar: np.ndarray,
    hi: float,
    legend: bool,
) -> None:
    ax.scatter(obs_bar, pred_bar, s=18, c="#64748b", alpha=0.55, label="mileage-plus-population")
    ax.scatter(obs_ly, pred_ly, s=22, c="#b45309", alpha=0.8, marker="x", label="last year")
    ax.plot([0, hi], [0, hi], color="#0f172a", lw=1.0, label="1:1")
    ax.set_xlim(0, hi)
    ax.set_ylim(0, hi)
    ax.set_xlabel("observed tons")
    ax.set_ylabel("predicted tons")
    if legend:
        ax.legend(fontsize=7, loc="upper left")


def write_scatter(dest: Path, *, fit: dict[str, Any], title: str, subtitle: str) -> Path:
    require_clean(title, source="fig1_title")
    require_clean(subtitle, source="fig1_sub")
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    h = fit["holdout"]
    obs_ly = _arr(h, "obs_ly")
    pred_ly = _arr(h, "pred_ly")
    obs_bar = _arr(h, "obs_bar")
    pred_bar = _arr(h, "pred_bar")
    full_hi, zoom_hi = scatter_limits(obs_ly, pred_ly, obs_bar, pred_bar)
    two = zoom_hi < 0.5 * full_hi
    if two:
        fig, axes = plt.subplots(1, 2, figsize=(11.2, 5.6))
        _draw_panel(
            axes[0],
            obs_ly=obs_ly,
            pred_ly=pred_ly,
            obs_bar=obs_bar,
            pred_bar=pred_bar,
            hi=full_hi,
            legend=True,
        )
        axes[0].add_patch(
            Rectangle(
                (0, 0),
                zoom_hi,
                zoom_hi,
                fill=False,
                ls="--",
                lw=0.9,
                edgecolor="#0f172a",
            )
        )
        axes[0].set_title("full scale", fontsize=9)
        _draw_panel(
            axes[1],
            obs_ly=obs_ly,
            pred_ly=pred_ly,
            obs_bar=obs_bar,
            pred_bar=pred_bar,
            hi=zoom_hi,
            legend=False,
        )
        axes[1].set_title("zoom", fontsize=9)
    else:
        fig, ax = plt.subplots(figsize=(6.4, 6.2))
        _draw_panel(
            ax,
            obs_ly=obs_ly,
            pred_ly=pred_ly,
            obs_bar=obs_bar,
            pred_bar=pred_bar,
            hi=full_hi,
            legend=True,
        )
    fig.suptitle(title, fontsize=11)
    fig.subplots_adjust(bottom=0.18, top=0.88, wspace=0.28)
    fig.text(0.5, 0.04, subtitle, ha="center", fontsize=8)
    dest.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(dest, dpi=130, bbox_inches="tight", pad_inches=0.18)
    plt.close(fig)
    return dest


def write_two(log_dir: Path, *, fit: dict[str, Any], live: bool) -> list[str]:
    _cap(1)
    log_dir.mkdir(parents=True, exist_ok=True)
    a = write_scatter(
        log_dir / "scatter.png",
        fit=fit,
        title="Gibson holdout origin-facility-quarter tons",
        subtitle=LIVE_SCATTER_SUBTITLE if live else FIXTURE_SCATTER_SUBTITLE,
    )
    leftover = log_dir / "dest_rank.png"
    if leftover.is_file():
        leftover.unlink()
    paths = [a]
    _cap(len(paths))
    return [p.name for p in paths]


def write_live_scatter_from_frozen(repo: Path) -> Path:
    """Restyle logs/in_live/scatter.png from frozen cells. Does not rescore."""
    import json

    from gibsonforge.observe import sheet_drifted

    live_dir = repo / "logs" / "in_live"
    report = json.loads((live_dir / "stage_c_report.json").read_text(encoding="utf-8"))
    if sheet_drifted(report):
        raise GateError("refusing figure rebuild: live JSON drifted from lock")
    fit = fit_from_holdout(report["holdout"])
    dest = write_scatter(
        live_dir / "scatter.png",
        fit=fit,
        title="Gibson holdout origin-facility-quarter tons",
        subtitle=LIVE_SCATTER_SUBTITLE,
    )
    leftover = live_dir / "dest_rank.png"
    if leftover.is_file():
        leftover.unlink()
    return dest
