# Copyright (c) 2026 Martial Systems LLC. All rights reserved.

import pytest

from gibson.errors import FetchError
from gibson.geo import crs_name, miles, require_lonlat_crs


def test_miles_zero_and_known() -> None:
    assert miles(40.0, -86.0, 40.0, -86.0) == 0.0
    d = miles(39.7683, -86.1581, 41.6764, -86.2500)
    assert 120 < d < 140


def test_missing_crs_refused() -> None:
    with pytest.raises(FetchError, match="missing CRS"):
        crs_name(None)
    with pytest.raises(FetchError, match="missing CRS"):
        crs_name({"type": "name", "properties": {}})
    with pytest.raises(FetchError, match="refused CRS"):
        require_lonlat_crs("EPSG:5070")
    assert require_lonlat_crs("urn:ogc:def:crs:EPSG::4326") == "EPSG:4326"
