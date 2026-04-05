#!/usr/bin/env python3
"""
excel_to_json_per_sheet.py

- Reads an .xlsx with multiple sheets
- Columns: A = id, B = en (ignored), C.. = target languages
- For each sheet, creates a folder named exactly like the sheet (e.g., "Working at Height")
  inside the output directory, then writes: main-{<column header>}.json for every column C+
- JSON content has NO headers: { "<id>": "<target>", ... }
"""

import argparse
import json
from pathlib import Path
import pandas as pd


def slugify(s: str) -> str:
    s = (s or "").strip()
    return "".join(ch if ch.isalnum() or ch in (" ", "-", "_") else "_" for ch in s).strip() or "unknown"


def build_mapping(df: pd.DataFrame, id_idx: int, target_idx: int) -> dict:
    sub = df.iloc[:, [id_idx, target_idx]].copy()
    sub.columns = ["id", "target"]

    # Clean
    sub = sub.dropna(subset=["id", "target"])
    sub["id"] = sub["id"].astype(str).str.strip()
    sub["target"] = sub["target"].astype(str).str.strip()
    sub = sub[(sub["id"] != "") & (sub["target"] != "")]

    if sub.empty:
        return {}

    # Warn on duplicate IDs (last wins)
    dups = sub["id"][sub["id"].duplicated(keep=False)].unique().tolist()
    if dups:
        print(f"  Warning: duplicate IDs found for this column: {dups}. Last occurrence will be used.")

    return {row["id"]: row["target"] for _, row in sub.iterrows()}


def main():
    ap = argparse.ArgumentParser(description="Convert Excel (multi-sheet) to per-sheet JSON key/value files.")
    ap.add_argument("excel_path", help="Path to input .xlsx")
    ap.add_argument(
        "-o", "--outdir",
        default=str(Path.home() / "Downloads"),   # Default to Downloads
        help="Output directory (default: your Downloads folder)"
    )
    ap.add_argument("--id-col", default=0, type=int, help="Zero-based index for ID column (default: 0 for column A)")
    ap.add_argument(
        "--start-col",
        default=2,
        type=int,
        help="Zero-based index to start exporting targets from (default: 2 for column C)"
    )
    args = ap.parse_args()

    in_path = Path(args.excel_path)
    base_outdir = Path(args.outdir)
    base_outdir.mkdir(parents=True, exist_ok=True)

    xls = pd.ExcelFile(in_path, engine="openpyxl")

    for sheet_name in xls.sheet_names:
        # Read WITH headers so row 1 is treated as headers and not data.
        df = pd.read_excel(in_path, sheet_name=sheet_name, header=0, engine="openpyxl")

        # Validate column count
        if df.shape[1] <= max(args.id_col, args.start_col):
            print(f"Skipping '{sheet_name}': not enough columns.")
            continue

        # Create per-sheet folder inside the output dir, named after the sheet
        sheet_dir = base_outdir / sheet_name
        try:
            sheet_dir.mkdir(parents=True, exist_ok=True)
        except OSError:
            sheet_dir = base_outdir / slugify(sheet_name)
            sheet_dir.mkdir(parents=True, exist_ok=True)

        print(f"Processing sheet: {sheet_name}")

        wrote_any = False
        for target_idx in range(args.start_col, df.shape[1]):
            raw_header = str(df.columns[target_idx]) if target_idx < len(df.columns) else ""
            language_code = (raw_header or "").strip().lower() or f"col{target_idx+1}"

            # Build mapping for this target column
            mapping = build_mapping(df, args.id_col, target_idx)

            if not mapping:
                # Entire column empty or no usable rows — skip silently with a note
                print(f"  Skipping column {target_idx} ('{language_code}'): no usable rows (id + target).")
                continue

            out_file = sheet_dir / f"main-{slugify(language_code)}.json"
            with out_file.open("w", encoding="utf-8") as f:
                json.dump(mapping, f, ensure_ascii=False, indent=2)

            wrote_any = True
            print(f"  Wrote {out_file} (sheet='{sheet_name}', language='{language_code}')")

        if not wrote_any:
            print(f"  No outputs for sheet '{sheet_name}' (no columns from {args.start_col} had data).")


if __name__ == "__main__":
    main()
