#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from bisect import bisect_right
from datetime import datetime
from typing import Any, Dict, Tuple, Optional, List

KEY_PATTERN = re.compile(r'"(?P<id>\d+)"\s*:')


def load_json_dict(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise RuntimeError(f"Expected top-level JSON object (dict) in {path}, got {type(data).__name__}")
    return {str(k): v for k, v in data.items()}


def build_key_positions(path: str) -> Dict[str, Tuple[int, int]]:
    """
    Best-effort map of id -> (line, col) by scanning the raw file text for '"<digits>":'
    Line and col are 1-based.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return {}

    newline_idxs = [-1]
    newline_idxs.extend(i for i, ch in enumerate(text) if ch == "\n")

    positions: Dict[str, Tuple[int, int]] = {}
    for m in KEY_PATTERN.finditer(text):
        id_str = m.group("id")
        if id_str in positions:
            continue
        pos = m.start()
        line = bisect_right(newline_idxs, pos)  # 1-based due to sentinel -1
        line_start_idx = newline_idxs[line - 1]
        col = (pos - line_start_idx)  # 1-based because line_start_idx is index of '\n' (or -1)
        positions[id_str] = (line, col)
    return positions


def safe_preview(value: Any, max_len: int = 200) -> str:
    if value is None:
        s = "null"
    elif isinstance(value, str):
        s = value
    else:
        s = repr(value)
    return (s[: max_len - 3] + "...") if len(s) > max_len else s


def sort_key(id_str: str):
    try:
        return (0, int(id_str))
    except ValueError:
        return (1, id_str)


def compare_dicts(
    a: Dict[str, Any],
    b: Dict[str, Any],
) -> Tuple[Dict[str, Tuple[Optional[Any], Optional[Any], str]], int, int, int]:
    """
    Returns:
      diffs: id -> (a_value, b_value, status)
      total_union: number of unique ids across both
      missing_in_b: count
      missing_in_a: count
    """
    keys_a = set(a.keys())
    keys_b = set(b.keys())
    union_keys = keys_a | keys_b

    diffs: Dict[str, Tuple[Optional[Any], Optional[Any], str]] = {}
    missing_in_b = 0
    missing_in_a = 0

    for k in union_keys:
        in_a = k in a
        in_b = k in b
        if in_a and in_b:
            if a[k] != b[k]:
                diffs[k] = (a[k], b[k], "DIFFERENT")
        elif in_a and not in_b:
            missing_in_b += 1
            diffs[k] = (a[k], None, "MISSING_IN_FILE2")
        elif in_b and not in_a:
            missing_in_a += 1
            diffs[k] = (None, b[k], "MISSING_IN_FILE1")

    return diffs, len(union_keys), missing_in_b, missing_in_a


def append_report_section(
    lines: List[str],
    file1: str,
    file2: str,
    total_union: int,
    diffs: Dict[str, Tuple[Optional[Any], Optional[Any], str]],
    missing_in_b: int,
    missing_in_a: int,
    pos1: Dict[str, Tuple[int, int]],
    pos2: Dict[str, Tuple[int, int]],
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
    lines.append(f"  - Missing in {name2}: {missing_in_b}")
    lines.append(f"  - Missing in {name1}: {missing_in_a}")
    lines.append(f"Percentage difference: {percent:.2f}%")
    lines.append("-" * 80)

    if not diffs:
        lines.append("No differences found.")
        return

    for k in sorted(diffs.keys(), key=sort_key):
        v1, v2, status = diffs[k]
        p1 = pos1.get(k)
        p2 = pos2.get(k)
        p1s = f"{p1[0]}:{p1[1]}" if p1 else "N/A"
        p2s = f"{p2[0]}:{p2[1]}" if p2 else "N/A"

        # Make status read nicely with real filenames
        if status == "MISSING_IN_FILE2":
            status_pretty = f"MISSING_IN_{name2}"
        elif status == "MISSING_IN_FILE1":
            status_pretty = f"MISSING_IN_{name1}"
        else:
            status_pretty = status

        lines.append(f"ID: {k}  |  Status: {status_pretty}")
        lines.append(f"  {name1} @ {p1s}: {safe_preview(v1)}")
        lines.append(f"  {name2} @ {p2s}: {safe_preview(v2)}")
        lines.append("")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Compare id->string JSON files. Provide 2+ files; compares them pairwise in order."
    )
    ap.add_argument("files", nargs="+", help="2+ JSON file paths (compared pairwise in given order)")
    ap.add_argument("-o", "--out", default="json_diff_report.txt", help="Output report path")
    args = ap.parse_args()

    if len(args.files) < 2:
        print("Error: provide at least two JSON files.", file=sys.stderr)
        return 2

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_lines: List[str] = [
        "JSON Comparison Report (Pairwise)",
        f"Generated: {now}",
        f"Files: {', '.join(os.path.abspath(p) for p in args.files)}",
    ]

    # Compare adjacent pairs
    for i in range(len(args.files) - 1):
        f1 = args.files[i]
        f2 = args.files[i + 1]
        try:
            a = load_json_dict(f1)
            b = load_json_dict(f2)
        except Exception as e:
            report_lines.append("")
            report_lines.append("=" * 100)
            report_lines.append(f"Comparison failed: {os.path.basename(f1)} <-> {os.path.basename(f2)}")
            report_lines.append(f"Paths: {os.path.abspath(f1)} <-> {os.path.abspath(f2)}")
            report_lines.append(f"Reason: {e}")
            continue

        diffs, total_union, missing_in_b, missing_in_a = compare_dicts(a, b)
        pos1 = build_key_positions(f1)
        pos2 = build_key_positions(f2)

        append_report_section(
            report_lines, f1, f2, total_union, diffs, missing_in_b, missing_in_a, pos1, pos2
        )

    with open(args.out, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines).rstrip() + "\n")

    print(f"Wrote report to: {os.path.abspath(args.out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
