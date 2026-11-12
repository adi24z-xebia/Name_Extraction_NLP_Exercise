
import re


# Remove common email prefixes accidentally included in NER spans.
LEADING_NOISE = re.compile(
    r"^(?:hi|hii|hello|best|regards|thanks|thank you)"
    r"(?:[\s,:;!—-]+)",
    flags=re.IGNORECASE,
)

# Remove common email-client suffixes included in entity spans.
TRAILING_NOISE = re.compile(
    r"(?:\s+sent|\s+wrote|\s+forwarded message)$",
    flags=re.IGNORECASE,
)

POSSESSIVE_SUFFIX = re.compile(
    r"(?<=[A-Za-z])['’]s$",
    flags=re.IGNORECASE,
)

def clean_person_candidate(candidate: str) -> str:
    """
    Remove obvious email formatting noise from a PERSON candidate.

    This function does not infer missing names or decide whether
    a candidate is genuinely a human being.
    """
    if not candidate:
        return ""

    name = candidate.strip()

    # Remove leading greetings or sign-off labels.
    name = LEADING_NOISE.sub("", name).strip()

    # Remove trailing email-client text.
    name = TRAILING_NOISE.sub("", name).strip()

    # Remove possessive suffixes, e.g. "Arora's" -> "Arora".
    name = POSSESSIVE_SUFFIX.sub("", name).strip()

    # Remove leftover separators at the boundaries.
    name = name.strip(" \t\r\n,;:-—")

    # Collapse repeated internal whitespace.
    name = re.sub(r"\s+", " ", name)

    return name
