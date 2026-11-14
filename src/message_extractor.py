
import re

from src.ner_extractor import extract_person_candidates
from src.json_parser import find_json_blocks, flatten_json
from src.json_field_filter import is_relevant_json_text
from src.email_structure import parse_email_structure
from src.role_extractor import (
    clean_role_name,
    extract_sender_and_recipients,
    split_recipient_names,
)


# Capture capitalized human-name mentions, including first names.
# The negative lookbehind prevents matching email addresses.
MENTION_PATTERN = re.compile(
    r"(?<![\w.@])@([A-Z][a-z]+(?:[ -][A-Z][a-z]+){0,2})\b"
)


def remove_json_blocks(text: str, blocks: list[dict]) -> str:
    """Replace JSON blocks with spaces while preserving newlines."""
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
    """Extract person candidates from plain text and relevant JSON fields."""
    if not text:
        return []

    json_blocks = find_json_blocks(text)

    plain_text = remove_json_blocks(text, json_blocks)
    plain_candidates = []

    if plain_text.strip():
        plain_candidates = extract_person_candidates(plain_text, nlp)

    results = []
    seen = set()

    def add_candidate(name, source, json_path=None, block_number=None):
        if not name:
            return

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

    for block_number, block in enumerate(json_blocks):
        for item in flatten_json(block["value"]):
            if not is_relevant_json_text(
                item["json_path"],
                item["text"],
            ):
                continue

            for name in extract_person_candidates(item["text"], nlp):
                add_candidate(
                    name,
                    source="json",
                    json_path=item["json_path"],
                    block_number=block_number,
                )

    return results


def extract_structural_names(text: str) -> list[str]:
    """Extract names explicitly identified in greetings and signatures."""
    if not text:
        return []

    structure = parse_email_structure(text)
    names = []

    # Greetings can contain multiple recipients.
    for greeting in structure["outer_salutations"]:
        names.extend(split_recipient_names(greeting["text"]))

    for greeting in structure["forwarded_salutations"]:
        names.extend(split_recipient_names(greeting["text"]))

    # Signatures may contain one name or a name with an email address.
    for signature in (
        structure["outer_signatures"]
        + structure["forwarded_signatures"]
    ):
        name = clean_role_name(signature["text"])

        if name:
            names.append(name)

    return names


def extract_mentions(text: str) -> list[str]:
    """Extract capitalized names explicitly written as @mentions."""
    if not text:
        return []

    return [
        match.group(1).strip()
        for match in MENTION_PATTERN.finditer(text)
    ]


def extract_message_record(
    message_id: str,
    text: str,
    nlp,
) -> dict:
    """
    Produce consolidated extraction results for one email.

    all_names includes candidates from ordinary text, JSON,
    greetings, signatures, and explicit @mentions.

    Sender and recipients are resolved only from the outer email.
    """
    if not text:
        return {
            "ID": str(message_id),
            "all_names": [],
            "sender": "",
            "recipients": [],
        }

    candidates = extract_message_person_candidates(
        message_id,
        text,
        nlp,
    )

    all_names = []
    seen = set()

    def add_name(name):
        if not name:
            return

        name = name.strip()
        key = name.casefold()

        if key not in seen:
            seen.add(key)
            all_names.append(name)

    # Names identified by spaCy in prose and relevant JSON fields.
    for candidate in candidates:
        add_name(candidate["name"])

    # Names explicitly identified in greetings and signatures.
    for name in extract_structural_names(text):
        add_name(name)

    # Explicit @mentions, including first-name mentions.
    for name in extract_mentions(text):
        add_name(name)

    roles = extract_sender_and_recipients(text)

    # Ensure identified sender and recipients also appear in all_names.
    add_name(roles["sender"])

    for recipient in roles["recipients"]:
        add_name(recipient)

    return {
        "ID": str(message_id),
        "all_names": all_names,
        "sender": roles["sender"],
        "recipients": roles["recipients"],
    }
