#!/usr/bin/env python3
# Copyright (c) 2026 Martial Systems LLC. All rights reserved.
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(REPO), str(REPO / "src")]

from gibsonforge._bootstrap import ensure_paths  # noqa: E402
from gibsonforge.gate import require_observed  # noqa: E402
from gibsonforge.observe import observe  # noqa: E402


def main() -> int:
    gf = ensure_paths()
    import graphforge
    from graphforge.consumer_gate import discover_product_laws
    from graphforge.product_law import require_law

    print(f"graphforge {getattr(graphforge, '__version__', '?')} @ {gf}")
    for law in discover_product_laws(REPO / "gibsonforge"):
        build = law.get("build") or law.get("builder")
        if not callable(build):
            continue
        require_law(
            build(),
            dict(law.get("state") or {}),
            allow_decisions=law.get("allow_decisions"),
            law_id=str(law.get("id") or "gibson_law"),
            thread_id=f"sanity_{law.get('id')}",
            raise_error=True,
        )
    obs = observe(REPO, fixture=False, overwrite_frozen_sheet=False)
    require_observed(obs, fixture=False, thread_id="sanity_live")
    print("product_laws: OK")
    print(
        "observed",
        {k: obs[k] for k in (
            "stage0_ok",
            "answers_averaged",
            "readme_has_county_rows",
            "gibson_table_outside_pdf",
            "buyer_pdf_missing",
            "parent_restamped",
            "sheet_restamped",
            "overwrite_frozen_sheet",
        )},
    )
    tr = subprocess.run(
        [sys.executable, "-m", "pytest", str(REPO / "tests" / "test_gibsonforge_laws.py"), "-q"],
        cwd=str(REPO),
        check=False,
    )
    return tr.returncode


if __name__ == "__main__":
    raise SystemExit(main())
