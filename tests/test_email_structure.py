
from src.email_structure import (
    extract_salutations,
    extract_signatures,
    split_forwarded_content,
    parse_email_structure,
)


def test_extracts_multiple_recipients():
    text = "Hi Ritu and Megan,\n\nPlease review this."
    result = extract_salutations(text)

    assert len(result) == 1
    assert result[0]["text"] == "Ritu and Megan"


def test_extracts_indian_name():
    text = "Dear अरुण:\n\nPlease review."
    result = extract_salutations(text)

    assert result[0]["text"] == "अरुण"


def test_ignores_generic_greeting():
    text = "Dear Madam,\n\nPlease review."
    assert extract_salutations(text) == []


def test_extracts_signature():
    text = "Please review.\n\nRegards, Sarah"
    result = extract_signatures(text)

    assert len(result) == 1
    assert result[0]["text"] == "Sarah"


def test_extracts_signature_on_next_line():
    text = "Please review.\n\nRegards,\nSarah\nDelivery Head"
    result = extract_signatures(text)

    assert result[0]["text"] == "Sarah"


def test_detects_forwarded_message():
    text = (
        "Hi Tanvi,\nPlease review.\n\n"
        "-----Original Message-----\n"
        "From: Anita Rathore\n"
        "To: Tanvi"
    )

    result = split_forwarded_content(text)

    assert result["has_forwarded"] is True
    assert "Hi Tanvi" in result["outer_text"]
    assert "Anita Rathore" in result["forwarded_text"]


def test_message_without_forwarding():
    text = "Hi Amit,\n\nRegards, Rahul"

    result = split_forwarded_content(text)

    assert result["has_forwarded"] is False
    assert result["forwarded_text"] == ""


def test_parses_outer_and_forwarded_sections():
    text = (
        "Hi Tanvi,\n\nRegards, Sarah\n\n"
        "-----Original Message-----\n"
        "From: Anita Rathore"
    )

    result = parse_email_structure(text)

    assert result["has_forwarded"] is True
    assert result["outer_salutations"][0]["text"] == "Tanvi"
    assert result["outer_signatures"][0]["text"] == "Sarah"
