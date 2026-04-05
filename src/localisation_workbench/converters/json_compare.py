import json
import os
import re
from bisect import bisect_right
from pathlib import Path
from typing import Any, Optional


KEY_PATTERN = re.compile(r'"(?P<id>\d+)"\s*:')


def load_json_dict(path: str) -> dict[str, Any]:
    file_path = Path(path)
    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise RuntimeError(
            f"Expected top-level JSON object (dict) in {path}, got {type(data).__name__}"
        )

    return {str(k): v for k, v in data.items()}


def build_key_positions(path: str) -> dict[str, tuple[int, int]]:
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError:
        return {}

    newline_idxs = [-1]
    newline_idxs.extend(i for i, ch in enumerate(text) if ch == "\n")

    positions: dict[str, tuple[int, int]] = {}
    for match in KEY_PATTERN.finditer(text):
        id_str = match.group("id")
        if id_str in positions:
            continue

        pos = match.start()
        line = bisect_right(newline_idxs, pos)
        line_start_idx = newline_idxs[line - 1]
        col = pos - line_start_idx
        positions[id_str] = (line, col)

    return positions


def safe_preview(value: Any, max_len: int = 200) -> str:
    if value is None:
        text = "null"
    elif isinstance(value, str):
        text = value
    else:
        text = repr(value)

    return (text[: max_len - 3] + "...") if len(text) > max_len else text


def sort_key(id_str: str):
    try:
        return (0, int(id_str))
    except ValueError:
        return (1, id_str)


def compare_dicts(
    first: dict[str, Any],
    second: dict[str, Any],
) -> tuple[dict[str, tuple[Optional[Any], Optional[Any], str]], int, int, int]:
    keys_first = set(first.keys())
    keys_second = set(second.keys())
    union_keys = keys_first | keys_second

    diffs: dict[str, tuple[Optional[Any], Optional[Any], str]] = {}
    missing_in_second = 0
    missing_in_first = 0

    for key in union_keys:
        in_first = key in first
        in_second = key in second

        if in_first and in_second:
            if first[key] != second[key]:
                diffs[key] = (first[key], second[key], "DIFFERENT")
        elif in_first and not in_second:
            missing_in_second += 1
            diffs[key] = (first[key], None, "MISSING_IN_FILE2")
        elif in_second and not in_first:
            missing_in_first += 1
            diffs[key] = (None, second[key], "MISSING_IN_FILE1")

    return diffs, len(union_keys), missing_in_second, missing_in_first


def append_report_section(
    lines: list[str],
    file1: str,
    file2: str,
    total_union: int,
    diffs: dict[str, tuple[Optional[Any], Optional[Any], str]],
    missing_in_file2: int,
    missing_in_file1: int,
    pos1: dict[str, tuple[int, int]],
    pos2: dict[str, tuple[int, int]],
) -> None:
    name1 = os.path.basename(file1)
    name2 = os.path.basename(file2)

    different_count = sum(1 for _, _, status in diffs.values() if status == "DIFFERENT")
    diff_total = len(diffs)
    percent = (diff_total / total_union * 100.0) if total_union else 0.0

    lines.append("")
    lines.append("=" * 100)
    lines.append(f"Comparison: {name1}  <->  {name2}")
    lines.append(f"Paths:      {os.path.abspath(file1)}  <->  {os.path.abspath(file2)}")
    lines.append("=" * 100)
    lines.append(f"Total IDs (union): {total_union}")
    lines.append(f"Total differing IDs: {diff_total}")
    lines.append(f"  - Value mismatches: {different_count}")
    lines.append(f"  - Missing in {name2}: {missing_in_file2}")
    lines.append(f"  - Missing in {name1}: {missing_in_file1}")
    lines.append(f"Percentage difference: {percent:.2f}%")
    lines.append("-" * 80)

    if not diffs:
        lines.append("No differences found.")
        return

    for key in sorted(diffs.keys(), key=sort_key):
        value1, value2, status = diffs[key]
        p1 = pos1.get(key)
        p2 = pos2.get(key)
        p1s = f"{p1[0]}:{p1[1]}" if p1 else "N/A"
        p2s = f"{p2[0]}:{p2[1]}" if p2 else "N/A"

        if status == "MISSING_IN_FILE2":
            status_pretty = f"MISSING_IN_{name2}"
        elif status == "MISSING_IN_FILE1":
            status_pretty = f"MISSING_IN_{name1}"
        else:
            status_pretty = status

        lines.append(f"ID: {key}  |  Status: {status_pretty}")
        lines.append(f"  {name1} @ {p1s}: {safe_preview(value1)}")
        lines.append(f"  {name2} @ {p2s}: {safe_preview(value2)}")
        lines.append("")


def compare_json_files(file1: str, file2: str) -> str:
    first = load_json_dict(file1)
    second = load_json_dict(file2)

    diffs, total_union, missing_in_second, missing_in_first = compare_dicts(first, second)
    pos1 = build_key_positions(file1)
    pos2 = build_key_positions(file2)

    lines: list[str] = ["JSON Comparison Report"]
    append_report_section(
        lines,
        file1,
        file2,
        total_union,
        diffs,
        missing_in_second,
        missing_in_first,
        pos1,
        pos2,
    )

    return "\n".join(lines).rstrip() + "\n"