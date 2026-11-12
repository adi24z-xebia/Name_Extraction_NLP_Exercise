
from src.json_parser import (
    find_json_blocks,
    flatten_json,
    parse_and_flatten_message,
)


def test_finds_valid_json_object():
    text = '{"name": "Amit Verma"}'
    assert len(find_json_blocks(text)) == 1


def test_ignores_invalid_json_and_placeholders():
    text = "Dear {FirstName}. [[prompt]]"
    assert find_json_blocks(text) == []


def test_flattens_nested_objects():
    data = {
        "ticket": {
            "body": "Amit Verma will review this."
        }
    }

    result = flatten_json(data)

    assert result == [{
        "json_path": "$.ticket.body",
        "text": "Amit Verma will review this.",
    }]


def test_flattens_arrays():
    data = {
        "comments": [
            {"body": "Hello Amit"},
            {"body": "Regards, Rahul"},
        ]
    }

    result = flatten_json(data)

    assert result[0]["json_path"] == "$.comments[0].body"
    assert result[1]["json_path"] == "$.comments[1].body"


def test_preserves_message_id():
    result = parse_and_flatten_message(
        "1234567",
        '{"body": "Amit Verma will review this."}',
    )

    assert result[0]["message_id"] == "1234567"
    assert result[0]["text"] == "Amit Verma will review this."


def test_ignores_numbers_and_boolean_values():
    data = {"ticket_id": 123, "active": True}

    assert flatten_json(data) == []
