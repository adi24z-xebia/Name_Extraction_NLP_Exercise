
from unittest.mock import Mock

from src.message_extractor import (
    extract_message_record,
    extract_mentions,
)

def make_empty_nlp():
    nlp = Mock()
    nlp.return_value.ents = []
    return nlp


def test_extract_message_record_roles_and_mentions():
    nlp = make_empty_nlp()

    record = extract_message_record(
        "1234567",
        "Hi Amit Verma and Rahul,\n\n"
        "Please coordinate with @Anirban.\n\n"
        "Regards,\nSarah",
        nlp,
    )

    assert record["ID"] == "1234567"
    assert record["sender"] == "Sarah"
    assert record["recipients"] == ["Amit Verma", "Rahul"]
    assert "Sarah" in record["all_names"]
    assert "Amit Verma" in record["all_names"]
    assert "Rahul" in record["all_names"]
    assert "Anirban" in record["all_names"]


def test_forwarded_sender_does_not_replace_outer_sender():
    nlp = make_empty_nlp()

    record = extract_message_record(
        "1234568",
        "Hi Tanvi,\n\n"
        "Please see the forwarded email.\n\n"
        "Regards,\nSarah\n\n"
        "---------- Forwarded message ----------\n"
        "Hi Anita,\n\n"
        "Regards,\nRohan",
        nlp,
    )

    assert record["sender"] == "Sarah"
    assert record["recipients"] == ["Tanvi"]

    assert "Rohan" in record["all_names"]
    assert "Anita" in record["all_names"]


def test_email_addresses_are_not_mentions():
    assert extract_mentions(
        "Contact amit@example.com or message @Rahul."
    ) == ["Rahul"]


def test_empty_message():
    record = extract_message_record("1234569", "", Mock())

    assert record == {
        "ID": "1234569",
        "all_names": [],
        "sender": "",
        "recipients": [],
    }
