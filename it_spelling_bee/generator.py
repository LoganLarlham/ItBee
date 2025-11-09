import random
from typing import List, Tuple

from .lexicon.store import Lexicon
from .config import Settings
from .letters import mask_of, LETTER_TO_BIT
from .typing import Letters, GeneratedBoard, WordEntry
from .rules import RuleSet, is_valid
from .scoring import score_word


def _random_letters(rng: random.Random) -> Tuple[str, List[str]]:
    # pick 7 distinct letters from alphabet
    letters = list(LETTER_TO_BIT.keys())
    rng.shuffle(letters)
    picked = letters[:7]
    required = picked[0]
    others = picked[1:]
    return required, others


def generate_board(lex: Lexicon, settings: Settings, rng: random.Random) -> GeneratedBoard:
    # simple rejection sampling with limited tries
    tries = 0
    alphabet = frozenset(LETTER_TO_BIT.keys())
    rules = RuleSet(min_len=settings.min_len, alphabet=alphabet)
    while tries < 200:
        tries += 1
        required, others = _random_letters(rng)
        letters = Letters(required=required, others=tuple(others))
        board_mask = 0
        for ch in (required, *others):
            board_mask |= LETTER_TO_BIT[ch]
        # Create a board instance for validation
        # Create initial board for validating words
        temp_board = GeneratedBoard(
            letters=letters,
            words=[],  # Will be populated as we find valid words
            scores={},
            total_points=0,
            threshold=0,
            mask=board_mask
        )
        # Get candidates containing required letter
        candidates = list(lex.iter_by_required(required))
        valid = []
        scores = {}
        total = 0
        for entry in candidates:
            # Validate with temp board
            if is_valid(entry, temp_board, rules, required):
                sc = score_word(entry, temp_board, settings)
                valid.append(entry)
                scores[entry.text] = sc
                total += sc
        if settings.min_valid_words <= len(valid) <= settings.max_valid_words and settings.min_total_points <= total <= settings.max_total_points:
            threshold = int((total * settings.win_fraction) + 0.9999)
            return GeneratedBoard(letters=letters, words=list(valid), scores=scores, total_points=total, threshold=threshold, mask=board_mask)
    # fallback: return whatever we have from last attempt
    threshold = int((total * settings.win_fraction) + 0.9999)
    return GeneratedBoard(letters=letters, words=list(valid), scores=scores, total_points=total, threshold=threshold, mask=board_mask)
