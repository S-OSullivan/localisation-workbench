import json
from pathlib import Path
from typing import Any

import pandas as pd


def load_json(file_path: Path) -> dict[str, Any]:
    if not file_path.exists():
        return {}

    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(f"{file_path} must contain a top-level JSON object (dict).")

    return {str(k): v if v is not None else "" for k, v in data.items()}


def clean_sheet_name(name: str) -> str:
    sheet_name = name
    for bad in r'[]:*?/\\':
        sheet_name = sheet_name.replace(bad, "-")
    sheet_name = sheet_name[:31] if len(sheet_name) > 31 else sheet_name
    return sheet_name or "Sheet"


def make_sheet_dataframe(
    folder_path: Path, base_lang: str, target_lang: str
) -> tuple[str, pd.DataFrame]:
    base_file = folder_path / f"main-{base_lang}.json"
    target_file = folder_path / f"main-{target_lang}.json"

    base_map = load_json(base_file)
    target_map = load_json(target_file)

    ids = sorted(set(base_map.keys()).union(target_map.keys()), key=lambda x: (len(x), x))

    rows = []
    for item_id in ids:
        rows.append(
            {
                "id": item_id,
                f"main-{base_lang}": base_map.get(item_id, ""),
                f"main-{target_lang}": target_map.get(item_id, ""),
            }
        )

    df = pd.DataFrame(rows, columns=["id", f"main-{base_lang}", f"main-{target_lang}"])
    sheet_name = clean_sheet_name(folder_path.name)

    return sheet_name, df


def find_child_folders(root: Path) -> list[Path]:
    if not root.exists() or not root.is_dir():
        raise ValueError(f"Root path is not a directory: {root}")

    folders = []
    for folder in sorted([d for d in root.iterdir() if d.is_dir()]):
        has_json = any(file.name.startswith("main-") and file.suffix == ".json" for file in folder.glob("main-*.json"))
        if has_json:
            folders.append(folder)

    return folders


def convert_json_to_excel(
    root_dir: str,
    base_lang: str = "en",
    target_lang: str = "de",
    output_filename: str = "translations.xlsx",
    include_root: bool = False,
) -> Path:
    root = Path(root_dir).resolve()
    output_path = root / output_filename
    sheets: list[tuple[str, pd.DataFrame]] = []

    if include_root and any(root.glob("main-*.json")):
        sheet_name, df = make_sheet_dataframe(root, base_lang, target_lang)
        if not df.empty:
            sheets.append((sheet_name, df))

    for folder in find_child_folders(root):
        sheet_name, df = make_sheet_dataframe(folder, base_lang, target_lang)
        if not df.empty:
            sheets.append((sheet_name, df))

    if not sheets:
        raise ValueError("No matching folders or JSON files found.")

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        for sheet_name, df in sheets:
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    return output_path