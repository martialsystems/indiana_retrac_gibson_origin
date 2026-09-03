# Copyright (c) 2026 Martial Systems LLC

import json
from pathlib import Path

import numpy as np

from gibson.config import LIVE_SCATTER_SUBTITLE
from gibson.figure import fit_from_holdout, scatter_limits, write_scatter

REPO = Path(__file__).resolve().parents[1]


def test_live_scale_gap_gets_a_zoom() -> None:
    live = json.loads((REPO / "logs" / "in_live" / "stage_c_report.json").read_text(encoding="utf-8"))
    fit = fit_from_holdout(live["holdout"])
    h = fit["holdout"]
    full_hi, zoom_hi = scatter_limits(
        np.array(h["obs_ly"], dtype=float),
        np.array(h["pred_ly"], dtype=float),
        np.array(h["obs_bar"], dtype=float),
        np.array(h["pred_bar"], dtype=float),
    )
    assert full_hi > 200000
    assert zoom_hi < 50000
    assert zoom_hi < 0.2 * full_hi


def test_tight_scale_stays_one_panel(tmp_path: Path) -> None:
    fit = {
        "holdout": {
            "obs_ly": [10.0, 20.0, 30.0],
            "pred_ly": [11.0, 19.0, 28.0],
            "obs_bar": [10.0, 20.0, 30.0],
            "pred_bar": [12.0, 18.0, 25.0],
        }
    }
    full_hi, zoom_hi = scatter_limits(
        np.array(fit["holdout"]["obs_ly"]),
        np.array(fit["holdout"]["pred_ly"]),
        np.array(fit["holdout"]["obs_bar"]),
        np.array(fit["holdout"]["pred_bar"]),
    )
    assert zoom_hi == full_hi
    dest = write_scatter(
        tmp_path / "scatter.png",
        fit=fit,
        title="tight",
        subtitle="Fixture planted last-year persistence. Does not rescue live.",
    )
    assert dest.is_file()


def test_live_scatter_writes_two_panels(tmp_path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.image as mpimg

    live = json.loads((REPO / "logs" / "in_live" / "stage_c_report.json").read_text(encoding="utf-8"))
    dest = write_scatter(
        tmp_path / "scatter.png",
        fit=fit_from_holdout(live["holdout"]),
        title="Gibson holdout origin-facility-quarter tons",
        subtitle=LIVE_SCATTER_SUBTITLE,
    )
    img = mpimg.imread(dest)
    height, width = img.shape[0], img.shape[1]
    assert width > height * 1.3
