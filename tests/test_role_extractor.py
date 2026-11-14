
from src.role_extractor import (
    clean_role_name,
    split_recipient_names,
    extract_sender_and_recipients,
)


def test_extracts_sender_and_single_recipient():
    result = extract_sender_and_recipients(
        "Hi Amit Verma,\n\nPlease review.\n\nRegards, Sarah"
    )

    assert result["recipients"] == ["Amit Verma"]
    assert result["sender"] == "Sarah"


def test_extracts_multiple_recipients():
    result = extract_sender_and_recipients(
        "Hi Ritu, Megan and Tanvi,\n\nPlease review."
    )

    assert result["recipients"] == ["Ritu", "Megan", "Tanvi"]


def test_extracts_sender_from_next_line():
    result = extract_sender_and_recipients(
        "Hello Amit,\n\nRegards,\nSarah\nDelivery Head"
    )

    assert result["sender"] == "Sarah"


def test_ignores_initials_only_signature():
    result = extract_sender_and_recipients(
        "Hi Amit,\n\nRegards,\nNN"
    )

    assert result["sender"] == ""


def test_removes_honorifics():
    assert clean_role_name("Dr. Amit Verma") == "Amit Verma"
    assert clean_role_name("Anirban ji") == "Anirban"
    assert clean_role_name("Trivedi ma'am") == "Trivedi"


def test_ignores_generic_recipient():
    result = extract_sender_and_recipients(
        "Dear Madam,\n\nPlease review.\n\nRegards, Sarah"
    )

    assert result["recipients"] == []
    assert result["sender"] == "Sarah"


def test_does_not_treat_thanks_sentence_as_signature():
    result = extract_sender_and_recipients(
        "Hi Amit,\n\nThanks for the update."
    )

    assert result["sender"] == ""


def test_forwarded_sender_is_not_outer_sender():
    result = extract_sender_and_recipients(
        "Hi Tanvi,\n\nRegards, Sarah\n\n"
        "-----Original Message-----\n"
        "From: Anita Rathore\n"
        "To: Tanvi"
    )

    assert result["sender"] == "Sarah"
    assert result["recipients"] == ["Tanvi"]


def test_splits_ampersand_recipients():
    assert split_recipient_names("Amit & Rahul") == [
        "Amit",
        "Rahul",
    ]
