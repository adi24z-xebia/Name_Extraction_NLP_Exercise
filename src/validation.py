
import pandas as pd

from src.config import INPUT_COLUMNS


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
