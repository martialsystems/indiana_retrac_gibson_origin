# Copyright (c) 2026 Martial Systems LLC

import pytest

from gibson.errors import ArchiveError
from gibson.http import get_bytes


def test_retrac_login_refused() -> None:
    with pytest.raises(ArchiveError, match="live Re-TRAC login"):
        get_bytes("https://app.re-trac.com/")
    with pytest.raises(ArchiveError, match="live Re-TRAC login"):
        get_bytes("https://app.re-trac.com/login")
