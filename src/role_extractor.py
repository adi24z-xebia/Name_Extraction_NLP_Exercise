
import re

from src.email_structure import parse_email_structure


HONORIFIC_PREFIX = re.compile(
    r"^(?:(?:mr|mrs|ms|miss|dr|prof|justice|capt)\.?\s+)",
    flags=re.IGNORECASE,
)

HONORIFIC_SUFFIX = re.compile(
    r"\s+(?:ji|ma['’]?am)$",
    flags=re.IGNORECASE,
)

EMAIL_PATTERN = re.compile(
    r"\s*<[^<>@\s]+@[^<>@\s]+>\s*"
)

INITIALS_ONLY = re.compile(
    r"^(?:[A-Z]\.\s*){1,4}$|^[A-Z]{2,3}$"
)

GENERIC_NAMES = {
    "sir",
    "madam",
    "sir/madam",
    "team",
    "everyone",
    "all",
    "colleagues",
    "there",
}


def clean_role_name(value: str) -> str:
    """Clean a name extracted from a greeting or signature."""

    if not value:
        return ""

    name = value.strip()

    # Use only the first line of a signature.
    name = name.splitlines()[0].strip()

    # Remove an email address displayed alongside the name.
    name = EMAIL_PATTERN.sub("", name).strip()

    name = HONORIFIC_PREFIX.sub("", name).strip()
    name = HONORIFIC_SUFFIX.sub("", name).strip()

    name = name.strip(" \t\r\n,;:-—")
    name = re.sub(r"\s+", " ", name)

    if not name:
        return ""

    if name.casefold() in GENERIC_NAMES:
        return ""

    # Assignment rule: initials-only signatures are not names.
    if INITIALS_ONLY.fullmatch(name):
        return ""

    return name


def split_recipient_names(value: str) -> list[str]:
    """Split a greeting containing multiple recipients."""

    parts = re.split(
        r"\s*(?:,|;|\band\b|&)\s*",
        value,
        flags=re.IGNORECASE,
    )

    results = []
    seen = set()

    for part in parts:
        name = clean_role_name(part)

        if not name:
            continue

        key = name.casefold()

        if key not in seen:
            seen.add(key)
            results.append(name)

    return results


def extract_sender_and_recipients(text: str) -> dict:
    """
    Resolve the outer email sender and recipients.

    Sender comes from the last identifiable outer signature.
    Recipients come from the outer greeting.
    Forwarded content is not used for either field.
    """

    structure = parse_email_structure(text)

    recipients = []

    for greeting in structure["outer_salutations"]:
        recipients.extend(
            split_recipient_names(greeting["text"])
        )

    # Deduplicate recipients while preserving their order.
    unique_recipients = []
    seen_recipients = set()

    for name in recipients:
        key = name.casefold()

        if key not in seen_recipients:
            seen_recipients.add(key)
            unique_recipients.append(name)

    sender = ""

    # The final outer signature is the strongest available clue.
    for signature in reversed(structure["outer_signatures"]):
        candidate = clean_role_name(signature["text"])

        if candidate:
            sender = candidate
            break

    return {
        "sender": sender,
        "recipients": unique_recipients,
    }
