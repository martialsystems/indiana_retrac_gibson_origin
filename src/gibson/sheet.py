# Copyright (c) 2026 Martial Systems LLC. All rights reserved.
"""Buyer PDF: cover paragraph, one table, two figures. Not a git clone."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from gibson.claims import require_clean
from gibson.config import PARENT_CITATION, PARENT_LOCK, QUESTION
from gibson.errors import FetchError


def _fmt(val: float | None, *, digits: int = 1, pct: bool = False) -> str:
    if val is None:
        return ""
    if pct:
        return f"{100.0 * float(val):.2f}%"
    return f"{float(val):,.{digits}f}"


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
    cover = str(hold["cover"])
    require_clean(cover, source="cover")
    require_clean(QUESTION, source="question")
    crs = (report.get("fetch_meta") or {}).get("crs") or {}
    if report.get("fixture"):
        crs_line = "Fixture coordinates are planted lon/lat. Live CRS is logged on the buyer sheet."
    else:
        if not crs or not crs.get("facilities_geojson"):
            raise FetchError("missing CRS on live sheet")
        crs_line = (
            f"CRS: facilities {crs.get('facilities_geojson')}, counties {crs.get('counties')}, "
            f"warp {crs.get('warp')}, GIS outSR={crs.get('gis_query_outSR')}."
        )
    require_clean(crs_line, source="crs")

    styles = getSampleStyleSheet()
    title_s = ParagraphStyle(
        "SheetTitle",
        parent=styles["Heading1"],
        fontName="Times-Bold",
        fontSize=14,
        leading=18,
        spaceAfter=8,
        textColor=colors.HexColor("#111111"),
    )
    h2 = ParagraphStyle(
        "SheetH2",
        parent=styles["Heading2"],
        fontName="Times-Bold",
        fontSize=11,
        leading=14,
        spaceBefore=10,
        spaceAfter=6,
        textColor=colors.HexColor("#111111"),
    )
    body = ParagraphStyle(
        "SheetBody",
        parent=styles["BodyText"],
        fontName="Times-Roman",
        fontSize=9,
        leading=12,
        alignment=TA_LEFT,
        spaceAfter=6,
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

    parent = PARENT_CITATION
    g = parent["gibson_statewide_j"]
    parent_txt = (
        f"Statewide baseline citation, parent {PARENT_LOCK}: last year wins assignment on "
        f"intersection cells (RMSE {parent['intersection_last_year_rmse']} vs "
        f"{parent['intersection_bar_rmse']}, n={parent['n_intersection']}); last year loses "
        f"origin-quarter totals ({parent['origin_total_last_year_rmse']} vs "
        f"{parent['origin_total_bar_rmse']}, bar scaled to the observed county total). "
        f"That lock’s Gibson row used statewide facility set J: last-year RMSE {g['last_year_rmse']} "
        f"vs bar {g['bar_rmse']}; holdout tons {g['holdout_tons']}; n={g['n']}. This sheet "
        f"restricts J to Gibson train-era destinations. Do not promote the statewide win."
    )
    require_clean(parent_txt, source="parent")

    residual = (
        f"Residuals stay residual. Miles are great-circle, not road miles. "
        f"n_point={report['n_point']}, n_centroid={report['n_centroid']} on the Gibson "
        f"destination set. 2024-only facilities have bar mass 0. Out-of-state origins are "
        f"dropped. Confirmation 2025 is out of train and out of J"
        f"{'; it reverses the holdout cell sign' if report.get('confirm_reverses_holdout') else '; it does not reopen this sheet'}."
    )
    require_clean(residual, source="residual")

    story: list[Any] = [
        Paragraph("Gibson origin Re-TRAC sheet", title_s),
        Paragraph("2026-09-03. One origin. Buyer file, not a git clone.", body),
        Paragraph(QUESTION, body),
        Paragraph(cover, body),
        Paragraph(parent_txt, body),
        Paragraph(crs_line, body),
        Paragraph(residual, body),
        Paragraph("Gibson 2024 reported cells", h2),
    ]

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
                Paragraph(_fmt(c["bar_share"], pct=True) if c["intersection"] else "", cell_s),
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
            "Bar-on-all-reported-Gibson-cells is a second line in the JSON, not mixed into the win.",
            small,
        )
    )

    scatter = log_dir / "scatter.png"
    rank = log_dir / "dest_rank.png"
    if scatter.is_file() and rank.is_file():
        story.append(PageBreak())
        story.append(Paragraph("Figures", h2))
        img_w = 4.6 * inch
        story.append(Image(str(scatter), width=img_w, height=img_w * 0.97))
        story.append(Paragraph("Figure 1. Gibson holdout cells. Last year vs mileage-plus-population. Tons of error.", small))
        story.append(Spacer(1, 8))
        story.append(Image(str(rank), width=img_w, height=img_w * 0.97))
        story.append(
            Paragraph(
                "Figure 2. 2023 share versus 2024 share by receiving facility. Rank of plants.",
                small,
            )
        )

    story.append(Paragraph("Revisions", h2))
    story.append(Paragraph("2026-09-03: first Gibson origin sheet from public IDEM waste-received XLSX.", small))

    doc = SimpleDocTemplate(
        str(dest),
        pagesize=landscape(letter),
        leftMargin=0.6 * inch,
        rightMargin=0.6 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
        title="Gibson origin Re-TRAC sheet",
        author="Martial Systems LLC",
    )
    doc.build(story)
    return dest
