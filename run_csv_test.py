from src.localisation_workbench.converters.csv_to_json import convert_csv_to_json

output_file = convert_csv_to_json("examples/sample_fr.csv")
print(f"Created: {output_file}")