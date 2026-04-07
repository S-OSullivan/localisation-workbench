import os
import tempfile
from pathlib import Path
import zipfile

import streamlit as st

from localisation_workbench.converters.csv_to_json import convert_csv_to_json
from localisation_workbench.converters.excel_to_json import convert_excel_to_json
from localisation_workbench.converters.json_compare import compare_json_files
from localisation_workbench.converters.json_to_excel import convert_json_to_excel
from localisation_workbench.scoring_io import score_csv_file


st.set_page_config(page_title="Localisation Workbench", layout="wide")

left_col, right_col = st.columns([2, 1])

with left_col:
    st.title("Localisation Workbench")
    st.subheader("A lightweight toolkit for transforming localisation files")
    st.write(
        "Convert and validate localisation assets across CSV, JSON, and Excel formats."
    )

with right_col:
    st.markdown("### Supported Flows")
    st.markdown(
        """
- CSV to JSON
- Excel to JSON
- JSON to Excel
- JSON Comparison
- Translation Quality Scoring
    """
    )

tool = st.radio(
    "Choose a tool",
    [
        "CSV to JSON",
        "Excel to JSON",
        "JSON to Excel",
        "JSON Comparison",
        "Translation Quality Scoring",
    ],
    horizontal=True,
)

st.markdown("---")

if tool == "CSV to JSON":
    st.header("CSV to JSON")
    st.caption("Upload a two-column CSV file and generate a JSON translation file.")
    uploaded_csv = st.file_uploader("Upload a CSV file", type=["csv"])

    if uploaded_csv is not None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            input_path = tmp_path / uploaded_csv.name
            input_path.write_bytes(uploaded_csv.getvalue())

            current_dir = Path.cwd()
            try:
                os.chdir(tmp_path)
                output_path = convert_csv_to_json(str(input_path))
                output_text = output_path.read_text(encoding="utf-8")
            finally:
                os.chdir(current_dir)

        st.success(f"Created: {output_path.name}")
        st.markdown("### JSON preview")
        st.code(output_text, language="json")

        st.download_button(
            label="Download JSON file",
            data=output_text,
            file_name=output_path.name,
            mime="application/json",
        )

elif tool == "Excel to JSON":
    st.header("Excel to JSON")
    st.caption("Upload a multi-sheet Excel workbook and export JSON files for each language column.")
    uploaded_excel = st.file_uploader("Upload an Excel file", type=["xlsx"])

    if uploaded_excel is not None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            input_path = tmp_path / uploaded_excel.name
            output_dir = tmp_path / "excel_output"
            zip_path = tmp_path / "excel_json_output.zip"

            input_path.write_bytes(uploaded_excel.getvalue())

            written_files = convert_excel_to_json(str(input_path), str(output_dir))

            if written_files:
                with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    for file_path in written_files:
                        zip_file.write(file_path, arcname=file_path.relative_to(output_dir))

                st.success(f"Created {len(written_files)} JSON files.")
                st.markdown("### Generated files")
                for file_path in written_files:
                    st.write(str(file_path.relative_to(output_dir)))

                st.download_button(
                    label="Download ZIP of JSON files",
                    data=zip_path.read_bytes(),
                    file_name="excel_json_output.zip",
                    mime="application/zip",
                )
            else:
                st.warning("No JSON files were generated from the uploaded workbook.")

elif tool == "JSON to Excel":
    st.header("JSON to Excel")
    st.caption("Upload translation JSON files and combine them into a downloadable Excel workbook.")
    uploaded_json_files = st.file_uploader(
        "Upload one or more JSON translation files",
        type=["json"],
        accept_multiple_files=True,
    )
    base_lang = st.text_input("Base language code", value="en")
    target_lang = st.text_input("Target language code", value="de")

    if uploaded_json_files:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            root_dir = tmp_path / "json_to_excel_input"
            sheet_dir = root_dir / "UploadedFiles"
            sheet_dir.mkdir(parents=True, exist_ok=True)

            for uploaded_file in uploaded_json_files:
                file_path = sheet_dir / uploaded_file.name
                file_path.write_bytes(uploaded_file.getvalue())

            output_path = convert_json_to_excel(
                str(root_dir),
                base_lang=base_lang,
                target_lang=target_lang,
                output_filename="translations.xlsx",
            )

            output_bytes = output_path.read_bytes()

        st.success("Excel workbook created.")
        st.markdown("### Generated workbook")
        st.write("translations.xlsx")

        st.download_button(
            label="Download Excel workbook",
            data=output_bytes,
            file_name="translations.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
elif tool == "Translation Quality Scoring":
    st.header("Translation Quality Scoring")
    st.caption(
        "Upload a CSV file with source and translation columns, with an optional reference column, to generate a scored QA output file."
    )

    uploaded_scoring_csv = st.file_uploader(
        "Upload a scoring CSV file",
        type=["csv"],
        key="scoring_csv",
    )
    source_column = st.text_input("Source column name", value="source")
    translation_column = st.text_input("Translation column name", value="translation")
    reference_column = st.text_input(
        "Reference column name (optional)",
        value="reference",
    )

    if uploaded_scoring_csv is not None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            input_path = tmp_path / uploaded_scoring_csv.name
            output_path = tmp_path / "scored_translations.csv"

            input_path.write_bytes(uploaded_scoring_csv.getvalue())

            output_file = score_csv_file(
                str(input_path),
                str(output_path),
                source_column=source_column,
                translation_column=translation_column,
                reference_column=reference_column or None,
            )

            output_text = Path(output_file).read_text(encoding="utf-8")
            output_lines = output_text.strip().splitlines()

            total_rows = max(len(output_lines) - 1, 0)
            passed_rows = sum(1 for line in output_lines[1:] if ",True," in line)
            failed_rows = total_rows - passed_rows

        st.success("Scored CSV created.")
        metric_col_1, metric_col_2, metric_col_3 = st.columns(3)
        metric_col_1.metric("Rows scored", total_rows)
        metric_col_2.metric("Passed", passed_rows)
        metric_col_3.metric("Failed", failed_rows)
        st.markdown("### Output preview")
        st.code(output_text, language="text")

        st.download_button(
            label="Download scored CSV",
            data=output_text,
            file_name="scored_translations.csv",
            mime="text/csv",
        )

elif tool == "JSON Comparison":
    st.header("JSON Comparison")
    st.caption("Upload two JSON files to generate a text report showing missing keys and value differences.")
    uploaded_json_1 = st.file_uploader("Upload the first JSON file", type=["json"], key="json1")
    uploaded_json_2 = st.file_uploader("Upload the second JSON file", type=["json"], key="json2")

    if uploaded_json_1 is not None and uploaded_json_2 is not None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            file1_path = tmp_path / uploaded_json_1.name
            file2_path = tmp_path / uploaded_json_2.name

            file1_path.write_bytes(uploaded_json_1.getvalue())
            file2_path.write_bytes(uploaded_json_2.getvalue())

            report_text = compare_json_files(str(file1_path), str(file2_path))

        st.success("Comparison report created.")
        st.markdown("### Report preview")
        st.code(report_text, language="text")

        st.download_button(
            label="Download comparison report",
            data=report_text,
            file_name="comparison_report.txt",
            mime="text/plain",
        )

st.markdown("---")

st.markdown("### Why this project exists")
st.write(
    """
Localisation teams often work across CSV, JSON, and Excel files.
This project turns repetitive file-conversion workflows into a reusable Python toolkit
with both a command-line interface and a simple product-style UI.
"""
)