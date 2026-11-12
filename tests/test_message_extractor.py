
from src.message_extractor import (
    extract_message_person_candidates,
    remove_json_blocks,
)
from src.json_parser import find_json_blocks


def test_json_blocks_are_removed_from_plain_text():
    text = 'Hello Amit. {"body": "Hello Rahul"} Regards.'

    blocks = find_json_blocks(text)
    result = remove_json_blocks(text, blocks)

    assert "Hello Amit." in result
    assert "Regards." in result
    assert '"body"' not in result
    assert "Hello Rahul" not in result


def test_plain_text_candidates_are_preserved(monkeypatch):
    def fake_extractor(text, nlp):
        return ["Amit Verma"]

    monkeypatch.setattr(
        "src.message_extractor.extract_person_candidates",
        fake_extractor,
    )

    result = extract_message_person_candidates(
        "1234567",
        "Hello Amit Verma.",
        nlp=None,
    )

    assert result[0]["name"] == "Amit Verma"
    assert result[0]["source"] == "plain_text"


def test_json_body_candidates_are_extracted(monkeypatch):
    def fake_extractor(text, nlp):
        if "Amit Verma" in text:
            return ["Amit Verma"]
        return []

    monkeypatch.setattr(
        "src.message_extractor.extract_person_candidates",
        fake_extractor,
    )

    result = extract_message_person_candidates(
        "1234567",
        '{"body": "Amit Verma will review this."}',
        nlp=None,
    )

    assert len(result) == 1
    assert result[0]["name"] == "Amit Verma"
    assert result[0]["source"] == "json"
    assert result[0]["json_path"] == "$.body"


def test_json_email_metadata_is_not_extracted(monkeypatch):
    def fake_extractor(text, nlp):
        return ["Rachel Fitzgerald"]

    monkeypatch.setattr(
        "src.message_extractor.extract_person_candidates",
        fake_extractor,
    )

    result = extract_message_person_candidates(
        "1234567",
        '{"assignee": "rachel.fitzgerald@example.com"}',
        nlp=None,
    )

    assert result == []


def test_duplicate_candidates_are_removed(monkeypatch):
    def fake_extractor(text, nlp):
        return ["Amit Verma"]

    monkeypatch.setattr(
        "src.message_extractor.extract_person_candidates",
        fake_extractor,
    )

    result = extract_message_person_candidates(
        "1234567",
        'Amit Verma {"body": "Amit Verma"}',
        nlp=None,
    )

    assert len(result) == 1
