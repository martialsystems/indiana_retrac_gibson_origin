# Copyright (c) 2026 Martial Systems LLC

import pytest

from gibson.errors import SplitError
from gibson.split import CONFIRM, HOLDOUT, TRAIN, assert_split, role


def test_pinned_years() -> None:
    assert role(2021) == TRAIN
    assert role(2023) == TRAIN
    assert role(2024) == HOLDOUT
    assert role(2025) == CONFIRM
    assert role(2020) == "other"


def test_confirm_leak_refused() -> None:
    with pytest.raises(SplitError):
        assert_split(confirm_in_train=True, confirm_in_j=False, random_split=False)
    with pytest.raises(SplitError):
        assert_split(confirm_in_train=False, confirm_in_j=True, random_split=False)
    with pytest.raises(SplitError):
        assert_split(confirm_in_train=False, confirm_in_j=False, random_split=True)
