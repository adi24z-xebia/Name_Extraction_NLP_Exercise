
import pandas as pd

from src.config import BATCH_SIZE, OUTPUT_COLUMNS, OUTPUT_FILE
from src.data_loader import load_input
from src.ner_extractor import load_nlp_model
from src.message_extractor import extract_message_record
from src.validation import validate_output


def main():
    print("Starting name extraction pipeline...")

    # Load and validate the source dataset.
    input_df = load_input()
    print(f"Loaded {len(input_df)} email records.")

    # Load spaCy once and reuse it for every message.
    nlp = load_nlp_model()
    print("spaCy model loaded.")

    output_records = []
    total_records = len(input_df)

    # Process the input in manageable batches.
    for start in range(0, total_records, BATCH_SIZE):
        end = min(start + BATCH_SIZE, total_records)
        batch = input_df.iloc[start:end]

        for row in batch.itertuples(index=False):
            record = extract_message_record(
                message_id=row.ID,
                text=row.data,
                nlp=nlp,
            )

            output_records.append({
                "ID": record["ID"],
                "all_names": "; ".join(record["all_names"]),
                "sender": record["sender"],
                "recipients": "; ".join(record["recipients"]),
            })

        print(f"Processed {end}/{total_records} records.")

    # Create a DataFrame with the exact required column order.
    output_df = pd.DataFrame(
        output_records,
        columns=OUTPUT_COLUMNS,
    )

    # Create the output directory if it does not exist.
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Write the final CSV.
    output_df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig",
    )

    # Read the file back and validate the actual saved output.
    saved_df = pd.read_csv(
        OUTPUT_FILE,
        dtype=str,
        keep_default_na=False,
        encoding="utf-8-sig",
    )

    validate_output(saved_df, input_df)

    print("\nPipeline completed successfully.")
    print(f"Records processed: {len(output_df)}")
    print(f"Output file: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
