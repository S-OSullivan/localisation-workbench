import argparse

from localisation_workbench.converters.csv_to_json import convert_csv_to_json
from localisation_workbench.converters.excel_to_json import convert_excel_to_json
from localisation_workbench.converters.json_compare import compare_json_files
from localisation_workbench.converters.json_to_excel import convert_json_to_excel
from localisation_workbench.quality_scoring import score_translation_pair
from localisation_workbench.scoring_io import score_csv_file


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Localisation Workbench command-line tools"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    csv_parser = subparsers.add_parser("csv-to-json", help="Convert CSV to JSON")
    csv_parser.add_argument("input_csv", help="Path to the input CSV file")

    excel_parser = subparsers.add_parser("excel-to-json", help="Convert Excel to JSON")
    excel_parser.add_argument("input_excel", help="Path to the input Excel file")
    excel_parser.add_argument("output_dir", help="Directory where JSON files will be written")

    compare_parser = subparsers.add_parser("compare-json", help="Compare two JSON files")
    compare_parser.add_argument("file1", help="First JSON file")
    compare_parser.add_argument("file2", help="Second JSON file")
    compare_parser.add_argument(
        "--output",
        default="comparison_report.txt",
        help="Path to the output report file",
    )

    json_excel_parser = subparsers.add_parser(
        "json-to-excel", help="Convert folder-based JSON files to Excel"
    )
    json_excel_parser.add_argument("root_dir", help="Root directory containing JSON folders")
    json_excel_parser.add_argument("--base-lang", default="en", help="Base language code")
    json_excel_parser.add_argument("--target-lang", default="de", help="Target language code")
    json_excel_parser.add_argument(
        "--output-filename",
        default="translations.xlsx",
        help="Output Excel filename",
    )

    score_parser = subparsers.add_parser(
        "score-translation",
        help="Score a single source and translation pair",
    )
    score_parser.add_argument("source_text", help="Source text")
    score_parser.add_argument("translation_text", help="Translation text")

    score_csv_parser = subparsers.add_parser(
        "score-csv",
        help="Score translation rows from a CSV file",
    )
    score_csv_parser.add_argument("input_csv", help="Path to the input CSV file")
    score_csv_parser.add_argument("output_csv", help="Path to the output CSV file")
    score_csv_parser.add_argument(
        "--source-column",
        default="source",
        help="Source text column name",
    )
    score_csv_parser.add_argument(
        "--translation-column",
        default="translation",
        help="Translation text column name",
    )
    score_csv_parser.add_argument(
        "--reference-column",
        default=None,
        help="Optional reference text column name",
    )

    args = parser.parse_args()

    if args.command == "csv-to-json":
        output_file = convert_csv_to_json(args.input_csv)
        print(f"Created: {output_file}")

    elif args.command == "excel-to-json":
        written_files = convert_excel_to_json(args.input_excel, args.output_dir)
        for file_path in written_files:
            print(f"Created: {file_path}")

    elif args.command == "compare-json":
        report = compare_json_files(args.file1, args.file2)
        with open(args.output, "w", encoding="utf-8") as file:
            file.write(report)
        print(f"Created: {args.output}")

    elif args.command == "json-to-excel":
        output_file = convert_json_to_excel(
            args.root_dir,
            base_lang=args.base_lang,
            target_lang=args.target_lang,
            output_filename=args.output_filename,
        )
        print(f"Created: {output_file}")

    elif args.command == "score-translation":
        result = score_translation_pair(args.source_text, args.translation_text)
        print(f"Score: {result.score}/{result.max_score}")
        print(f"Passed: {result.passed}")
        if result.issues:
            print("Issues:")
            for issue in result.issues:
                print(f"- {issue}")
        else:
            print("Issues: none")

    elif args.command == "score-csv":
        output_file = score_csv_file(
            args.input_csv,
            args.output_csv,
            source_column=args.source_column,
            translation_column=args.translation_column,
            reference_column=args.reference_column,
        )
        print(f"Created: {output_file}")


if __name__ == "__main__":
    main()