from it_spelling_bee.scoring import score_word
from it_spelling_bee.config import Settings


def test_score_bounds():
    settings = Settings()
    entry = {"text": "cane", "zipf": 5.0, "mask": 0}
    s = score_word(entry, None, settings)
    assert s >= 1
