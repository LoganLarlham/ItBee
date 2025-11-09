from typing import Iterable, Tuple
import random
import unicodedata

ALPHABET = "abcdefghijklmnopqrstuvwxyz"
LETTER_TO_BIT = {ch: 1 << (ord(ch) - ord('a')) for ch in ALPHABET}


def normalize_text(s: str) -> str:
    s = s.lower()
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s


def mask_of(text: str) -> int:
    """Convert text to a bitmask where each letter sets its corresponding bit.
    Only counts each letter once and normalizes text first."""
    text = normalize_text(text)
    # Only use the first occurrence of each letter, sorted for consistency
    unique_letters = sorted(set(text))
    m = 0
    for ch in unique_letters:
        if ch in LETTER_TO_BIT:
            m |= LETTER_TO_BIT[ch]
    return m


def uses_only(word_mask: int, board_mask: int) -> bool:
    return (word_mask & ~board_mask) == 0


def mask_includes(mask: int, letter: str) -> bool:
    letter = letter.lower()
    return bool(mask & LETTER_TO_BIT.get(letter, 0))


def shuffle_letters(required: str, others: Iterable[str], rng: random.Random) -> Tuple[str, Tuple[str, ...]]:
    others_list = list(others)
    rng.shuffle(others_list)
    return required, tuple(others_list)
