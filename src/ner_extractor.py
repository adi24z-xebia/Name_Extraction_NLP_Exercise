
import spacy

from src.config import ENGLISH_MODEL
from src.preprocessing import preprocess_text
from src.candidate_cleanup import clean_person_candidate


def load_nlp_model():
    """Load the spaCy model once and reuse it."""
    try:
        return spacy.load(ENGLISH_MODEL)

    except OSError as exc:
        raise RuntimeError(
            f"Could not load spaCy model: {ENGLISH_MODEL}. "
            "Install it using: "
            "python -m spacy download en_core_web_sm"
        ) from exc


def extract_entities(text: str, nlp):
    """
    Extract named entities from a message.

    Returns candidate entities with their labels
    and positions in the processed text.
    """
    cleaned_text = preprocess_text(text)

    if not cleaned_text:
        return []

    doc = nlp(cleaned_text)

    return [
        {
            "text": entity.text,
            "label": entity.label_,
            "start": entity.start_char,
            "end": entity.end_char,
        }
        for entity in doc.ents
    ]


def extract_person_candidates(text: str, nlp):
    """Return cleaned entities classified as PERSON."""
    entities = extract_entities(text, nlp)

    candidates = []
    seen = set()

    for entity in entities:
        if entity["label"] != "PERSON":
            continue

        candidate = clean_person_candidate(entity["text"])

        if not candidate:
            continue

        # Case-insensitive deduplication, preserving first occurrence.
        key = candidate.casefold()

        if key not in seen:
            seen.add(key)
            candidates.append(candidate)

    return candidates


def extract_entities_batch(texts, nlp, batch_size=100):
    """
    Process multiple messages efficiently using spaCy's
    pipeline batching mechanism.
    """
    cleaned_texts = (
        preprocess_text(text) for text in texts
    )

    for doc in nlp.pipe(
        cleaned_texts,
        batch_size=batch_size,
    ):
        yield [
            {
                "text": entity.text,
                "label": entity.label_,
                "start": entity.start_char,
                "end": entity.end_char,
            }
            for entity in doc.ents
        ]
