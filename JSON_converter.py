import csv
import json
import sys
import os

if len(sys.argv) < 2:
    print("Usage: python3 script.py <file1.csv> <file2.csv> ...")
    sys.exit(1)

for input_csv in sys.argv[1:]:
    if not os.path.exists(input_csv):
        print(f"Error: File '{input_csv}' does not exist. Skipping...")
        continue

    with open(input_csv, mode="r", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        fieldnames = reader.fieldnames

        if not fieldnames or len(fieldnames) < 2:
            print(f"Error: {input_csv} must have at least two columns (ID and language). Skipping...")
            continue

        id_col = fieldnames[0]          # First column is ID
        lang_col = fieldnames[1]        # Second column is language code
        language_code = lang_col.strip()

        data = {}
        for row in reader:
            text_value = row[lang_col].strip().strip('"').strip("'")  # Remove leading/trailing quotes
            data[row[id_col]] = text_value

    output_file = f"main-{language_code}.json"
    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

    print(f"{input_csv} â†’ {output_file} created successfully!")