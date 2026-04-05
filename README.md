# Localisation Workbench

A Python-based toolkit for transforming and validating localisation files across CSV, JSON, and Excel formats.

## Overview

Localisation teams often work across multiple file types and manually convert data between formats for translators, developers, and operations workflows.

Localisation Workbench is a lightweight product demo that simplifies those workflows by providing:

- reusable Python conversion modules
- a command-line interface
- a Streamlit demo UI
- comparison reporting for JSON files

## Features

- Convert CSV to JSON
- Convert Excel to JSON
- Convert folder-based JSON files to Excel
- Compare two JSON files and generate a text report
- Preview and download converted JSON in a simple UI

## Project Structure

```text
localisation_workbench/
├── app/
│   └── streamlit_app.py
├── examples/
│   ├── compare_samples/
│   ├── json_to_excel_sample/
│   ├── output/
│   ├── main-fr.json
│   ├── sample_fr.csv
│   └── sample_translations.xlsx
├── src/
│   └── localisation_workbench/
│       ├── __init__.py
│       ├── cli.py
│       └── converters/
│           ├── __init__.py
│           ├── csv_to_json.py
│           ├── excel_to_json.py
│           ├── json_compare.py
│           └── json_to_excel.py
├── tests/
│   └── test_csv_to_json.py
├── .gitignore
├── pyproject.toml
├── README.md
└── requirements.txt
```

## Why I Built This

This project was created as a portfolio demo for technical product roles.

The goal was to show:

- Python development skills
- workflow automation thinking
- file transformation and validation logic
- packaging and CLI design
- ability to turn backend functionality into a lightweight product UI

 ## Core Capabilities

1. CSV to JSON

Converts CSV files into JSON files using:

- column 1 as the ID
- column 2 as the translated text
- the second column header as the language code

Example input:
<id,fr
1001,Bonjour
1002,Au revoir
1003,Salut>

Example output:
{
    "1001": "Bonjour",
    "1002": "Au revoir",
    "1003": "Salut"
}

2. Excel to JSON

Converts a multi-sheet Excel workbook into JSON translation files.

Expected format:

- first row contains headers
- first column contains IDs
- target languages begin from column C by default

The tool creates:

- one folder per sheet
- one main-<language>.json file per language column

3. JSON to Excel

Reads folder-based translation JSON files such as:
Greetings/
  main-en.json
  main-de.json

  and combines them into a single Excel workbook with:

- one sheet per folder
- one row per translation ID
- columns for base and target language values

4. JSON Comparison

Compares two JSON files and produces a text report showing:

- differing values
- keys missing from one file
- a summary of differences

## Installation

Create and activate a virtual environment, then install dependencies:
<pip install -r requirements.txt
python -m pip install -e .>

 ## Run the CLI

Show available commands:

python -m localisation_workbench.cli --help

 ## Run the Streamlit Demo

```bash
streamlit run app/streamlit_app.py
``` 

The Streamlit demo currently supports all four core flows:

 - CSV to JSON: upload a CSV file, preview the JSON output, and download the generated file
 - Excel to JSON: upload an Excel workbook and download the generated JSON files as a ZIP archive
 - JSON to Excel: upload translation JSON files and download a generated Excel workbook
 - JSON Comparison: upload two JSON files, preview the comparison report, and download it as a text file

 ## Testing

Run the automated test suite with:

python -m pytest

 ## Example Use Case

A localisation manager receives:

- source strings in CSV
- translation updates in Excel
- existing application resources in JSON

This toolkit helps convert between formats, compare file versions, and prepare outputs for different stakeholders with less manual effort.

 ## Technical Highlights

This project demonstrates:

- Python package structuring with src/
- modular backend design
- command-line interface development with argparse
- file handling across CSV, JSON, and Excel
- automated testing with pytest
- lightweight UI development with Streamlit
- Git and GitHub project organization

 ## Next Improvements
- add more automated tests
- support more validation checks
- add screenshots of the demo app
- improve error handling and user feedback