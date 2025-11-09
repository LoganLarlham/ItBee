from it_spelling_bee.scoring import score_word
from it_spelling_bee.config import Settings
from it_spelling_bee.typing import WordEntry, GeneratedBoard, Letters

def test_score_basic_rules():
    settings = Settings()
    # Standard word
    entry = WordEntry(text="cane", zipf=5.0, mask=0)
    s = score_word(entry, None, settings)
    assert s >= 1
    assert s <= 50  # Respect score cap

    # Long rare word
    long_rare = WordEntry(text="zzzzzzzz", zipf=1.0, mask=0)
    s_rare = score_word(long_rare, None, settings)
    assert s_rare > s  # Rarer word should score higher
    assert s_rare <= 50  # Still respect cap

def test_score_length_bonus():
    settings = Settings()
    short = WordEntry(text="cat", zipf=5.0, mask=0)
    long = WordEntry(text="catting", zipf=5.0, mask=0)  # Same zipf, longer
    
    s_short = score_word(short, None, settings)
    s_long = score_word(long, None, settings)
    assert s_long > s_short  # Longer word scores higher with same frequency

def test_pangram_bonus():
    settings = Settings(pangram_bonus_points=7)
    word = WordEntry(text="abcdefg", zipf=5.0, mask=0b1111111)  # Uses all letters
    board = GeneratedBoard(
        letters=Letters(required="a", others=("b", "c", "d", "e", "f", "g")),
        words=[],
        scores={},
        total_points=0,
        threshold=0,
        mask=0b1111111
    )
    
    # Score with and without board context
    s_no_board = score_word(word, None, settings)
    s_with_board = score_word(word, board, settings)
    assert s_with_board == s_no_board + settings.pangram_bonus_points

def test_zipf_scoring():
    settings = Settings()
    # Test monotonicity: higher zipf (more common) -> lower score
    scores = []
    for zipf in [2.0, 3.0, 4.0, 5.0, 6.0, 7.0]:
        entry = WordEntry(text="test", zipf=zipf, mask=0)
        scores.append(score_word(entry, None, settings))
    
    # Verify scores decrease as zipf increases
    assert all(scores[i] >= scores[i+1] for i in range(len(scores)-1))
