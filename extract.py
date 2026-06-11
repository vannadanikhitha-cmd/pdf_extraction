"""
Borderless PDF Table Extractor
--------------------------------
Extracts table data from PDFs (including borderless/invisible-border tables)
and outputs JSON with headers as keys and empty string for missing values.

Usage:
    python extract_table.py input.pdf
    python extract_table.py input.pdf --output result.json
    python extract_table.py input.pdf --page 1          # specific page (1-based)

Install dependencies:
    pip install pdfplumber pandas
"""

import json
import argparse
import sys
import pdfplumber
import pandas as pd


# ── Tuning knobs ────────────────────────────────────────────────────────────
# These settings help pdfplumber detect borderless / implicit tables.
# Adjust snap_tolerance / join_tolerance if rows/columns are mis-aligned.
BORDERLESS_TABLE_SETTINGS = {
    "vertical_strategy":   "text",   # infer columns from text alignment
    "horizontal_strategy": "text",   # infer rows   from text alignment
    "snap_tolerance":      5,        # pixels – merge nearby text into one column
    "join_tolerance":      3,        # pixels – join close text fragments
    "edge_min_length":     10,
    "min_words_vertical":  1,
    "min_words_horizontal": 1,
    "intersection_tolerance": 5,
}


def clean_cell(value) -> str:
    """Return a stripped string; None / blank → empty string."""
    if value is None:
        return ""
    cleaned = str(value).strip()
    return cleaned


def extract_tables_from_page(page) -> list[list[list[str]]]:
    """
    Try two strategies in order:
      1. Default (works if borders exist)
      2. Text-alignment strategy (for borderless tables)
    Returns a list of raw tables (each table = list of rows = list of cells).
    """
    tables = page.extract_tables()          # strategy 1
    if not tables:
        tables = page.extract_tables(BORDERLESS_TABLE_SETTINGS)   # strategy 2
    return tables or []


def table_to_records(raw_table: list[list]) -> list[dict]:
    """
    Convert a raw pdfplumber table (list of rows) into a list of dicts.
    - First non-empty row is treated as the header.
    - Missing / None cells become "".
    - Duplicate header names get a numeric suffix (_2, _3 …).
    """
    if not raw_table:
        return []

    # Find the header row (first row that has at least one non-empty cell)
    header_row_idx = 0
    for i, row in enumerate(raw_table):
        if any(cell for cell in row if cell):
            header_row_idx = i
            break

    raw_headers = [clean_cell(h) for h in raw_table[header_row_idx]]

    # De-duplicate blank / repeated headers
    seen: dict[str, int] = {}
    headers: list[str] = []
    for h in raw_headers:
        if h == "":
            h = "column"
        if h in seen:
            seen[h] += 1
            headers.append(f"{h}_{seen[h]}")
        else:
            seen[h] = 1
            headers.append(h)

    records: list[dict] = []
    for row in raw_table[header_row_idx + 1:]:
        # Skip completely empty rows
        if not any(cell for cell in row if cell):
            continue

        record: dict = {}
        for col_idx, header in enumerate(headers):
            value = clean_cell(row[col_idx]) if col_idx < len(row) else ""
            record[header] = value
        records.append(record)

    return records


def extract(pdf_path: r"C:\Users\Hello\Downloads\06450200001031 Jan'26 - Feb'26.pdf", target_page: int | None = None) -> list[dict]:
    """
    Open *pdf_path* and extract every table found.
    Returns a flat list of row-records (dicts).
    *target_page* is 1-based; pass None to scan all pages.
    """
    all_records: list[dict] = []

    with pdfplumber.open(pdf_path) as pdf:
        pages = pdf.pages if target_page is None else [pdf.pages[target_page - 1]]

        for page_num, page in enumerate(pages, start=1 if target_page is None else target_page):
            raw_tables = extract_tables_from_page(page)

            if not raw_tables:
                print(f"  [page {page_num}] No tables detected – trying crop heuristic …", file=sys.stderr)
                # Last-resort: treat the whole page text as a single table
                words = page.extract_words()
                if words:
                    raw_tables = page.extract_tables(BORDERLESS_TABLE_SETTINGS)

            for tbl_idx, raw_table in enumerate(raw_tables, start=1):
                records = table_to_records(raw_table)
                if records:
                    print(f"  [page {page_num}] Table {tbl_idx}: {len(records)} rows extracted.", file=sys.stderr)
                    all_records.extend(records)
                else:
                    print(f"  [page {page_num}] Table {tbl_idx}: empty after parsing, skipped.", file=sys.stderr)

    return all_records


def main():
    parser = argparse.ArgumentParser(description="Extract borderless table data from a PDF to JSON.")
    parser.add_argument("pdf", help="Path to the input PDF file")
    parser.add_argument("--output", "-o", default=None,
                        help="Output JSON file path (default: <pdf_name>_tables.json)")
    parser.add_argument("--page", "-p", type=int, default=None,
                        help="Extract from a specific page only (1-based index)")
    parser.add_argument("--indent", type=int, default=2,
                        help="JSON indentation spaces (default: 2)")
    args = parser.parse_args()

    print(f"Processing: {args.pdf}", file=sys.stderr)
    records = extract(args.pdf, target_page=args.page)

    if not records:
        print("⚠  No table data found. Check the PDF or adjust BORDERLESS_TABLE_SETTINGS.", file=sys.stderr)
        sys.exit(1)

    output_path = args.output or args.pdf.rsplit(".", 1)[0] + "_tables.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=args.indent, ensure_ascii=False)

    print(f"\n✅  {len(records)} rows written to: {output_path}", file=sys.stderr)
    # Also print JSON to stdout so the script is pipeable
    print(json.dumps(records, indent=args.indent, ensure_ascii=False))


if __name__ == "__main__":
    main()