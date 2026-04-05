import csv
import json
from pathlib import Path


def convert_csv_to_json(input_csv: str) -> Path:
    input_path = Path(input_csv)

    if not input_path.exists():
        raise FileNotFoundError(f"File does not exist: {input_csv}")

    with input_path.open(mode="r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        fieldnames = reader.fieldnames

        if not fieldnames or len(fieldnames) < 2:
            raise ValueError(
                f"{input_csv} must have at least two columns (ID and language)."
            )

        id_col = fieldnames[0]
        lang_col = fieldnames[1]
        language_code = lang_col.strip()

        data = {}
        for row in reader:
            text_value = row[lang_col].strip().strip('"').strip("'")
            data[row[id_col]] = text_value

    output_file = Path(f"main-{language_code}.json")

    with output_file.open("w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

    return output_file