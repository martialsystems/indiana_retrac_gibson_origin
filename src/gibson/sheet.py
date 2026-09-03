# Copyright (c) 2026 Martial Systems LLC. All rights reserved.
"""Buyer packet: operator PDF, 48-row CSV, five-line cover email."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from gibson.claims import require_clean
from gibson.config import PACKET_FOOTNOTE, QUESTION, REPO_ROOT

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
COVER_LETTER = "cover_letter.txt"
LEAD_PLANTS = ("26-06", "63-04")
ONLY_2024_ORDER = (
    "87-13",
    "10-01",
    "42-09",
    "84-06",
    "32-02",
    "53-009",
    "49-066",
    "45-47",
)
TINY_DUAL_TONS = 100.0
BLANK = "\u00a0"


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
    if not (s.isupper() and len(s.split()) >= 3):
        return s
    keep = {"LLC", "INC", "LTD", "LP", "RWS", "CD", "EQ"}
    return " ".join(tok if tok in keep else tok.title() for tok in s.split())


def sort_cells(cells: list[dict[str, Any]]) -> list[dict[str, Any]]:
    from collections import defaultdict

    by_fid: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for c in cells:
        by_fid[c["facility_id"]].append(c)
    plant_tons = {fid: sum(float(r["tons"]) for r in rows) for fid, rows in by_fid.items()}
    has_prior = {
        fid: any(r.get("tons_prior") is not None for r in rows) for fid, rows in by_fid.items()
    }
    only_set = set(ONLY_2024_ORDER)

    def chrono(fid: str) -> list[dict[str, Any]]:
        return sorted(by_fid[fid], key=lambda r: int(r["quarter"]))

    out: list[dict[str, Any]] = []
    for fid in LEAD_PLANTS:
        if fid in by_fid:
            out.extend(chrono(fid))
            by_fid.pop(fid)
    dual: list[str] = []
    tiny: list[str] = []
    only: list[str] = []
    for fid in list(by_fid):
        if fid in only_set or not has_prior[fid]:
            only.append(fid)
        elif plant_tons[fid] < TINY_DUAL_TONS:
            tiny.append(fid)
        else:
            dual.append(fid)
    dual.sort(key=lambda f: -plant_tons[f])
    for fid in dual:
        out.extend(chrono(fid))
    only_named = [f for f in ONLY_2024_ORDER if f in by_fid]
    only_rest = sorted((f for f in only if f not in only_set), key=lambda f: -plant_tons[f])
    for fid in only_named + only_rest:
        out.extend(chrono(fid))
    tiny.sort(key=lambda f: -plant_tons[f])
    for fid in tiny:
        out.extend(chrono(fid))
    if len(out) != len(cells):
        raise ValueError(f"sort dropped rows: {len(out)} vs {len(cells)}")
    return out


def packet_copy(report: dict[str, Any]) -> dict[str, str]:
    hold = report["holdout"]
    ly = hold["last_year"]["rmse_tons"]
    bar = hold["bar"]["rmse_tons"]
    ot = hold["origin_total"]
    n_j = int(report.get("n_facilities_j") or 21)
    what = (
        "What this is. All reported Gibson-origin tons in 2024 versus the same quarter in 2023, "
        "as filed with IDEM. Permit 26-06 is Restricted Waste Site Type I at Gibson Generating "
        "Station South Landfill: on-site CCR and related industrial tons, not MSW. That door is "
        "97.8% of the file. One origin. Held-out 2024."
    )
    happened = (
        "What happened. 97.7% in 2023 and 97.8% in 2024 stayed on site at 26-06. The Q3 residual "
        "of +83,255 tons is more restricted-waste output at that landfill. Blackfoot (Pike County) "
        "is the largest remaining door, about 20,000 tons in 2024. Velpen C&D, Laubscher, "
        "Evansville Transfer, and Covanta follow. New in 2024 among the small remainder: "
        "Warrick Processing Center (Q2, 833 tons). Gone in 2024 (had Gibson tons in 2023, none "
        "in 2024): Bicknell Yard - Mullins Supply, Caldwell Environmental, Hoosier Landfill 2, "
        "EQ Industrial Services."
    )
    answers = (
        "Two answers, not averaged, on all reported tons including RWS Type I. Plants: last year "
        f"beats inverse-miles on the 35 cells where 2023 exists (RMSE {ly:,.1f} vs {bar:,.1f} tons). "
        f"The bar is inverse-miles among the {n_j} Gibson train destinations, not truck routing. "
        "It puts 72.43% on 26-06; actual is about 98%; last year copies 98%. County total: last year "
        f"misses the four 2024 quarter totals (RMSE {float(ot['last_year_rmse']):,.1f}). "
        "The miles bar is scaled to each quarter’s observed total, so its total error is zero "
        "by construction."
    )
    how = (
        "How to read a row. 2023 tons, 2023 share of that quarter, 2024 tons, 2024 share, "
        "residual. Residual = 2024 tons - 2023 same-quarter tons at that plant. It is not "
        "last year’s share applied to this year’s total. Q3 at 26-06 is +83,255 because "
        "restricted-waste tons at that site rose, not because a county MSW share moved."
    )
    # Unicode minus in residual formula trips nothing; punctuation rule prefers ASCII.
    how = how.replace(" − ", " - ")
    source = (
        "Source. IDEM public quarterly reports, 2021 to 2025. This file is the join. "
        "CSV of the same 48 rows is the second attachment."
    )
    note = (
        "Blank bar share means last year was missing, so that row is not in the 35-cell RMSE. "
        "Loc is point or centroid. Centroid = host-county centroid; 26-06 (the 98% plant) is a centroid."
    )
    out = {
        "what": what,
        "happened": happened,
        "answers": answers,
        "how": how,
        "source": source,
        "note": note,
        "footnote": PACKET_FOOTNOTE,
    }
    for key, text in out.items():
        require_clean(text, source=f"packet_{key}")
    return out


def cover_email_text() -> str:
    lines = [
        "All reported Gibson-origin tons, 2024 vs 2023 same quarter.",
        "97.8% is Restricted Waste Site Type I at Gibson Generating Station South Landfill.",
        "Last year beats miles on that door. Last year misses the quarterly total.",
        "Do not send this PDF to the county SWMD. A filtered MSW/C&D sheet would be a new question.",
        "Sheet lock c89de5b. Arithmetic stands. The customer was wrong.",
    ]
    text = "\n".join(lines) + "\n"
    require_clean(text, source="cover_email")
    return text


def cover_letter_text() -> str:
    text = (
        "Martial Systems LLC\n"
        "2026-09-03\n"
        "\n"
        "Operator memo. Do not send to Gibson County Solid Waste Management District.\n"
        "\n"
        "Re: Gibson origin Re-TRAC extract (all reported tons), sheet lock c89de5b\n"
        "\n"
        "The join is internally consistent. Origin = Gibson on the public IDEM quarterly "
        "waste-received file includes on-site restricted waste at permit 26-06, Gibson "
        "Generating Station South Landfill, Restricted Waste Site Type I. That door is 97.8% "
        "of 2024 Gibson-origin tons (97.7% in 2023). Parent lock 5800fc3 and this sheet lock "
        "scored all reported tons. They never said MSW-only.\n"
        "\n"
        "The mismatch is the customer. Binhack does not dispatch, budget, or take 26-06 CCR "
        "and FGD solids to the district board. The Q3 residual of +83,255 tons at 26-06 is "
        "plant output, not a fuller MSW day in Princeton. Do not email this PDF to "
        "gcsw@gibsoncounty-in.gov as Gibson County waste. Do not call the 98% persistence "
        "a district finding.\n"
        "\n"
        "Two answers, not averaged, on all reported tons. On the 35 cells where 2023 exists, "
        "last year beats inverse-miles (RMSE 15,596.8 vs 35,014.7 tons). Inverse-miles among "
        "the 21 Gibson train destinations puts 72.43% on 26-06; actual is about 98%; last year "
        "copies 98%. That win is real and almost mechanical for on-site RWS, not a SWMD routing "
        "result. On the four 2024 quarter totals, last year misses (RMSE 45,939.1). The miles "
        "bar is scaled to each quarter’s observed total, so its total error is zero by "
        "construction.\n"
        "\n"
        "What remains if 26-06 is dropped is about 2% of the tons: Blackfoot (MSW, Pike County, "
        "on the order of 5,000 tons a quarter), then Velpen C&D, Laubscher, Evansville Transfer, "
        "Covanta, and dust. That set would be a new object: Gibson-origin tons excluding RWS "
        "Type I, or MSW + transfer + C&D only. New question, new bar, new n. Do not sneak it "
        "into c89de5b. Parent 5800fc3 stays unfiltered and frozen.\n"
        "\n"
        "Loc: 26-06 is a host-county centroid. Miles to that site are wrong by construction. "
        "The 48-row table is all 2024 reported Gibson-origin cells, including RWS. Residual is "
        "2024 tons minus 2023 same-quarter tons at that plant.\n"
        "\n"
        "Packet files stay in delivery/ for the extract. Do not send them to gcsw@.\n"
        "\n"
        "Martial Systems LLC\n"
    )
    require_clean(text, source="cover_letter")
    return text


def write_cells_csv(dest: Path, *, hold: dict[str, Any]) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    rows = sort_cells(list(hold["cells"]))
    with dest.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(CSV_FIELDS), extrasaction="raise")
        writer.writeheader()
        for c in rows:
            writer.writerow(
                {
                    "Q": str(c["quarter"]),
                    "ID": c["facility_id"],
                    "Facility": _display_name(c["facility_name"]),
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


def write_cover_letter(dest: Path) -> Path:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(cover_letter_text(), encoding="utf-8")
    return dest


def _cell_para(text: str, style) -> Any:
    from reportlab.platypus import Paragraph

    return Paragraph(text if text else BLANK, style)


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
    story: list[Any] = [
        Paragraph("Gibson origin Re-TRAC sheet", title_s),
        Paragraph("2026-09-03. Gibson County, Indiana. Origin only.", body),
    ]
    copy: dict[str, str] | None = None
    if fixture:
        cover = str(hold["cover"])
        require_clean(cover, source="cover")
        story.append(Paragraph(cover, body))
        story.append(Paragraph("Fixture planted last-year persistence. Does not rescue live.", small))
        table_rows = list(hold["cells"])
    else:
        copy = packet_copy(report)
        story.append(Paragraph(copy["what"], body))
        story.append(Paragraph(copy["happened"], body))
        story.append(Paragraph(copy["answers"], body))
        story.append(Paragraph(copy["how"], body))
        story.append(Paragraph(copy["source"], body))
        table_rows = sort_cells(list(hold["cells"]))

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
        Paragraph("<b>point / centroid</b>", cell_s),
    ]
    data = [header]
    for c in table_rows:
        data.append(
            [
                _cell_para(str(c["quarter"]), cell_s),
                _cell_para(c["facility_id"], cell_s),
                _cell_para(_display_name(c["facility_name"]), cell_s),
                _cell_para(_fmt(c["tons_prior"]), cell_s),
                _cell_para(_fmt(c["share_prior"], pct=True), cell_s),
                _cell_para(_fmt(c["tons"]), cell_s),
                _cell_para(_fmt(c["share"], pct=True), cell_s),
                _cell_para(_fmt(c["residual_tons"]), cell_s),
                _cell_para(_fmt(c["bar_share"], pct=True) if c.get("intersection") else "", cell_s),
                _cell_para(str(c["how"]), cell_s),
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
    if copy is not None:
        story.append(Paragraph(copy["note"], small))
    else:
        story.append(
            Paragraph(
                "Bar share is on the intersection only (last year present).",
                small,
            )
        )

    scatter = log_dir / "scatter.png"
    rank = log_dir / "dest_rank.png"
    if scatter.is_file() and rank.is_file():
        story.append(PageBreak())
        img_w = 6.2 * inch
        story.append(Image(str(scatter), width=img_w, height=img_w * 0.92, hAlign="CENTER"))
        story.append(
            Paragraph(
                "Figure 1. Observed 2024 tons versus last year (orange) and inverse-miles (grey-blue). "
                "The four points on the right are 26-06, Restricted Waste Site Type I. Last year tracks "
                "that on-site door; miles sit low because they spread 27% of the bar to other doors.",
                small,
            )
        )
        story.append(PageBreak())
        story.append(Image(str(rank), width=img_w, height=img_w * 0.92, hAlign="CENTER"))
        story.append(
            Paragraph(
                "Figure 2. Each plant’s 2023 share vs 2024 share. 26-06 is the point at 0.98. "
                "Everything else is in the corner at 0. This is the monopoly chart.",
                small,
            )
        )

    def _first_page(canvas, doc) -> None:
        canvas.saveState()
        canvas.setFont("Times-Roman", 7)
        canvas.setFillColor(colors.HexColor("#475569"))
        canvas.drawString(0.55 * inch, 0.28 * inch, PACKET_FOOTNOTE if copy is not None else "")
        canvas.restoreState()

    doc = SimpleDocTemplate(
        str(dest),
        pagesize=landscape(letter),
        leftMargin=0.55 * inch,
        rightMargin=0.55 * inch,
        topMargin=0.42 * inch,
        bottomMargin=0.50 * inch,
        title="Gibson origin Re-TRAC sheet",
        author="Martial Systems LLC",
    )
    if copy is not None:
        doc.build(story, onFirstPage=_first_page)
    else:
        doc.build(story)
    return dest


def _rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT.resolve()))
    except ValueError:
        return str(path)


def write_packet(*, report: dict[str, Any], log_dir: Path, dest_dir: Path | None = None) -> dict[str, str]:
    from gibson.figure import write_packet_figures

    out = dest_dir or (REPO_ROOT / "delivery")
    out.mkdir(parents=True, exist_ok=True)
    if not report.get("fixture"):
        write_packet_figures(out, report["holdout"])
        fig_dir = out
    else:
        fig_dir = log_dir
    pdf = write_sheet(out / PACKET_PDF, report=report, log_dir=fig_dir)
    csv_path = write_cells_csv(out / PACKET_CSV, hold=report["holdout"])
    email = write_cover_email(out / COVER_EMAIL)
    letter = write_cover_letter(out / COVER_LETTER)
    return {
        "pdf": _rel(pdf),
        "csv": _rel(csv_path),
        "email": _rel(email),
        "letter": _rel(letter),
    }
