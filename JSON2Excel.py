#!/usr/bin/env python3
"""
Convert folder-wise JSON translations to a single Excel workbook.

Folder structure example:
root_path/
  featureA/
    main-en.json
    main-fr.json
  featureB/
    main-en.json
    main-de.json

Output:
root_path/translations.xlsx  # one sheet per folder (featureA, featureB, ...)

Usage:
  python json2excel.py /path/to/root --base en --target de --output translations.xlsx
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Any, Tuple, List

import pandas as pd


def load_json(file_path: Path) -> Dict[str, Any]:
    """Load a JSON file whose top-level is a dict of id -> content.
    Returns {} if file doesn't exist. Coerces keys to strings.
    """
    if not file_path.exists():
        return {}
    try:
        with file_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            raise ValueError(f"{file_path} must contain a top-level JSON object (dict).")
        # Coerce keys to strings to be consistent in Excel
        return {str(k): v if v is not None else "" for k, v in data.items()}
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON: {file_path}\n{e}") from e


def make_sheet_dataframe(
    folder_path: Path, base_lang: str, target_lang: str
) -> Tuple[str, pd.DataFrame]:
    """
    Build a DataFrame for a single folder.
    Columns: id, main-<base>, main-<target>
    Sheet name is the folder name (sanitized to Excel's 31-char limit).
    """
    base_file = folder_path / f"main-{base_lang}.json"
    target_file = folder_path / f"main-{target_lang}.json"

    base_map = load_json(base_file)
    target_map = load_json(target_file)

    # union of ids present in either map
    ids = sorted(set(base_map.keys()).union(target_map.keys()), key=lambda x: (len(x), x))

    rows: List[Dict[str, Any]] = []
    for _id in ids:
        rows.append(
            {
                "id": _id,
                f"main-{base_lang}": base_map.get(_id, ""),
                f"main-{target_lang}": target_map.get(_id, ""),
            }
        )

    df = pd.DataFrame(rows, columns=["id", f"main-{base_lang}", f"main-{target_lang}"])

    # Clean sheet name (Excel limit 31 chars; no []:*?/\\)
    sheet_name = folder_path.name
    for bad in r'[]:*?/\\':
        sheet_name = sheet_name.replace(bad, "-")
    sheet_name = sheet_name[:31] if len(sheet_name) > 31 else sheet_name
    if not sheet_name:
        sheet_name = "Sheet"

    return sheet_name, df


def find_child_folders(root: Path) -> List[Path]:
    """Return immediate child directories of root that contain any main-*.json file."""
    if not root.exists() or not root.is_dir():
        raise ValueError(f"Root path is not a directory: {root}")
    folders = []
    for p in sorted([d for d in root.iterdir() if d.is_dir()]):
        has_any = any((p / f).exists() for f in [*map(lambda s: f"main-{s}", ["en", "de", "fr", "es", "it", "pt", "nl", "sv", "no", "da", "fi", "pl", "cs", "tr", "ru", "ja", "ko", "zh"])]
                      ) or any(fp.name.startswith("main-") and fp.suffix == ".json" for fp in p.glob("main-*.json"))
        if has_any:
            folders.append(p)
    return folders


def main():
    parser = argparse.ArgumentParser(description="Convert JSON translations to Excel.")
    parser.add_argument("root", type=Path, help="Root directory containing subfolders.")
    parser.add_argument("--base", default="en", help="Base language code (default: en).")
    parser.add_argument("--target", default="de", help="Target language code (default: de).")
    parser.add_argument(
        "--output",
        default="translations.xlsx",
        help="Output Excel filename (saved inside the root directory).",
    )
    parser.add_argument(
        "--include-root",
        action="store_true",
        help="Also scan the root folder itself for main-*.json (not only its subfolders).",
    )

    args = parser.parse_args()
    root: Path = args.root.resolve()
    base_lang: str = args.base
    target_lang: str = args.target
    output_path: Path = root / args.output

    try:
        sheets: List[Tuple[str, pd.DataFrame]] = []

        # Optionally include the root itself as a sheet if it has JSONs
        if args.include_root:
            if any(root.glob("main-*.json")):
                sheets.append(make_sheet_dataframe(root, base_lang, target_lang))

        # Process each child folder
        for folder in find_child_folders(root):
            try:
                sheet_name, df = make_sheet_dataframe(folder, base_lang, target_lang)
                if not df.empty:
                    sheets.append((sheet_name, df))
            except Exception as e:
                print(f"[WARN] Skipping folder '{folder.name}': {e}", file=sys.stderr)

        if not sheets:
            raise SystemExit("No matching folders or JSON files found.")

        # Write all sheets into a single workbook
        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            for sheet_name, df in sheets:
                df.to_excel(writer, sheet_name=sheet_name, index=False)

        print(f"✅ Wrote {len(sheets)} sheet(s) to: {output_path}")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
