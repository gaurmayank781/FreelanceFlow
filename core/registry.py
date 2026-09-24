"""
Central list of every automation tool exposed in the V2 UI.

Everything that needs to know "what tools exist" — the Dashboard,
the Automation Center, the Favorites page — reads from here instead
of keeping its own copy, so adding a tool means editing one place.

Email Automation is intentionally NOT listed here (isolated from the
V2 nav — see email_automation/_disabled_page/).
"""
from __future__ import annotations

from typing import TypedDict


class Tool(TypedDict):
    slug: str
    icon: str
    name: str
    description: str
    category: str  # "Data" | "Files" | "Reports"
    page: str


TOOLS: list[Tool] = [
    {
        "slug": "csv_merger",
        "icon": "📊",
        "name": "CSV Merger",
        "description": "Combine several CSV files into one, even with mismatched columns.",
        "category": "Data",
        "page": "pages/04_📊_CSV_Merger.py",
    },
    {
        "slug": "data_cleaner",
        "icon": "🧹",
        "name": "Data Cleaner",
        "description": "Fix messy column names, blank rows, and duplicate rows.",
        "category": "Data",
        "page": "pages/05_🧹_Data_Cleaner.py",
    },
    {
        "slug": "csv_analyzer",
        "icon": "🔎",
        "name": "CSV Analyzer",
        "description": "Understand a dataset before you work on it — types, missing data, stats, warnings.",
        "category": "Data",
        "page": "pages/11_🔎_CSV_Analyzer.py",
    },
    {
        "slug": "csv_splitter",
        "icon": "✂️",
        "name": "CSV Splitter",
        "description": "Split one CSV into multiple files by row count or by a column's value.",
        "category": "Data",
        "page": "pages/12_✂️_CSV_Splitter.py",
    },
    {
        "slug": "duplicate_detector",
        "icon": "🧬",
        "name": "Duplicate Detector",
        "description": "Find duplicate rows — exact, by chosen columns, or a normalized near-match.",
        "category": "Data",
        "page": "pages/13_🧬_Duplicate_Detector.py",
    },
    {
        "slug": "data_quality_report",
        "icon": "🏅",
        "name": "Data Quality Report",
        "description": "A professional quality score + issues + recommendations, exportable to Excel/PDF.",
        "category": "Data",
        "page": "pages/14_🏅_Data_Quality_Report.py",
    },
    {
        "slug": "bulk_renamer",
        "icon": "📁",
        "name": "Bulk Renamer",
        "description": "Rename a batch of files with a numbered pattern.",
        "category": "Files",
        "page": "pages/02_📁_Bulk_Renamer.py",
    },
    {
        "slug": "folder_organizer",
        "icon": "🗂️",
        "name": "Folder Organizer",
        "description": "Sort a messy folder into type-based subfolders.",
        "category": "Files",
        "page": "pages/03_🗂️_Folder_Organizer.py",
    },
    {
        "slug": "excel_report",
        "icon": "📈",
        "name": "Excel Report",
        "description": "Auto-generated Excel dashboard — KPI cards, trend/top-items/breakdown charts, no setup.",
        "category": "Reports",
        "page": "pages/06_📈_Excel_Report.py",
    },
    {
        "slug": "pdf_report",
        "icon": "📄",
        "name": "PDF Report",
        "description": "Turn a CSV into a formatted, print-ready PDF table.",
        "category": "Reports",
        "page": "pages/07_📄_PDF_Report.py",
    },
]

CATEGORIES = ["Data", "Files", "Reports"]


def get_tool(slug: str) -> Tool | None:
    return next((t for t in TOOLS if t["slug"] == slug), None)


def tools_by_category(category: str) -> list[Tool]:
    return [t for t in TOOLS if t["category"] == category]
