from pathlib import Path
import json

from localisation_workbench.converters.csv_to_json import convert_csv_to_json


def test_convert_csv_to_json(tmp_path):
    csv_file = tmp_path / "sample.csv"
    csv_file.write_text(
        "id,fr\n1001,Bonjour\n1002,Au revoir\n1003,Salut\n",
        encoding="utf-8",
    )

    output_path = convert_csv_to_json(str(csv_file))

    assert output_path.name == "main-fr.json"
    assert output_path.exists()

    with output_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    assert data == {
        "1001": "Bonjour",
        "1002": "Au revoir",
        "1003": "Salut",
    }

    output_path.unlink()