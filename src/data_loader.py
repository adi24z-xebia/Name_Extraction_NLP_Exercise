
import pandas as pd

from src.config import INPUT_FILE
from src.validation import validate_input


def load_input() -> pd.DataFrame:
    """
    Load the input CSV and preserve the original IDs.
    """

    df = pd.read_csv(
        INPUT_FILE,
        dtype={
            "ID": "string",
            "data": "string",
        },
        keep_default_na=False,
        encoding="utf-8-sig",
    )

    validate_input(df)

    return df
