# Copyright (c) 2026 Martial Systems LLC. All rights reserved.

import pytest

from gibson.claims import require_clean, scan_text
from gibson.errors import ClaimBanError


def test_allowed_and_banned() -> None:
    assert scan_text("last year RMSE vs mileage-plus-population. Tons of error.") == []
    assert "will_get_tons" in scan_text("Marion will get 20 tons")
    assert "casualty" in scan_text("casualties from landfill siting")
    assert "em_dash" in scan_text("skill — not a forecast")
    assert "climate_attr" in scan_text("attributed to climate change")
    assert "pop_at_risk" in scan_text("population at risk in the floodplain")
    assert "logistics_opt" in scan_text("logistics optimized for Gibson")
    assert "truck_routing" in scan_text("truck routing to the plant")
    assert "truck_routing" not in scan_text("inverse-miles, not truck routing")
    assert "next_year_forecast" in scan_text("next-year forecast of Gibson tons")
    with pytest.raises(ClaimBanError):
        require_clean("will get 12 tons next quarter", source="t")
