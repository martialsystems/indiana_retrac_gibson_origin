# Copyright (c) 2026 Martial Systems LLC. All rights reserved.
"""Buyer packet: operator PDF, 48-row CSV, five-line cover email."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from gibson.claims import require_clean
from gibson.config import QUESTION, REPO_ROOT

CSV_FIELDS = (
    "Q",
    "ID",
    "Facility",
    "2023 tons",
    "2023 share",
    "2024 tons",
    "2024 share",
    "Residual",
    "Bar share",
    "Loc",
)
PACKET_PDF = "gibson_origin_2024_sheet.pdf"
PACKET_CSV = "gibson_origin_2024_cells.csv"
COVER_EMAIL = "cover_email.txt"
SHARE_HOLD = 0.05


def _fmt(val: float | None, *, digits: int = 1, pct: bool = False) -> str:
    if val is None:
        return ""
    if pct:
        return f"{100.0 * float(val):.2f}%"
    return f"{float(val):,.{digits}f}"


def _csv_num(val: float | None, *, digits: int = 1, pct: bool = False) -> str:
    if val is None:
        return ""
    if pct:
        return f"{100.0 * float(val):.2f}"
    return f"{float(val):.{digits}f}"


def _display_name(name: str) -> str:
    s = (name or "").strip()
    if s.isupper() and len(s) > 4:
        return s.title()
    return s


def plant_sentences(hold: dict[str, Any]) -> str:
    dest = list(hold.get("destinations") or [])
    held = [
        d
        for d in dest
        if max(float(d.get("share") or 0), float(d.get("share_prior") or 0)) >= SHARE_HOLD
    ]
    appeared = [
        d
        for d in dest
        if d.get("share_prior") is None and float(d.get("tons") or 0) >= 100
    ]
    dropped = [d for d in dest if d.get("share") == 0.0 and d.get("share_prior") not in (None, 0)]
    held_txt = ", ".join(
        f"{_display_name(d['facility_name'])} ({100.0 * float(d['share_prior']):.1f}% in 2023, "
        f"{100.0 * float(d['share']):.1f}% in 2024)"
        for d in held
    )
    if not held_txt:
        held_txt = "none"
    appeared_named = [_display_name(d["facility_name"]) for d in appeared]
    dropped_named = [_display_name(d["facility_name"]) for d in dropped]
    moved = []
    if appeared_named:
        moved.append("new in 2024: " + ", ".join(appeared_named))
    if dropped_named:
        moved.append(
            "2023 destinations with no 2024 Gibson tons: " + ", ".join(dropped_named)
        )
    moved_txt = "; ".join(moved) if moved else "no material share moved off the held plant"
    return (
        f"Held share 5% or more: {held_txt}. "
        f"Share that moved: {moved_txt}."
    )


def packet_copy(report: dict[str, Any]) -> dict[str, str]:
    hold = report["holdout"]
    ly = hold["last_year"]["rmse_tons"]
    bar = hold["bar"]["rmse_tons"]
    n = hold["n_last_year"]
    ot = hold["origin_total"]
    who = (
        "Gibson County origin tons, 2024, versus 2023 same quarter. "
        "One origin. Held-out 2024."
    )
    cells = (
        f"Cells: last year {ly:.1f} tons RMSE against mileage-plus-population "
        f"{bar:.1f} on {n} cells."
    )
    total = (
        f"Total: last year misses the four quarter totals "
        f"(RMSE {float(ot['last_year_rmse']):.1f} tons). "
        "The bar is scaled to the observed total, so its total error is zero by construction."
    )
    plants = plant_sentences(hold)
    how = (
        "How to read a row: 2023 tons, 2023 share, 2024 tons, 2024 share, residual. "
        "A positive residual means 2024 sent more to that plant than 2023’s habit."
    )
    missing = (
        "What is missing. Miles: great-circle. Centroids: nine destinations sit on the "
        "host-county centroid. Out-of-state origins: dropped. County total: last year "
        "does not know 2024’s Gibson total."
    )
    source = (
        "Source: IDEM public quarterly reports, 2021 to 2025. "
        "This file is the join, not the state’s spreadsheet."
    )
    out = {
        "who": who,
        "cells": cells,
        "total": total,
        "plants": plants,
        "how": how,
        "missing": missing,
        "source": source,
    }
    for key, text in out.items():
        require_clean(text, source=f"packet_{key}")
    return out


def cover_email_text() -> str:
    lines = [
        "Gibson 2024 vs 2023 same-quarter destinations.",
        "Last year picks the plants better than miles.",
        "Last year does not pick this year’s tonnage.",
        "Table + CSV attached.",
        "Price is the sheet, not a subscription unless they ask.",
    ]
    text = "\n".join(lines) + "\n"
    require_clean(text, source="cover_email")
    return text


def write_cells_csv(dest: Path, *, hold: dict[str, Any]) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    rows = hold["cells"]
    with dest.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(CSV_FIELDS), extrasaction="raise")
        writer.writeheader()
        for c in rows:
            writer.writerow(
                {
                    "Q": str(c["quarter"]),
                    "ID": c["facility_id"],
                    "Facility": c["facility_name"],
                    "2023 tons": _csv_num(c["tons_prior"]),
                    "2023 share": _csv_num(c["share_prior"], pct=True),
                    "2024 tons": _csv_num(c["tons"]),
                    "2024 share": _csv_num(c["share"], pct=True),
                    "Residual": _csv_num(c["residual_tons"]),
                    "Bar share": _csv_num(c["bar_share"], pct=True) if c.get("intersection") else "",
                    "Loc": str(c["how"]),
                }
            )
    return dest


def write_cover_email(dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(cover_email_text(), encoding="utf-8")
    return dest


def write_sheet(dest: Path, *, report: dict[str, Any], log_dir: Path) -> Path:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import landscape, letter
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        Image,
        PageBreak,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    dest.parent.mkdir(parents=True, exist_ok=True)
    hold = report["holdout"]
    require_clean(QUESTION, source="question")
    fixture = bool(report.get("fixture"))

    styles = getSampleStyleSheet()
    title_s = ParagraphStyle(
        "SheetTitle",
        parent=styles["Heading1"],
        fontName="Times-Bold",
        fontSize=13,
        leading=16,
        spaceAfter=6,
        textColor=colors.HexColor("#111111"),
    )
    h2 = ParagraphStyle(
        "SheetH2",
        parent=styles["Heading2"],
        fontName="Times-Bold",
        fontSize=10,
        leading=13,
        spaceBefore=8,
        spaceAfter=4,
        textColor=colors.HexColor("#111111"),
    )
    body = ParagraphStyle(
        "SheetBody",
        parent=styles["BodyText"],
        fontName="Times-Roman",
        fontSize=8.5,
        leading=11,
        alignment=TA_LEFT,
        spaceAfter=4,
        textColor=colors.HexColor("#111111"),
    )
    small = ParagraphStyle(
        "SheetSmall",
        parent=body,
        fontSize=7.5,
        leading=9.5,
        spaceAfter=2,
    )
    cell_s = ParagraphStyle(
        "SheetCell",
        parent=body,
        fontSize=7,
        leading=9,
        spaceAfter=0,
    )
    bullet_s = ParagraphStyle(
        "SheetBullet",
        parent=body,
        fontSize=8.5,
        leading=11,
        leftIndent=8,
        spaceAfter=1,
    )

    story: list[Any] = [
        Paragraph("Gibson origin Re-TRAC sheet", title_s),
        Paragraph("2026-09-03. Gibson County, Indiana. Origin only.", body),
        Paragraph(QUESTION, body),
    ]
    if fixture:
        cover = str(hold["cover"])
        require_clean(cover, source="cover")
        story.append(Paragraph(cover, body))
        story.append(Paragraph("Fixture planted last-year persistence. Does not rescue live.", small))
    else:
        copy = packet_copy(report)
        story.append(Paragraph(copy["who"], body))
        story.append(Paragraph(copy["cells"], body))
        story.append(Paragraph(copy["total"], body))
        story.append(Paragraph(copy["plants"], body))
        story.append(Paragraph(copy["how"], body))
        story.append(Paragraph("What is missing", h2))
        story.append(Paragraph("Miles: great-circle.", bullet_s))
        story.append(Paragraph("Centroids: nine destinations sit on the host-county centroid.", bullet_s))
        story.append(Paragraph("Out-of-state origins: dropped.", bullet_s))
        story.append(Paragraph("County total: last year does not know 2024’s Gibson total.", bullet_s))
        story.append(Paragraph(copy["source"], body))

    story.append(Paragraph("Gibson 2024 reported cells", h2))
    header = [
        Paragraph("<b>Q</b>", cell_s),
        Paragraph("<b>ID</b>", cell_s),
        Paragraph("<b>Facility</b>", cell_s),
        Paragraph("<b>2023 tons</b>", cell_s),
        Paragraph("<b>2023 share</b>", cell_s),
        Paragraph("<b>2024 tons</b>", cell_s),
        Paragraph("<b>2024 share</b>", cell_s),
        Paragraph("<b>Residual</b>", cell_s),
        Paragraph("<b>Bar share</b>", cell_s),
        Paragraph("<b>Loc</b>", cell_s),
    ]
    data = [header]
    for c in hold["cells"]:
        data.append(
            [
                Paragraph(str(c["quarter"]), cell_s),
                Paragraph(c["facility_id"], cell_s),
                Paragraph(c["facility_name"], cell_s),
                Paragraph(_fmt(c["tons_prior"]), cell_s),
                Paragraph(_fmt(c["share_prior"], pct=True), cell_s),
                Paragraph(_fmt(c["tons"]), cell_s),
                Paragraph(_fmt(c["share"], pct=True), cell_s),
                Paragraph(_fmt(c["residual_tons"]), cell_s),
                Paragraph(_fmt(c["bar_share"], pct=True) if c.get("intersection") else "", cell_s),
                Paragraph(str(c["how"]), cell_s),
            ]
        )
    page_w, _page_h = landscape(letter)
    usable = page_w - 1.2 * inch
    widths = [
        0.05 * usable,
        0.08 * usable,
        0.27 * usable,
        0.10 * usable,
        0.09 * usable,
        0.10 * usable,
        0.09 * usable,
        0.10 * usable,
        0.07 * usable,
        0.05 * usable,
    ]
    grid = Table(data, colWidths=widths, repeatRows=1)
    grid.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#94a3b8")),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 3),
                ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )
    story.append(grid)
    story.append(
        Paragraph(
            "Bar share is on the intersection only (last year present). "
            "A sortable CSV of these 48 rows is the second file.",
            small,
        )
    )

    scatter = log_dir / "scatter.png"
    rank = log_dir / "dest_rank.png"
    if scatter.is_file() and rank.is_file():
        story.append(PageBreak())
        story.append(Paragraph("Figures", h2))
        img_w = 4.4 * inch
        story.append(Image(str(scatter), width=img_w, height=img_w * 0.97))
        story.append(
            Paragraph(
                "Figure 1. Gibson holdout cells. Last year vs mileage-plus-population. Tons of error.",
                small,
            )
        )
        story.append(Spacer(1, 6))
        story.append(Image(str(rank), width=img_w, height=img_w * 0.97))
        story.append(
            Paragraph(
                "Figure 2. 2023 share versus 2024 share by receiving facility. Rank of plants.",
                small,
            )
        )

    doc = SimpleDocTemplate(
        str(dest),
        pagesize=landscape(letter),
        leftMargin=0.55 * inch,
        rightMargin=0.55 * inch,
        topMargin=0.42 * inch,
        bottomMargin=0.42 * inch,
        title="Gibson origin Re-TRAC sheet",
        author="Martial Systems LLC",
    )
    doc.build(story)
    return dest


def _rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT.resolve()))
    except ValueError:
        return str(path)


def write_packet(*, report: dict[str, Any], log_dir: Path, dest_dir: Path | None = None) -> dict[str, str]:
    out = dest_dir or (REPO_ROOT / "delivery")
    out.mkdir(parents=True, exist_ok=True)
    pdf = write_sheet(out / PACKET_PDF, report=report, log_dir=log_dir)
    csv_path = write_cells_csv(out / PACKET_CSV, hold=report["holdout"])
    email = write_cover_email(out / COVER_EMAIL)
    return {"pdf": _rel(pdf), "csv": _rel(csv_path), "email": _rel(email)}
