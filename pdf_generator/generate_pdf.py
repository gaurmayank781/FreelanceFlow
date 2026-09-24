"""
PDF Report Generator
----------------------
Turns a CSV file into a formatted PDF report: title, generated timestamp,
and a styled table with alternating row colors.

Usage:
    python generate_pdf.py --input sales.csv --output report.pdf
    python generate_pdf.py --input sales.csv --output report.pdf --title "Q1 Sales Report"
"""

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core.io_utils import read_csv_safe  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

HEADER_COLOR = colors.HexColor("#1F4E78")
ALT_ROW_COLOR = colors.HexColor("#F2F2F2")


def generate_pdf(input_path: Path, output_path: Path, title: str = "Report") -> dict:
    """
    Build a formatted PDF table report from a CSV file.

    Returns a summary dict: rows written, columns included.
    """
    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {input_path}")

    df = read_csv_safe(input_path)
    if df.empty:
        raise ValueError(f"No data found in {input_path}")

    doc = SimpleDocTemplate(str(output_path), pagesize=A4,
                             leftMargin=0.5 * inch, rightMargin=0.5 * inch,
                             topMargin=0.5 * inch, bottomMargin=0.5 * inch)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(title, styles["Title"]))
    elements.append(Paragraph(f"Generated on {datetime.now():%Y-%m-%d %H:%M}", styles["Normal"]))
    elements.append(Spacer(1, 0.25 * inch))

    table_data = [list(df.columns)] + df.astype(str).values.tolist()
    table = Table(table_data, repeatRows=1)

    style_commands = [
        ("BACKGROUND", (0, 0), (-1, 0), HEADER_COLOR),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ALT_ROW_COLOR]),
    ]
    table.setStyle(TableStyle(style_commands))
    elements.append(table)

    doc.build(elements)

    return {"rows_written": len(df), "columns": list(df.columns)}


def main():
    parser = argparse.ArgumentParser(description="Generate a formatted PDF report from a CSV file.")
    parser.add_argument("--input", required=True, help="Path to the input CSV")
    parser.add_argument("--output", required=True, help="Path for the output PDF")
    parser.add_argument("--title", default="Report", help="Title shown at the top of the PDF")
    args = parser.parse_args()

    try:
        summary = generate_pdf(Path(args.input), Path(args.output), args.title)
        log.info("Rows written: %d", summary["rows_written"])
        log.info("Columns: %s", ", ".join(summary["columns"]))
        log.info("\nSaved to %s", args.output)
    except (FileNotFoundError, ValueError) as e:
        log.error("Error: %s", e)
    except Exception as e:
        log.error("Unexpected error: %s", e)


if __name__ == "__main__":
    main()
