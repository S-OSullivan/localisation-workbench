import csv

from localisation_workbench.scoring_io import score_csv_file


def test_score_csv_file_writes_hybrid_scoring_output(tmp_path):
    input_csv = tmp_path / "input.csv"
    output_csv = tmp_path / "output.csv"

    input_csv.write_text(
        "\n".join(
            [
                "source,translation,reference",
                "Reset password,Réinitialiser mot de passe,Réinitialiser le mot de passe",
                "Start course,Start course,Commencer le cours",
            ]
        ),
        encoding="utf-8",
    )

    written_path = score_csv_file(
        str(input_csv),
        str(output_csv),
        source_column="source",
        translation_column="translation",
        reference_column="reference",
    )

    assert written_path == str(output_csv)
    assert output_csv.exists()

    with output_csv.open("r", encoding="utf-8", newline="") as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)

    assert len(rows) == 2

    assert rows[0]["source"] == "Reset password"
    assert rows[0]["translation"] == "Réinitialiser mot de passe"
    assert rows[0]["reference"] == "Réinitialiser le mot de passe"
    assert rows[0]["qa_score"] == ""
    assert rows[0]["reference_score"] != ""
    assert rows[0]["score"] != ""
    assert rows[0]["passed"] == "True"

    assert rows[1]["source"] == "Start course"
    assert rows[1]["translation"] == "Start course"
    assert rows[1]["reference"] == "Commencer le cours"
    assert rows[1]["qa_score"] == ""
    assert rows[1]["reference_score"] != ""
    assert rows[1]["score"] != ""
    assert rows[1]["passed"] in {"True", "False"}