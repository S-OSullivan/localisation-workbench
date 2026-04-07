from __future__ import annotations

import csv
from pathlib import Path

from localisation_workbench.quality_scoring import score_translation_rows


def score_csv_file(
    input_csv: str,
    output_csv: str,
    source_column: str = "source",
    translation_column: str = "translation",
    reference_column: str | None = None,
) -> str:
    """
    Read a CSV file, score each translation row, and write an enriched CSV file.
    """
    input_path = Path(input_csv)
    output_path = Path(output_csv)

    with input_path.open("r", encoding="utf-8-sig", newline="") as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)

    scored_rows = score_translation_rows(
        rows,
        source_key=source_column,
        translation_key=translation_column,
        reference_key=reference_column,
    )

    if not scored_rows:
        fieldnames = [source_column, translation_column]
        if reference_column:
            fieldnames.append(reference_column)
        fieldnames.extend(
            ["qa_score", "reference_score", "score", "max_score", "passed", "issues"]
        )
    else:
        fieldnames = list(scored_rows[0].keys())

    with output_path.open("w", encoding="utf-8", newline="") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(scored_rows)

    return str(output_path)