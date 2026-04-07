from localisation_workbench.quality_scoring import score_translation_pair


def test_score_translation_pair_passes_for_valid_translation():
    result = score_translation_pair("Hello {name}", "Bonjour {name}")

    assert result.score == 100
    assert result.max_score == 100
    assert result.passed is True
    assert result.issues == []


def test_score_translation_pair_flags_identical_text():
    result = score_translation_pair("Start course", "Start course")

    assert result.score == 75
    assert result.passed is True
    assert "Translation is identical to source text." in result.issues


def test_score_translation_pair_flags_empty_translation():
    result = score_translation_pair("Start course", "")

    assert result.score == 50
    assert result.passed is False
    assert "Translation text is empty." in result.issues


def test_score_translation_pair_flags_placeholder_mismatch():
    result = score_translation_pair("Hello {name}", "Bonjour")

    assert result.score == 85
    assert result.passed is True
    assert "Placeholder count does not match source text." in result.issues

def test_score_translation_rows_returns_enriched_rows():
    from localisation_workbench.quality_scoring import score_translation_rows

    rows = [
        {"source": "Hello {name}", "translation": "Bonjour {name}"},
        {"source": "Start course", "translation": "Start course"},
    ]

    results = score_translation_rows(rows)

    assert len(results) == 2

    assert results[0]["source"] == "Hello {name}"
    assert results[0]["translation"] == "Bonjour {name}"
    assert results[0]["score"] == 100
    assert results[0]["max_score"] == 100
    assert results[0]["passed"] is True
    assert results[0]["issues"] == ""

    assert results[1]["source"] == "Start course"
    assert results[1]["translation"] == "Start course"
    assert results[1]["score"] == 75
    assert results[1]["max_score"] == 100
    assert results[1]["passed"] is True
    assert results[1]["issues"] == "Translation is identical to source text."


def test_score_translation_rows_handles_missing_values():
    from localisation_workbench.quality_scoring import score_translation_rows

    rows = [
        {"source": "Welcome", "translation": ""},
        {"source": "", "translation": "Bonjour"},
    ]

    results = score_translation_rows(rows)

    assert results[0]["score"] == 50
    assert results[0]["passed"] is False
    assert results[0]["issues"] == "Translation text is empty."

    assert results[1]["score"] == 50
    assert results[1]["passed"] is False
    assert results[1]["issues"] == "Source text is empty."

def test_calculate_reference_similarity_returns_100_for_exact_match():
    from localisation_workbench.quality_scoring import calculate_reference_similarity

    score = calculate_reference_similarity(
        "Réinitialiser le mot de passe",
        "Réinitialiser le mot de passe",
    )

    assert score == 100.0


def test_calculate_reference_similarity_returns_lower_score_for_different_text():
    from localisation_workbench.quality_scoring import calculate_reference_similarity

    score = calculate_reference_similarity(
        "Bonjour",
        "Salut",
    )

    assert score < 100.0
    assert score >= 0.0