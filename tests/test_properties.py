import pytest
from hypothesis import given, strategies as st
from it_spelling_bee.letters import mask_of, uses_only, LETTER_TO_BIT
from it_spelling_bee.rules import is_valid, RuleSet
from it_spelling_bee.typing import WordEntry, GeneratedBoard, Letters

@given(st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=1))
def test_mask_invariants(word):
    """Test that mask_of is consistent and reversible-ish."""
    mask = mask_of(word)
    
    # Mask should be non-zero for non-empty alpha string
    assert mask > 0
    
    # Check that every letter in word has its bit set in mask
    for ch in word:
        bit = LETTER_TO_BIT[ch]
        assert (mask & bit) == bit

@given(st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=1), 
       st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=7))
def test_uses_only_property(word, board_letters):
    """Test uses_only logic."""
    word_mask = mask_of(word)
    board_mask = mask_of(board_letters)
    
    result = uses_only(word_mask, board_mask)
    
    # Manual check
    expected = all(c in board_letters for c in word)
    assert result == expected

@given(st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=4))
def test_is_valid_invariants(word):
    """Test rule validation logic."""
    # Filter out words with > 7 unique letters as they can never be valid on a 7-letter board
    if len(set(word)) > 7:
        return

    # Construct a board that contains all letters of the word plus 'a' if needed
    chars = list(set(word))
    if 'a' not in chars:
        chars.append('a')
    while len(chars) < 7:
        chars.append('z') # padding
        
    required = chars[0]
    others = tuple(chars[1:7])
    
    letters = Letters(required=required, others=others)
    board_mask = mask_of("".join(chars))
    
    board = GeneratedBoard(
        letters=letters,
        words=[],
        scores={},
        total_points=0,
        threshold=0,
        mask=board_mask
    )
    
    entry = WordEntry(text=word, zipf=4.0, mask=mask_of(word))
    rules = RuleSet(min_len=4, alphabet=frozenset("abcdefghijklmnopqrstuvwxyz"))
    
    # Should be valid if word length >= 4 and contains required
    valid = is_valid(entry, board, rules, required)
    
    if len(word) >= 4 and required in word:
        assert valid
    else:
        assert not valid
