
import pandas as pd

from src.ner_extractor import load_nlp_model
from src.evaluation import evaluate_predictions


BENCHMARK_FILE = "tests/fixtures/evaluation_samples.csv"


def main():
    print("Starting NER evaluation...")

    # Load labelled benchmark.
    df = pd.read_csv(
        BENCHMARK_FILE,
        dtype={"ID": "string", "data": "string"},
        keep_default_na=False,
        encoding="utf-8-sig",
    )

    # Validate benchmark structure.
    required_columns = {"ID", "data", "expected_names"}

    if not required_columns.issubset(df.columns):
        raise ValueError(
            f"Benchmark must contain columns: {required_columns}"
        )

    if df.empty:
        raise ValueError("Benchmark contains no labelled messages.")

    if df["ID"].duplicated().any():
        raise ValueError("Benchmark contains duplicate IDs.")

    if df["expected_names"].str.strip().eq("").any():
        raise ValueError(
            "Some messages have empty expected_names. "
            "Use [] when a message contains no human names."
        )

    print(f"Loaded {len(df)} labelled messages.")

    # Load spaCy model.
    nlp = load_nlp_model()

    print("Running evaluation...\n")

    results = evaluate_predictions(df, nlp)

    # Overall evaluation metrics.
    print("\nNER Evaluation Results")
    print("----------------------")
    print(f"Messages evaluated: {results['total_messages']}")
    print(f"True positives:     {results['true_positive']}")
    print(f"False positives:    {results['false_positive']}")
    print(f"False negatives:    {results['false_negative']}")
    print(f"Precision:          {results['precision']:.2%}")
    print(f"Recall:             {results['recall']:.2%}")
    print(f"F1 score:           {results['f1']:.2%}")

    print(
        "Exact-match messages: "
        f"{results['exact_match_messages']}/"
        f"{results['total_messages']}"
    )

    # Detailed message-level errors.
    print("\nMessage-level errors")
    print("--------------------")

    if not results["errors"]:
        print("No message-level errors found.")
    else:
        for error in results["errors"]:
            print(f"\nID: {error['ID']}")
            print(f"Expected:        {error['expected']}")
            print(f"Predicted:       {error['predicted']}")
            print(f"Matched:         {error['matched']}")
            print(f"False positives: {error['false_positives']}")
            print(f"False negatives: {error['false_negatives']}")

    print("\nEvaluation completed.")


if __name__ == "__main__":
    main()
