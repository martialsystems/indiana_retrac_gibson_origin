# Copyright (c) 2026 Martial Systems LLC. All rights reserved.
"""Temporal split. Confirmation is out of train and out of facility set J."""

from __future__ import annotations

from gibson.config import CONFIRM_YEARS, HOLDOUT_YEARS, TRAIN_YEARS
from gibson.errors import SplitError

TRAIN = "train"
HOLDOUT = "holdout"
CONFIRM = "confirm"
OTHER = "other"


def role(year: int) -> str:
    y = int(year)
    if y in TRAIN_YEARS:
        return TRAIN
    if y in HOLDOUT_YEARS:
        return HOLDOUT
    if y in CONFIRM_YEARS:
        return CONFIRM
    return OTHER


def assert_split(*, confirm_in_train: bool, confirm_in_j: bool, random_split: bool) -> None:
    if confirm_in_train or confirm_in_j:
        raise SplitError("confirmation leaked into train or facility set J")
    if random_split:
        raise SplitError("random row split is refused")
