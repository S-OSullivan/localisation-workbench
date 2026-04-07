import subprocess
import sys


def test_score_translation_cli_success():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "localisation_workbench.cli",
            "score-translation",
            "Hello {name}",
            "Bonjour {name}",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    assert "Score: 100/100" in result.stdout
    assert "Passed: True" in result.stdout
    assert "Issues: none" in result.stdout


def test_score_translation_cli_identical_text():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "localisation_workbench.cli",
            "score-translation",
            "Start course",
            "Start course",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    assert "Score: 75/100" in result.stdout
    assert "Passed: True" in result.stdout
    assert "- Translation is identical to source text." in result.stdout