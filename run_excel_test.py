from src.localisation_workbench.converters.excel_to_json import convert_excel_to_json

written_files = convert_excel_to_json(
    "examples/sample_translations.xlsx",
    "examples/output"
)

for file_path in written_files:
    print(f"Created: {file_path}")