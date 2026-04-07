from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher


@dataclass
class QualityScoreResult:
    source_text: str
    translation_text: str
    reference_text: str | None
    qa_score: int | None
    reference_score: float | None
    score: int
    max_score: int
    passed: bool
    issues: list[str]

def calculate_reference_similarity(
    translation_text: str,
    reference_text: str,
) -> float:
    """
    Return a simple similarity score between translation and reference text.

    The score is a percentage from 0.0 to 100.0.
    """
    translation = translation_text.strip()
    reference = reference_text.strip()

    if not translation or not reference:
        return 0.0

    return round(SequenceMatcher(None, translation, reference).ratio() * 100, 2)


def score_translation_pair(
    source_text: str,
    translation_text: str,
    reference_text: str | None = None,
) -> QualityScoreResult:
    
    """
    Score a translation pair using simple, explainable validation rules.

    This is intentionally lightweight and deterministic so it is easy to test,
    extend, and surface in both CLI and UI workflows.
    """
    max_score = 100
    score = max_score
    issues: list[str] = []

    source = source_text.strip()
    translation = translation_text.strip()

    if not source:
        issues.append("Source text is empty.")
        score -= 50

    if not translation:
        issues.append("Translation text is empty.")
        score -= 50

    if source and translation and source == translation:
        issues.append("Translation is identical to source text.")
        score -= 25

    if source and translation:
        source_placeholders = source.count("{")
        translation_placeholders = translation.count("{")

        if source_placeholders != translation_placeholders:
            issues.append("Placeholder count does not match source text.")
            score -= 15

    score = max(score, 0)

    reference_score = None

    if reference_text and translation:
        reference_score = calculate_reference_similarity(translation_text, reference_text)
        score = round((score + reference_score) / 2)

    return QualityScoreResult(
        source_text=source_text,
        translation_text=translation_text,
        reference_text=reference_text,
        qa_score=score if reference_score is None else None,
        reference_score=reference_score,
        score=score,
        max_score=max_score,
        passed=score >= 70,
        issues=issues,
    )


def score_translation_rows(
    rows: list[dict[str, str]],
    source_key: str = "source",
    translation_key: str = "translation",
    reference_key: str | None = None,
) -> list[dict[str, object]]:
    """
    Score a list of localisation rows and return enriched row data.

    Each output row keeps the original source and translation values and adds:
    - qa_score
    - reference_score
    - score
    - max_score
    - passed
    - issues
    """
    scored_rows: list[dict[str, object]] = []

    for row in rows:
        source_text = str(row.get(source_key, "") or "")
        translation_text = str(row.get(translation_key, "") or "")
        reference_text = str(row.get(reference_key, "") or "") if reference_key else None

        result = score_translation_pair(
            source_text,
            translation_text,
            reference_text=reference_text,
        )

        scored_rows.append(
            {
                **row,
                "qa_score": result.qa_score,
                "reference_score": result.reference_score,
                "score": result.score,
                "max_score": result.max_score,
                "passed": result.passed,
                "issues": "; ".join(result.issues) if result.issues else "",
            }
        )

    return scored_rows