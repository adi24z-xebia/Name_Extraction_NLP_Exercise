
from src.data_loader import load_input
from src.ner_extractor import (
    load_nlp_model,
    extract_entities_batch,
)


def main():
    print("Starting NER candidate extraction...")

    df = load_input()
    nlp = load_nlp_model()

    print(f"Loaded {len(df)} records.")
    print("Running spaCy NER...\n")

    total_person_candidates = 0

    for index, entities in enumerate(
        extract_entities_batch(
            df["data"],
            nlp
        )
    ):

        person_names = [
            entity["text"]
            for entity in entities
            if entity["label"] == "PERSON"
        ]

        total_person_candidates += len(person_names)

        # Inspect the first 20 records.
        if index < 20:
            print(f"ID: {df.iloc[index]['ID']}")

            print("All detected entities:", entities)
            print("PERSON candidates:", person_names)
            print("-" * 60)

    print("\nNER summary")
    print("-------------------")
    print(f"Records processed: {len(df)}")
    print(f"PERSON candidates: {total_person_candidates}")


if __name__ == "__main__":
    main()
