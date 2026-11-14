
import re



GREETING_PATTERN = re.compile(
    r"^[ \t]*(?:dear|hi|hii|hello|hey|"
    r"good morning|good afternoon|good evening)"
    r"\s+(?P<names>[^.!?\n]+?)\s*[,!:]?\s*$",
    flags=re.IGNORECASE | re.MULTILINE,
)



SIGNOFF_PATTERN = re.compile(
    r"^[ \t]*(?:regards|rgds|best|best regards|"
    r"thanks|thank you|thx|sincerely|cheers|"
    r"warm regards|kind regards)"
    r"(?:[ \t]*[,!—-][ \t]*(?P<name>[^\n]*))?"
    r"[ \t]*$",
    flags=re.IGNORECASE | re.MULTILINE,
)

FORWARDED_PATTERN = re.compile(
    r"^[ \t]*(?:"
    r"-{2,}\s*original message\s*-{2,}|"
    r"begin forwarded message:|"
    r"-{2,}\s*forwarded message\s*-{2,}"
    r")[ \t]*$",
    flags=re.IGNORECASE | re.MULTILINE,
)

GENERIC_RECIPIENTS = {
    "sir",
    "madam",
    "sir/madam",
    "team",
    "everyone",
    "all",
    "colleagues",
    "there",
}


def extract_salutations(text: str) -> list[dict]:
    """Extract greeting segments without deciding who is the sender."""

    results = []

    for match in GREETING_PATTERN.finditer(text):
        names = match.group("names").strip()

        if names.casefold() in GENERIC_RECIPIENTS:
            continue

        results.append({
            "text": names,
            "start": match.start("names"),
            "end": match.end("names"),
        })

    return results


def extract_signatures(text: str) -> list[dict]:
    """Extract names or text following common email sign-offs."""

    results = []

    for match in SIGNOFF_PATTERN.finditer(text):
        name = (match.group("name") or "").strip()

        # If the sign-off is on its own line, inspect the next
        # non-empty line for a possible signature.
        if not name:
            remaining = text[match.end():]
            next_lines = [
                line.strip()
                for line in remaining.splitlines()
                if line.strip()
            ]

            if next_lines:
                name = next_lines[0]

        if not name:
            continue

        results.append({
            "text": name,
            "start": match.start(),
            "end": match.end(),
        })

    return results


def split_forwarded_content(text: str) -> dict:
    """
    Separate the outer message from explicitly marked forwarded content.
    """

    match = FORWARDED_PATTERN.search(text)

    if not match:
        return {
            "outer_text": text,
            "forwarded_text": "",
            "has_forwarded": False,
        }

    return {
        "outer_text": text[:match.start()],
        "forwarded_text": text[match.start():],
        "has_forwarded": True,
    }


def parse_email_structure(text: str) -> dict:
    """Identify greetings, signatures and forwarded sections."""

    sections = split_forwarded_content(text)

    outer_text = sections["outer_text"]
    forwarded_text = sections["forwarded_text"]

    return {
        "has_forwarded": sections["has_forwarded"],
        "outer_text": outer_text,
        "forwarded_text": forwarded_text,
        "outer_salutations": extract_salutations(outer_text),
        "outer_signatures": extract_signatures(outer_text),
        "forwarded_salutations": extract_salutations(forwarded_text),
        "forwarded_signatures": extract_signatures(forwarded_text),
    }
