
from src.json_field_filter import is_relevant_json_text


def test_accepts_message_body():
    assert is_relevant_json_text(
        "$.ticket.body",
        "Amit Verma will review this.",
    )


def test_accepts_subject():
    assert is_relevant_json_text(
        "$.subject",
        "Meeting with Rahul",
    )


def test_rejects_assignee_email():
    assert not is_relevant_json_text(
        "$.ticket.assignee",
        "rachel.fitzgerald@acmecorp.example",
    )


def test_rejects_reporter_email():
    assert not is_relevant_json_text(
        "$.ticket.reporter",
        "nandiniv@acmecorp.example",
    )


def test_rejects_unknown_field():
    assert not is_relevant_json_text(
        "$.ticket.site",
        "MG Road",
    )


def test_rejects_empty_text():
    assert not is_relevant_json_text("$.body", "  ")
