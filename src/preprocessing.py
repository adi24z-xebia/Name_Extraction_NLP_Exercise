
import html
import re


def preprocess_text(text: str) -> str:
    """
    Perform minimal text normalization.

    Preserve punctuation, capitalization, initials,
    mentions and message boundaries.
    """
    if not text:
        return ""

    text = html.unescape(text)

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")
    text = text.replace("\x00", "")

    # Normalize horizontal whitespace, not newlines.
    text = re.sub(r"[ \t]+", " ", text)

    # Reduce excessive blank lines.
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()
