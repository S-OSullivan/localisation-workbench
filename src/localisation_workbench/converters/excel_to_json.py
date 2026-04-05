import json
from pathlib import Path

import pandas as pd


def slugify(value: str) -> str:
    value = (value or "").strip()
    cleaned = "".join(
        ch if ch.isalnum() or ch in (" ", "-", "_") else "_" for ch in value
    ).strip()
    return cleaned or "unknown"


def build_mapping(df: pd.DataFrame, id_idx: int, target_idx: int) -> dict:
    sub = df.iloc[:, [id_idx, target_idx]].copy()
    sub.columns = ["id", "target"]

    sub = sub.dropna(subset=["id", "target"])
    sub["id"] = sub["id"].astype(str).str.strip()
    sub["target"] = sub["target"].astype(str).str.strip()
    sub = sub[(sub["id"] != "") & (sub["target"] != "")]

    if sub.empty:
        return {}

    return {row["id"]: row["target"] for _, row in sub.iterrows()}


def convert_excel_to_json(
    excel_path: str,
    output_dir: str,
    id_col: int = 0,
    start_col: int = 2,
) -> list[Path]:
    input_path = Path(excel_path)
    base_output_dir = Path(output_dir)

    if not input_path.exists():
        raise FileNotFoundError(f"Excel file does not exist: {excel_path}")

    base_output_dir.mkdir(parents=True, exist_ok=True)
    written_files = []

    xls = pd.ExcelFile(input_path, engine="openpyxl")

    for sheet_name in xls.sheet_names:
        df = pd.read_excel(input_path, sheet_name=sheet_name, header=0, engine="openpyxl")

        if df.shape[1] <= max(id_col, start_col):
            continue

        sheet_dir = base_output_dir / sheet_name
        try:
            sheet_dir.mkdir(parents=True, exist_ok=True)
        except OSError:
            sheet_dir = base_output_dir / slugify(sheet_name)
            sheet_dir.mkdir(parents=True, exist_ok=True)

        for target_idx in range(start_col, df.shape[1]):
            raw_header = str(df.columns[target_idx]) if target_idx < len(df.columns) else ""
            language_code = (raw_header or "").strip().lower() or f"col{target_idx + 1}"

            mapping = build_mapping(df, id_col, target_idx)
            if not mapping:
                continue

            output_file = sheet_dir / f"main-{slugify(language_code)}.json"
            with output_file.open("w", encoding="utf-8") as json_file:
                json.dump(mapping, json_file, ensure_ascii=False, indent=2)

            written_files.append(output_file)

    return written_files