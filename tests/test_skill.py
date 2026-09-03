# Copyright (c) 2026 Martial Systems LLC

from gibson.fixture import build_fixture
from gibson.skill import score


def test_origin_pop_cancels_and_fixture_beats() -> None:
    rows, counties, facilities = build_fixture()
    fit = score(rows, counties=counties, facilities=facilities)
    assert fit["origin_key"] == "gibson"
    assert fit["origin_pop_cancels"] is True
    assert fit["last_year_beats_bar"] is True
    hold = fit["holdout"]
    assert hold["origin_total"]["bar_rmse"] == 0.0
    assert hold["origin_total"]["last_year_rmse"] > 0.0
    assert hold["n_skip_last_year"] > 0
    assert hold["last_year"]["rmse_tons"] < hold["bar"]["rmse_tons"]
    doubled = {k: {**v, "pop_2020": v["pop_2020"] * 10} for k, v in counties.items()}
    fit2 = score(rows, counties=doubled, facilities=facilities)
    assert abs(fit["holdout"]["bar"]["rmse_tons"] - fit2["holdout"]["bar"]["rmse_tons"]) < 1e-9
    assert all(c["origin_key"] == "gibson" for c in rows)
    assert "cover" in hold
    assert "Do not average" in hold["cover"]
