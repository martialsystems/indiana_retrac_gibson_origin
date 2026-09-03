# Copyright (c) 2026 Martial Systems LLC
"""Locked Gibson-origin last year vs origin-pop / miles."""

from __future__ import annotations

from pathlib import Path

QUESTION = (
    "For waste that originated in Gibson County, Indiana, does "
    '"same facility, same quarter, last year" beat a simple '
    "distance-weighted split of this year’s total when you hold out 2024?"
)
ORIGIN_KEY = "gibson"
ORIGIN_NAME = "Gibson"
USER_AGENT = "MartialSystemsResearch/indiana_retrac_gibson_origin"
MAX_FIGURES = 2
MILE_EPS = 1.0
EARTH_MI = 3958.7613
REQUIRED_CRS = "EPSG:4326"

TRAIN_YEARS = (2021, 2022, 2023)
HOLDOUT_YEARS = (2024,)
CONFIRM_YEARS = (2025,)

TON_COLS = (
    "Municipal Solid Waste",
    "Construction/Demolition",
    "Foundry",
    "Coal Ash",
    "Flue Gas Desulfurization Waste",
    "Other Non-Municipal",
    "Alternate Daily Cover/Reuse",
)

IDEM_XLSX_URL = "https://www.in.gov/idem/waste/files/reporting_sw_quarterly_report_2025.xlsx"
GIS_URL = (
    "https://gisdata.in.gov/server/rest/services/Hosted/"
    "Authorized_Operating_Solid_Waste_Facilities/FeatureServer/2120/query"
    "?where=1%3D1&outFields=sw_program_id,facility_name,county,facility_type"
    "&returnGeometry=true&outSR=4326&f=geojson"
)
RETRAC_LOGIN = "https://app.re-trac.com/"

REPO_ROOT = Path(__file__).resolve().parents[2]
INDEX_GIST = "https://gist.github.com/martialsystems/66b896b0a4a0b8cba2b478aef64312f3"
MAPS_GIST = "https://gist.github.com/martialsystems/16584e78d079666f7e8994b4cc6158be"
PARENT_REPO = "https://github.com/martialsystems/indiana_retrac_last_year"
PARENT_LOCK = "5800fc3"
SHEET_LOCK = "c89de5b"

# Statewide baseline citation only. Do not recompute. Do not restamp 5800fc3.
PARENT_CITATION = {
    "sha": PARENT_LOCK,
    "repo": PARENT_REPO,
    "intersection_last_year_rmse": 6504.7,
    "intersection_bar_rmse": 16633.0,
    "n_intersection": 4370,
    "origin_total_last_year_rmse": 23313.3,
    "origin_total_bar_rmse": 0.0,
    "gibson_statewide_j": {
        "last_year_rmse": 15597,
        "bar_rmse": 76281,
        "holdout_tons": 1540946,
        "n": 35,
    },
}

# Frozen live skill at SHEET_LOCK. One-decimal tons, as the README.
SHEET_HOLDOUT = {
    "last_year_rmse": 15596.8,
    "bar_rmse": 35014.7,
    "origin_total_last_year_rmse": 45939.1,
    "origin_total_bar_rmse": 0.0,
    "n_intersection": 35,
    "n_cells": 48,
    "n_origin_total": 4,
}

LIVE_SCATTER_SUBTITLE = (
    "Gibson holdout cells. Last year vs mileage-plus-population. Tons of error."
)
LIVE_RANK_SUBTITLE = (
    "2023 share versus 2024 share by receiving facility. Rank of plants."
)
FIXTURE_SCATTER_SUBTITLE = "Fixture planted last-year persistence. Does not rescue live."
FIXTURE_RANK_SUBTITLE = "Fixture destination shares. Does not rescue live."

# Public README must ship these three. Omitting the third republishes the SWMD mistake.
THREE_SENTENCES = (
    "Last year wins the cell-by-cell assignment.",
    "It loses the quarterly totals (because the distance model is forced to hit this year’s total exactly).",
    "97.8% of 2024 reported Gibson-origin tons went to 26-06, Restricted Waste Site Type I (Duke CCR), not an MSW landfill.",
)
TYPE_OVERRIDE = {
    "26-06": "Restricted Waste Site Type I (Duke CCR)",
}
