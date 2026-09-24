"""
Excel Report Generator
-----------------------
Turns a plain CSV into a formatted Excel report: styled header row,
auto-sized columns, frozen header, and a Summary sheet with basic stats
for every numeric column.

Usage:
    python generate_report.py --input sales.csv --output report.xlsx
    python generate_report.py --input sales.csv --output report.xlsx --title "Q1 Sales Report"
"""

import argparse
import logging
import re
import sys
import warnings
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.chart import BarChart, LineChart, PieChart, Reference
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core.io_utils import read_csv_safe  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

HEADER_FILL = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
HEADER_FONT = Font(color="FFFFFF", bold=True)

# Dashboard-specific styling
KPI_FILLS = [
    PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid"),
    PatternFill(start_color="2E7D32", end_color="2E7D32", fill_type="solid"),
    PatternFill(start_color="B45309", end_color="B45309", fill_type="solid"),
    PatternFill(start_color="6D28D9", end_color="6D28D9", fill_type="solid"),
]
KPI_LABEL_FONT = Font(color="FFFFFF", size=10)
KPI_VALUE_FONT = Font(color="FFFFFF", size=20, bold=True)
SECTION_FONT = Font(bold=True, size=13, color="1F4E78")
NOTE_FONT = Font(italic=True, color="808080")

_MONEY_WORDS = r"(revenue|sales|amount|price|cost|profit|total|value|income|expense)"
_ID_WORDS = r"(^id$|_id$|^order|^invoice)"
_ITEM_WORDS = r"(product|item|sku|name)"
_BREAKDOWN_WORDS = r"(region|category|segment|department|country|city|state)"


def _write_data_sheet_content(ws, df: pd.DataFrame, title: str | None):
    start_row = 1
    if title:
        ws.cell(row=1, column=1, value=title).font = Font(bold=True, size=14)
        start_row = 3

    # Header row
    for col_idx, col_name in enumerate(df.columns, start=1):
        cell = ws.cell(row=start_row, column=col_idx, value=str(col_name))
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT
        cell.alignment = Alignment(horizontal="center")

    # Data rows
    for row_idx, row in enumerate(df.itertuples(index=False), start=start_row + 1):
        for col_idx, value in enumerate(row, start=1):
            ws.cell(row=row_idx, column=col_idx, value=value)

    # Auto-size columns based on content length
    for col_idx, col_name in enumerate(df.columns, start=1):
        max_len = max(
            len(str(col_name)),
            df[col_name].astype(str).map(len).max() if len(df) else 0,
        )
        ws.column_dimensions[get_column_letter(col_idx)].width = max_len + 4

    # Freeze header row so it stays visible while scrolling
    ws.freeze_panes = ws.cell(row=start_row + 1, column=1)

    return ws


def _write_data_sheet(wb: Workbook, df: pd.DataFrame, sheet_name: str, title: str | None):
    ws = wb.active
    ws.title = sheet_name
    return _write_data_sheet_content(ws, df, title)


def _write_summary_sheet(wb: Workbook, df: pd.DataFrame):
    ws = wb.create_sheet("Summary")
    numeric_cols = df.select_dtypes(include="number").columns

    headers = ["Column", "Count", "Sum", "Average", "Min", "Max"]
    for col_idx, header in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col_idx, value=header)
        cell.fill = HEADER_FILL
        cell.font = HEADER_FONT

    for row_idx, col_name in enumerate(numeric_cols, start=2):
        series = df[col_name]
        ws.cell(row=row_idx, column=1, value=str(col_name))
        ws.cell(row=row_idx, column=2, value=int(series.count()))
        ws.cell(row=row_idx, column=3, value=round(float(series.sum()), 2))
        ws.cell(row=row_idx, column=4, value=round(float(series.mean()), 2))
        ws.cell(row=row_idx, column=5, value=round(float(series.min()), 2))
        ws.cell(row=row_idx, column=6, value=round(float(series.max()), 2))

    for col_idx, header in enumerate(headers, start=1):
        ws.column_dimensions[get_column_letter(col_idx)].width = len(header) + 6

    return ws


def _detect_roles(df: pd.DataFrame) -> dict:
    """
    Guess which columns play which role, purely from column names + dtypes.
    No config from the user — used to build the auto Dashboard.
    """
    date_col = None
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            date_col = col
            break
    if date_col is None:
        candidates = []
        for col in df.columns:
            if pd.api.types.is_string_dtype(df[col]) or df[col].dtype == object:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    parsed = pd.to_datetime(df[col], errors="coerce")
                hit_rate = parsed.notna().mean() if len(df) else 0
                if hit_rate > 0.7:
                    candidates.append((col, hit_rate, "date" in str(col).lower()))
        if candidates:
            candidates.sort(key=lambda c: (c[2], c[1]), reverse=True)
            date_col = candidates[0][0]

    numeric_cols = [c for c in df.select_dtypes(include="number").columns if not re.search(_ID_WORDS, str(c), re.I)]
    primary_numeric_col = None
    if numeric_cols:
        money_like = [c for c in numeric_cols if re.search(_MONEY_WORDS, str(c), re.I)]
        if money_like:
            primary_numeric_col = money_like[0]
        else:
            primary_numeric_col = max(numeric_cols, key=lambda c: df[c].abs().sum())

    category_cols = []
    for col in df.columns:
        if col == date_col or not (pd.api.types.is_string_dtype(df[col]) or df[col].dtype == object):
            continue
        n_unique = df[col].nunique(dropna=True)
        if 2 <= n_unique <= 30 and n_unique < max(0.5 * len(df), 1):
            category_cols.append(col)

    top_items_col = None
    item_like = [c for c in category_cols if re.search(_ITEM_WORDS, str(c), re.I)]
    if item_like:
        top_items_col = item_like[0]
    elif category_cols:
        top_items_col = category_cols[0]

    breakdown_col = None
    breakdown_like = [c for c in category_cols if re.search(_BREAKDOWN_WORDS, str(c), re.I) and c != top_items_col]
    if breakdown_like:
        breakdown_col = breakdown_like[0]
    else:
        remaining = [c for c in category_cols if c != top_items_col]
        if remaining:
            breakdown_col = remaining[0]

    id_like_col = next((c for c in df.columns if re.search(_ID_WORDS, str(c), re.I)), None)
    records_label = "Total Records"
    if id_like_col:
        name = str(id_like_col).lower()
        records_label = "Total Orders" if "order" in name else "Total Invoices" if "invoice" in name else "Total Records"

    return {
        "date_col": date_col,
        "primary_numeric_col": primary_numeric_col,
        "top_items_col": top_items_col,
        "breakdown_col": breakdown_col,
        "records_label": records_label,
    }


def _build_trend_data(df: pd.DataFrame, date_col: str, value_col: str) -> pd.DataFrame:
    dates = pd.to_datetime(df[date_col], errors="coerce")
    working = pd.DataFrame({"date": dates, "value": df[value_col]}).dropna(subset=["date"])
    span_days = (working["date"].max() - working["date"].min()).days if len(working) else 0
    freq = "D" if span_days <= 62 else "W" if span_days <= 365 else "M"
    grouped = working.set_index("date")["value"].resample(freq).sum().reset_index()
    grouped["label"] = grouped["date"].dt.strftime("%Y-%m-%d")
    return grouped[["label", "value"]]


def _build_top_items_data(df: pd.DataFrame, item_col: str, value_col: str | None, top_n: int = 10) -> pd.DataFrame:
    if value_col:
        grouped = df.groupby(item_col)[value_col].sum().sort_values(ascending=False).head(top_n)
    else:
        grouped = df.groupby(item_col).size().sort_values(ascending=False).head(top_n)
    return grouped.reset_index().rename(columns={grouped.name if value_col else 0: "value", item_col: "label"})


def _build_breakdown_data(df: pd.DataFrame, category_col: str, value_col: str | None) -> pd.DataFrame:
    if value_col:
        grouped = df.groupby(category_col)[value_col].sum().sort_values(ascending=False)
    else:
        grouped = df.groupby(category_col).size().sort_values(ascending=False)
    return grouped.reset_index().rename(columns={grouped.name if value_col else 0: "value", category_col: "label"})


def _write_kpi_card(ws, row: int, col_start: int, label: str, value: str, fill: PatternFill):
    label_cell = ws.cell(row=row, column=col_start, value=label)
    value_cell = ws.cell(row=row + 1, column=col_start, value=value)
    for r in (row, row + 1):
        ws.merge_cells(start_row=r, start_column=col_start, end_row=r, end_column=col_start + 1)
    for c in range(col_start, col_start + 2):
        ws.cell(row=row, column=c).fill = fill
        ws.cell(row=row + 1, column=c).fill = fill
    label_cell.font = KPI_LABEL_FONT
    label_cell.alignment = Alignment(horizontal="center", vertical="center")
    value_cell.font = KPI_VALUE_FONT
    value_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[row].height = 18
    ws.row_dimensions[row + 1].height = 32


def _format_number(value: float) -> str:
    if abs(value) >= 1000:
        return f"{value:,.0f}"
    if float(value).is_integer():
        return f"{value:.0f}"
    return f"{value:,.2f}"

def generate_report(input_path: Path, output_path: Path, sheet_name: str = "Data", title: str = None) -> dict:
    """
    Build a formatted Excel report from a CSV file.

    Returns a summary dict: rows written, numeric columns summarized.
    """
    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {input_path}")

    df = read_csv_safe(input_path)
    if df.empty:
        raise ValueError(f"No data found in {input_path}")

    wb = Workbook()
    _write_data_sheet(wb, df, sheet_name, title)
    numeric_cols = df.select_dtypes(include="number").columns
    if len(numeric_cols) > 0:
        _write_summary_sheet(wb, df)

    wb.save(output_path)

    return {
        "rows_written": len(df),
        "columns": list(df.columns),
        "numeric_columns_summarized": list(numeric_cols),
    }


def _write_chart_data_sheet(wb: Workbook, trend_df, top_items_df, breakdown_df):
    ws = wb.create_sheet("Chart Data")
    col = 1

    if trend_df is not None and len(trend_df):
        ws.cell(row=1, column=col, value="Date").font = Font(bold=True)
        ws.cell(row=1, column=col + 1, value="Value").font = Font(bold=True)
        for i, (_, r) in enumerate(trend_df.iterrows(), start=2):
            ws.cell(row=i, column=col, value=r["label"])
            ws.cell(row=i, column=col + 1, value=round(float(r["value"]), 2))
        trend_range = {"col": col + 1, "min_row": 1, "max_row": len(trend_df) + 1, "cat_col": col}
        col += 3
    else:
        trend_range = None

    if top_items_df is not None and len(top_items_df):
        ws.cell(row=1, column=col, value="Item").font = Font(bold=True)
        ws.cell(row=1, column=col + 1, value="Value").font = Font(bold=True)
        for i, (_, r) in enumerate(top_items_df.iterrows(), start=2):
            ws.cell(row=i, column=col, value=str(r["label"]))
            ws.cell(row=i, column=col + 1, value=round(float(r["value"]), 2))
        items_range = {"col": col + 1, "min_row": 1, "max_row": len(top_items_df) + 1, "cat_col": col}
        col += 3
    else:
        items_range = None

    if breakdown_df is not None and len(breakdown_df):
        ws.cell(row=1, column=col, value="Category").font = Font(bold=True)
        ws.cell(row=1, column=col + 1, value="Value").font = Font(bold=True)
        for i, (_, r) in enumerate(breakdown_df.iterrows(), start=2):
            ws.cell(row=i, column=col, value=str(r["label"]))
            ws.cell(row=i, column=col + 1, value=round(float(r["value"]), 2))
        breakdown_range = {"col": col + 1, "min_row": 1, "max_row": len(breakdown_df) + 1, "cat_col": col}
    else:
        breakdown_range = None

    return ws, trend_range, items_range, breakdown_range


def _write_dashboard_sheet(wb: Workbook, title: str, kpis: list[tuple[str, str]], chart_ws,
                            trend_range, items_range, breakdown_range, notes: list[str]):
    ws = wb.active
    ws.title = "Dashboard"

    ws.cell(row=1, column=1, value=title).font = Font(bold=True, size=16, color="1F4E78")
    ws.cell(row=2, column=1, value="Generated by FreelanceFlow").font = NOTE_FONT

    kpi_row = 4
    col = 1
    for i, (label, value) in enumerate(kpis):
        _write_kpi_card(ws, kpi_row, col, label, value, KPI_FILLS[i % len(KPI_FILLS)])
        col += 3
    ws.row_dimensions[3].height = 6

    chart_row = kpi_row + 3
    ws.cell(row=chart_row, column=1, value="Charts").font = SECTION_FONT
    chart_row += 1

    charts_placed = 0
    if trend_range:
        chart = LineChart()
        chart.title = "Trend Over Time"
        chart.height, chart.width = 8, 16
        data = Reference(chart_ws, min_col=trend_range["col"], max_col=trend_range["col"],
                          min_row=trend_range["min_row"], max_row=trend_range["max_row"])
        cats = Reference(chart_ws, min_col=trend_range["cat_col"], max_col=trend_range["cat_col"],
                          min_row=trend_range["min_row"] + 1, max_row=trend_range["max_row"])
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)
        chart.style = 2
        ws.add_chart(chart, f"A{chart_row}")
        charts_placed += 1
    else:
        ws.cell(row=chart_row, column=1, value="Trend chart not available — no date column detected.").font = NOTE_FONT

    row_after_first = chart_row + 17

    if items_range:
        chart = BarChart()
        chart.type = "col"
        chart.title = "Top Items"
        chart.height, chart.width = 8, 16
        data = Reference(chart_ws, min_col=items_range["col"], max_col=items_range["col"],
                          min_row=items_range["min_row"], max_row=items_range["max_row"])
        cats = Reference(chart_ws, min_col=items_range["cat_col"], max_col=items_range["cat_col"],
                          min_row=items_range["min_row"] + 1, max_row=items_range["max_row"])
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)
        chart.style = 10
        ws.add_chart(chart, f"A{row_after_first}")
        charts_placed += 1
    else:
        ws.cell(row=row_after_first, column=1, value="Top items chart not available — no suitable category column detected.").font = NOTE_FONT

    if breakdown_range:
        chart = PieChart()
        chart.title = "Category / Regional Breakdown"
        chart.height, chart.width = 8, 12
        data = Reference(chart_ws, min_col=breakdown_range["col"], max_col=breakdown_range["col"],
                          min_row=breakdown_range["min_row"], max_row=breakdown_range["max_row"])
        cats = Reference(chart_ws, min_col=breakdown_range["cat_col"], max_col=breakdown_range["cat_col"],
                          min_row=breakdown_range["min_row"] + 1, max_row=breakdown_range["max_row"])
        chart.add_data(data, titles_from_data=True)
        chart.set_categories(cats)
        ws.add_chart(chart, f"J{row_after_first}")
        charts_placed += 1
    else:
        ws.cell(row=row_after_first, column=10, value="Breakdown chart not available.").font = NOTE_FONT

    if notes:
        note_row = row_after_first + 18
        for note in notes:
            ws.cell(row=note_row, column=1, value=f"Note: {note}").font = NOTE_FONT
            note_row += 1

    ws.column_dimensions["A"].width = 14
    for c in "BCDEFGHIJKL":
        ws.column_dimensions[c].width = 12

    return ws, charts_placed


def generate_dashboard_report(input_path: Path, output_path: Path, title: str = None) -> dict:
    """
    Build an auto-generated Excel dashboard from a CSV: KPI cards, a trend
    chart, a top-items chart, and a category/regional breakdown chart —
    with no manual configuration. Column roles (date/value/category) are
    guessed from column names and dtypes; any chart that isn't supported
    by the data is skipped with a note rather than faked.

    Sheets produced: Dashboard, Chart Data, Data, Summary (Summary only
    if there are numeric columns).
    """
    if not input_path.exists():
        raise FileNotFoundError(f"File not found: {input_path}")

    df = read_csv_safe(input_path)
    if df.empty:
        raise ValueError(f"No data found in {input_path}")

    roles = _detect_roles(df)
    value_col = roles["primary_numeric_col"]
    notes = []

    # KPI cards
    kpis = []
    if value_col:
        total = df[value_col].sum()
        avg = df[value_col].mean()
        kpis.append((f"Total {value_col}", _format_number(total)))
        kpis.append((f"Average {value_col}", _format_number(avg)))
    kpis.append((roles["records_label"], _format_number(len(df))))
    breakdown_kpi_col = roles["breakdown_col"] or roles["top_items_col"]
    if breakdown_kpi_col:
        kpis.append((f"Unique {breakdown_kpi_col}", _format_number(df[breakdown_kpi_col].nunique())))
    elif value_col:
        kpis.append((f"Max {value_col}", _format_number(df[value_col].max())))

    # Chart data
    trend_df = None
    if roles["date_col"] and value_col:
        trend_df = _build_trend_data(df, roles["date_col"], value_col)
    elif not roles["date_col"]:
        notes.append("No date-like column was found, so a trend chart couldn't be built.")

    top_items_df = None
    if roles["top_items_col"]:
        top_items_df = _build_top_items_data(df, roles["top_items_col"], value_col)

    breakdown_df = None
    if roles["breakdown_col"] and roles["breakdown_col"] != roles["top_items_col"]:
        breakdown_df = _build_breakdown_data(df, roles["breakdown_col"], value_col)
    elif roles["top_items_col"] and not roles["breakdown_col"]:
        # only one usable category column — reuse it for the breakdown view too
        breakdown_df = _build_breakdown_data(df, roles["top_items_col"], value_col)
    if not roles["top_items_col"] and not roles["breakdown_col"]:
        notes.append("No suitable category column was found, so item/category charts couldn't be built.")

    wb = Workbook()
    chart_ws, trend_range, items_range, breakdown_range = _write_chart_data_sheet(
        wb, trend_df, top_items_df, breakdown_df
    )
    _, charts_placed = _write_dashboard_sheet(
        wb, title or input_path.stem, kpis, chart_ws, trend_range, items_range, breakdown_range, notes
    )

    ws_data = wb.create_sheet("Data")
    _write_data_sheet_content(ws_data, df, title=None)

    numeric_cols = df.select_dtypes(include="number").columns
    if len(numeric_cols) > 0:
        _write_summary_sheet(wb, df)

    wb.save(output_path)

    return {
        "rows_written": len(df),
        "columns": list(df.columns),
        "kpis": kpis,
        "charts_placed": charts_placed,
        "notes": notes,
        "detected_roles": roles,
    }


def main():
    parser = argparse.ArgumentParser(description="Generate a formatted Excel report from a CSV file.")
    parser.add_argument("--input", required=True, help="Path to the input CSV")
    parser.add_argument("--output", required=True, help="Path for the output .xlsx file")
    parser.add_argument("--sheet-name", default="Data", help="Name for the data sheet (default: Data)")
    parser.add_argument("--title", default=None, help="Optional title shown above the table")
    parser.add_argument("--dashboard", action="store_true",
                         help="Generate the auto Dashboard (KPI cards + charts) instead of the plain report")
    args = parser.parse_args()

    try:
        if args.dashboard:
            summary = generate_dashboard_report(Path(args.input), Path(args.output), args.title)
            log.info("Rows written: %d", summary["rows_written"])
            log.info("KPIs: %s", ", ".join(f"{k}={v}" for k, v in summary["kpis"]))
            log.info("Charts placed: %d", summary["charts_placed"])
            for note in summary["notes"]:
                log.info("Note: %s", note)
        else:
            summary = generate_report(Path(args.input), Path(args.output), args.sheet_name, args.title)
            log.info("Rows written: %d", summary["rows_written"])
            log.info("Columns: %s", ", ".join(summary["columns"]))
            if summary["numeric_columns_summarized"]:
                log.info("Summary sheet added for: %s", ", ".join(summary["numeric_columns_summarized"]))
        log.info("\nSaved to %s", args.output)
    except (FileNotFoundError, ValueError) as e:
        log.error("Error: %s", e)
    except Exception as e:
        log.error("Unexpected error: %s", e)


if __name__ == "__main__":
    main()
