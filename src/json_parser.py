
import json
from json import JSONDecodeError


def find_json_blocks(text: str) -> list[dict]:
    """
    Find valid JSON objects or arrays embedded in text.
    """
    if not text:
        return []

    decoder = json.JSONDecoder()
    blocks = []
    index = 0

    while index < len(text):
        if text[index] not in "{[":
            index += 1
            continue

        try:
            value, end_index = decoder.raw_decode(text, index)
        except JSONDecodeError:
            index += 1
            continue

        if isinstance(value, (dict, list)):
            blocks.append({
                "value": value,
                "start": index,
                "end": end_index,
            })
            index = end_index
        else:
            index += 1

    return blocks


def flatten_json(value, path="$") -> list[dict]:
    """
    Recursively flatten JSON and retain paths.
    Only string values are returned for downstream text processing.
    """
    flattened = []

    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            flattened.extend(flatten_json(child, child_path))

    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_path = f"{path}[{index}]"
            flattened.extend(flatten_json(child, child_path))

    elif isinstance(value, str):
        flattened.append({
            "json_path": path,
            "text": value,
        })

    return flattened


def parse_and_flatten_message(message_id: str, text: str) -> list[dict]:
    """
    Parse JSON blocks and return flattened text with source metadata.
    """
    results = []

    for block_number, block in enumerate(find_json_blocks(text)):
        flattened_values = flatten_json(block["value"])

        for item in flattened_values:
            results.append({
                "message_id": message_id,
                "block_number": block_number,
                "json_path": item["json_path"],
                "text": item["text"],
            })

    return results
