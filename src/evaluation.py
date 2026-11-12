
import json
import re
import unicodedata

import pandas as pd

from src.ner_extractor import extract_person_candidates


def normalize_name(name: str) -> str:
    """Normalize superficial differences without changing name identity."""
    name = unicodedata.normalize("NFC", str(name))
    name = name.strip()
    name = re.sub(r"\s+", " ", name)
    return name.casefold()


def evaluate_predictions(df: pd.DataFrame, nlp) -> dict:
    """
    Compare spaCy PERSON predictions with manually labelled names.

    expected_names must contain JSON arrays, for example:
    ["Amit Verma", "Laura"]
    """

    true_positive = 0
    false_positive = 0
    false_negative = 0
    exact_match_messages = 0
    error_details = []

    for row in df.itertuples(index=False):
        try:
            expected = json.loads(row.expected_names)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Invalid JSON in expected_names for ID {row.ID}"
            ) from exc

        if not isinstance(expected, list):
            raise ValueError(
                f"expected_names must be a JSON array for ID {row.ID}"
            )

        if not all(isinstance(name, str) for name in expected):
            raise ValueError(
                f"All expected names must be strings for ID {row.ID}"
            )

        actual = extract_person_candidates(row.data, nlp)

        expected_set = {
            normalize_name(name) for name in expected if name.strip()
        }

        actual_set = {
            normalize_name(name) for name in actual if name.strip()
        }

        matched = expected_set & actual_set
        false_positives = actual_set - expected_set
        false_negatives = expected_set - actual_set

        true_positive += len(matched)
        false_positive += len(false_positives)
        false_negative += len(false_negatives)

        if not false_positives and not false_negatives:
            exact_match_messages += 1
        else:
            error_details.append({
                "ID": row.ID,
                "expected": sorted(expected_set),
                "predicted": sorted(actual_set),
                "matched": sorted(matched),
                "false_positives": sorted(false_positives),
                "false_negatives": sorted(false_negatives),
            })

    precision = (
        true_positive / (true_positive + false_positive)
        if true_positive + false_positive else 0.0
    )

    recall = (
        true_positive / (true_positive + false_negative)
        if true_positive + false_negative else 0.0
    )

    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall else 0.0
    )

    return {
        "true_positive": true_positive,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "exact_match_messages": exact_match_messages,
        "total_messages": len(df),
        "errors": error_details,
    }
