from src.localisation_workbench.converters.json_to_excel import convert_json_to_excel

output_file = convert_json_to_excel(
    "examples/json_to_excel_sample",
    base_lang="en",
    target_lang="de",
    output_filename="translations.xlsx",
)

print(f"Created: {output_file}")