# Copyright (c) 2026 Martial Systems LLC. All rights reserved.
"""One-origin fixture with planted last-year persistence. Does not rescue live."""

from __future__ import annotations

from typing import Any

import numpy as np


def build_fixture() -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    rng = np.random.default_rng(3)
    counties = {
        "gibson": {
            "name": "Gibson",
            "lat": 38.31,
            "lon": -87.62,
            "pop_2020": 33008,
            "fips": "18051",
            "key": "gibson",
        }
    }
    facilities = {
        "26-06": {"lat": 38.32, "lon": -87.63, "how": "point", "name": "Near Fill"},
        "84-06": {"lat": 39.50, "lon": -86.10, "how": "point", "name": "Far Fill"},
        "10-01": {"lat": 38.40, "lon": -85.80, "how": "centroid", "name": "New Fill"},
    }
    rows = []
    for year in (2021, 2022, 2023, 2024, 2025):
        base = 100.0 if year < 2024 else 150.0
        for q in (1, 2, 3, 4):
            noise = float(rng.normal(0, 1.5))
            t_near = max(0.0, 0.8 * base + noise)
            t_far = max(0.0, 0.2 * base - 0.3 * noise)
            rows.append(
                {
                    "origin_key": "gibson",
                    "origin_name": "Gibson",
                    "facility_id": "26-06",
                    "facility_name": facilities["26-06"]["name"],
                    "year": year,
                    "quarter": q,
                    "tons": t_near,
                }
            )
            rows.append(
                {
                    "origin_key": "gibson",
                    "origin_name": "Gibson",
                    "facility_id": "84-06",
                    "facility_name": facilities["84-06"]["name"],
                    "year": year,
                    "quarter": q,
                    "tons": t_far,
                }
            )
            if year >= 2024:
                rows.append(
                    {
                        "origin_key": "gibson",
                        "origin_name": "Gibson",
                        "facility_id": "10-01",
                        "facility_name": facilities["10-01"]["name"],
                        "year": year,
                        "quarter": q,
                        "tons": 4.0,
                    }
                )
    return rows, counties, facilities
