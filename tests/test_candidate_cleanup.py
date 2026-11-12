
import pytest

from src.candidate_cleanup import clean_person_candidate


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("Hii Mei", "Mei"),
        ("Best - Colin", "Colin"),
        ("Kavya Gupta Sent", "Kavya Gupta"),
        ("Radhika Sent", "Radhika"),
        ("R. Arora's", "R. Arora"),
        ("  Amit   Verma  ", "Amit Verma"),
        ("Anirban Singh", "Anirban Singh"),
        ("", ""),
    ],
)
def test_clean_person_candidate(raw, expected):
    assert clean_person_candidate(raw) == expected


def test_does_not_invent_missing_name_parts():
    assert clean_person_candidate("Verma") == "Verma"


def test_does_not_remove_internal_punctuation():
    assert clean_person_candidate("Rekha C.") == "Rekha C."
