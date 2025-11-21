import pytest
from it_spelling_bee.generator import generate_board
from it_spelling_bee.lexicon.store import Lexicon
from it_spelling_bee.config import Settings
import random

@pytest.fixture
def lexicon():
    # Use the bundled sample lexicon for consistent testing
    return Lexicon(db_path=None)

def test_generator_determinism(lexicon):
    """Test that the generator produces the same board for the same seed."""
    settings = Settings(seed=12345, min_valid_words=1, min_total_points=1)
    rng1 = random.Random(12345)
    board1 = generate_board(lexicon, settings, rng1)
    
    rng2 = random.Random(12345)
    board2 = generate_board(lexicon, settings, rng2)
    
    assert board1.letters == board2.letters
    assert board1.total_points == board2.total_points
    assert len(board1.words) == len(board2.words)

def test_generator_constraints(lexicon):
    """Test that generated boards meet minimum constraints."""
    # Note: The sample lexicon is small, so we use lenient settings
    settings = Settings(
        seed=42,
        min_valid_words=5,
        max_valid_words=100,
        min_total_points=10,
        max_total_points=1000
    )
    rng = random.Random(42)
    board = generate_board(lexicon, settings, rng)
    
    assert len(board.words) >= settings.min_valid_words
    assert board.total_points >= settings.min_total_points
    # Check required letter is in all words
    req = board.letters.required
    for w in board.words:
        assert req in w.text
