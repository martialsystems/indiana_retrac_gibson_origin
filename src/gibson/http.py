# Copyright (c) 2026 Martial Systems LLC. All rights reserved.
"""Injectable GET. Re-TRAC login URLs are refused."""

from __future__ import annotations

import time
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from gibson.config import RETRAC_LOGIN, USER_AGENT
from gibson.errors import ArchiveError, FetchError

GetBytes = Callable[[str], bytes]


def _forbid_login(url: str) -> None:
    if "re-trac.com" in url.lower() and "files/" not in url.lower():
        raise ArchiveError(f"live Re-TRAC login is not the science lock: {url}")
    if RETRAC_LOGIN in url:
        raise ArchiveError(f"live Re-TRAC login is not the science lock: {url}")


def get_bytes(url: str, *, timeout: int = 90, attempts: int = 6) -> bytes:
    _forbid_login(url)
    req = Request(url, headers={"User-Agent": USER_AGENT})
    last: BaseException | None = None
    for i in range(attempts):
        try:
            with urlopen(req, timeout=timeout) as resp:
                body = resp.read()
                if int(getattr(resp, "status", 200) or 200) == 404 or not body:
                    raise FetchError(f"GET empty or 404: {url}")
                return body
        except HTTPError as exc:
            last = exc
            if int(getattr(exc, "code", 0) or 0) == 404:
                raise FetchError(f"GET empty or 404: {url}") from exc
            if i == attempts - 1:
                raise FetchError(f"GET failed: {url}: {exc}") from exc
        except (URLError, TimeoutError, ConnectionResetError, ConnectionError) as exc:
            last = exc
            if i == attempts - 1:
                raise FetchError(f"GET failed: {url}: {exc}") from exc
        time.sleep(min(2 ** i, 8))
    raise FetchError(f"GET failed: {url}: {last}")
