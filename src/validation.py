
import pandas as pd

from src.config import INPUT_COLUMNS, OUTPUT_COLUMNS


def validate_input(df: pd.DataFrame) -> None:
    """
    Validate the input dataset against the expected data contract.
    """

    # Check schema
    if list(df.columns) != INPUT_COLUMNS:
        raise ValueError(
            f"Expected columns {INPUT_COLUMNS}, "
            f"received {list(df.columns)}"
        )

    # Check missing or empty IDs
    if df["ID"].isna().any() or (df["ID"] == "").any():
        raise ValueError("Missing or empty IDs detected")

    # Check ID length
    invalid_ids = df[df["ID"].str.len() != 7]

    if not invalid_ids.empty:
        raise ValueError(
            f"Found {len(invalid_ids)} IDs "
            "that are not exactly 7 characters"
        )

    # Check uniqueness
    if df["ID"].duplicated().any():
        raise ValueError("Duplicate IDs detected")

    # Data can be empty; an empty message is not an invalid record.
    print("Input validation passed.")


def validate_output(output_df: pd.DataFrame, input_df: pd.DataFrame) -> None:
    """Validate the generated submission against the input dataset."""

    if list(output_df.columns) != OUTPUT_COLUMNS:
        raise ValueError(
            f"Expected output columns {OUTPUT_COLUMNS}, "
            f"received {list(output_df.columns)}"
        )

    if len(output_df) != len(input_df):
        raise ValueError(
            f"Row count mismatch: expected {len(input_df)}, "
            f"received {len(output_df)}"
        )

    if output_df["ID"].isna().any() or (output_df["ID"] == "").any():
        raise ValueError("Output contains missing or empty IDs")

    if output_df["ID"].duplicated().any():
        raise ValueError("Output contains duplicate IDs")

    if output_df["ID"].tolist() != input_df["ID"].tolist():
        raise ValueError("Output IDs do not match input IDs in original order")

    print("Output validation passed.")
