
import re

# Fields likely to contain actual message text.
TEXT_FIELDS = {
    "body",
    "content",
    "text",
    "message",
    "subject",
    "comment",
    "description",
}

# Fields that should not independently be treated as message text.
EXCLUDED_FIELDS = {
    "email",
    "email_address",
    "assignee",
    "reporter",
    "sender_email",
    "recipient_email",
}


def is_relevant_json_text(json_path: str, text: str) -> bool:
    """
    Decide whether a flattened JSON string is suitable for NER.
    """
    if not text or not text.strip():
        return False

    field_name = json_path.rsplit(".", 1)[-1].lower()

    if field_name in EXCLUDED_FIELDS:
        return False

    if field_name not in TEXT_FIELDS:
        return False

    # Exclude strings that are only email addresses.
    if re.fullmatch(r"[\w.+-]+@[\w.-]+\.\w+", text.strip()):
        return False

    return True
