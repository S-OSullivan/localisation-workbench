from src.localisation_workbench.converters.json_compare import compare_json_files

report = compare_json_files(
    "examples/compare_samples/file_a.json",
    "examples/compare_samples/file_b.json",
)

output_path = "examples/compare_samples/comparison_report.txt"

with open(output_path, "w", encoding="utf-8") as file:
    file.write(report)

print(f"Created: {output_path}")