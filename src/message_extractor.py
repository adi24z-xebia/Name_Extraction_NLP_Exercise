
from src.ner_extractor import extract_person_candidates
from src.json_parser import find_json_blocks, flatten_json
from src.json_field_filter import is_relevant_json_text


def remove_json_blocks(text: str, blocks: list[dict]) -> str:
    """
    Replace valid JSON blocks with spaces while preserving newlines.
    This prevents duplicate NER extraction from the original message.
    """
    characters = list(text)

    for block in blocks:
        for index in range(block["start"], block["end"]):
            if characters[index] not in "\r\n":
                characters[index] = " "

    return "".join(characters)


def extract_message_person_candidates(
    message_id: str,
    text: str,
    nlp,
) -> list[dict]:
    """
    Extract person candidates from plain text and relevant JSON fields.

    Returns candidate names with their source information.
    """
    if not text:
        return []

    json_blocks = find_json_blocks(text)

    # Extract from the ordinary prose outside JSON blocks.
    plain_text = remove_json_blocks(text, json_blocks)
    plain_candidates = []

    if plain_text.strip():
        plain_candidates = extract_person_candidates(plain_text, nlp)

    results = []
    seen = set()

    def add_candidate(name, source, json_path=None, block_number=None):
        key = name.casefold()

        if key in seen:
            return

        seen.add(key)

        results.append({
            "message_id": str(message_id),
            "name": name,
            "source": source,
            "json_path": json_path,
            "block_number": block_number,
        })

    for name in plain_candidates:
        add_candidate(name, source="plain_text")

    # Extract from relevant string values inside JSON.
    for block_number, block in enumerate(json_blocks):
        flattened_values = flatten_json(block["value"])

        for item in flattened_values:
            if not is_relevant_json_text(
                item["json_path"],
                item["text"],
            ):
                continue

            json_candidates = extract_person_candidates(
                item["text"],
                nlp,
            )

            for name in json_candidates:
                add_candidate(
                    name,
                    source="json",
                    json_path=item["json_path"],
                    block_number=block_number,
                )

    return results
