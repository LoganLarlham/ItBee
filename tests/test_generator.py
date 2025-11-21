import random
import pytest
from it_spelling_bee.generator import generate_board, WeightedLetterSampler
from it_spelling_bee.config import Settings
from it_spelling_bee.lexicon.store import Lexicon
from it_spelling_bee.letters import mask_of
from it_spelling_bee.typing import WordEntry

class MockLexicon(Lexicon):
    """Mock lexicon for testing generator with words guaranteed to be valid for any board"""
    def __init__(self):
        # Create a variety of simple words that should work with any board
        # Each word uses 3-4 common letters and every vowel+consonant combo
        words = []
        for v in "aeiou":
            for c1 in "bcdfg":
                for c2 in "lmnrt":
                    w = f"{v}{c1}{v}{c2}"
                    words.append(WordEntry(text=w, zipf=4.0, mask=mask_of(w)))
        self._entries = words
        self._by_required = {}
        for w in words:
            for ch in set(w.text):
                self._by_required.setdefault(ch, []).append(w)

    def iter_all(self):
        return iter(self._entries)

    def iter_by_required(self, letter):
        # Return words containing the required letter
        return iter(self._by_required.get(letter, []))

def test_weighted_sampler():
    rng = random.Random(42)
    sampler = WeightedLetterSampler()
    required, others = sampler.sample_set(rng)
    
    assert len(required) == 1
    assert len(others) == 6
    assert required not in others
    assert len(set(others)) == 6  # All distinct
    
    # Check constraints (at least 2 vowels, 3 consonants)
    vowels = sum(1 for c in (required + "".join(others)) if c in "aeiou")
    assert vowels >= 2
    assert (7 - vowels) >= 3

def test_generate_board_constraints():
    settings = Settings(
        min_valid_words=2,
        max_valid_words=10,
        min_total_points=5,
        max_total_points=50,
        seed=42
    )
    lex = MockLexicon()
    rng = random.Random(42)
    
    board = generate_board(lex, settings, rng)
    
    # Check board structure
    assert board.letters.required
    assert len(board.letters.others) == 6
    assert len(set(board.letters.others)) == 6
    
    # Check constraints
    assert len(board.words) >= settings.min_valid_words
    assert len(board.words) <= settings.max_valid_words
    assert board.total_points >= settings.min_total_points
    assert board.total_points <= settings.max_total_points
    assert board.threshold == int((board.total_points * settings.win_fraction) + 0.9999)

def test_generate_board_deterministic():
    settings = Settings(seed=42)
    lex = MockLexicon()
    rng1 = random.Random(42)
    rng2 = random.Random(42)
    
    board1 = generate_board(lex, settings, rng1)
    board2 = generate_board(lex, settings, rng2)
    
    # Same seed should produce identical boards
    assert board1.letters.required == board2.letters.required
    assert board1.letters.others == board2.letters.others
    assert board1.total_points == board2.total_points
    assert board1.threshold == board2.threshold

def test_generate_board_scoring():
    settings = Settings()
    lex = MockLexicon()
    rng = random.Random(42)
    
    board = generate_board(lex, settings, rng)
    
    # Each word should have a score
    assert len(board.scores) == len(board.words)
    for word in board.words:
        assert word.text in board.scores
        assert 0 < board.scores[word.text] <= 50  # Score within bounds
    
    # Total points should match sum of scores
    assert board.total_points == sum(board.scores.values())