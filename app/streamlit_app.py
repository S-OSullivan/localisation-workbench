import json
import tempfile
from pathlib import Path

import streamlit as st

from localisation_workbench.converters.csv_to_json import convert_csv_to_json


st.set_page_config(page_title="Localisation Workbench", layout="wide")

st.title("Localisation Workbench")
st.subheader("A lightweight toolkit for transforming localisation files")

st.markdown(
    """
This demo project supports:

- CSV to JSON
- Excel to JSON
- JSON to Excel
- JSON comparison reports
"""
)

st.markdown("### CSV to JSON demo")

uploaded_csv = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_csv is not None:
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        input_path = tmp_path / uploaded_csv.name

        input_path.write_bytes(uploaded_csv.getvalue())

        current_dir = Path.cwd()
        try:
            import os

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

st.markdown("### Why this project exists")
st.write(
    """
Localisation teams often work across CSV, JSON, and Excel files.
This project turns repetitive file-conversion workflows into a reusable Python toolkit
with both a command-line interface and a simple product-style UI.
"""
)