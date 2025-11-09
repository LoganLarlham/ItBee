import pytest
from it_spelling_bee.rules import RuleSet, is_valid
from it_spelling_bee.typing import WordEntry, GeneratedBoard, Letters
from it_spelling_bee.letters import mask_of

def test_basic_rules():
    alphabet = frozenset("abcdefghijklmnopqrstuvwxyz")
    rules = RuleSet(min_len=4, alphabet=alphabet)
    board = GeneratedBoard(
        letters=Letters(required="a", others=("b", "c", "d", "e", "f", "g")),
        words=[],
        scores={},
        total_points=0,
        threshold=0,
        mask=mask_of("abcdefg")
    )

    # Valid word
    valid = WordEntry(text="cade", zipf=5.0, mask=mask_of("cade"))
    assert is_valid(valid, board, rules, "a")

    # Too short
    short = WordEntry(text="cat", zipf=5.0, mask=mask_of("cat"))
    assert not is_valid(short, board, rules, "a")

    # Missing required letter
    no_req = WordEntry(text="bird", zipf=5.0, mask=mask_of("bird"))
    assert not is_valid(no_req, board, rules, "a")

    # Uses invalid letters
    invalid = WordEntry(text="cakes", zipf=5.0, mask=mask_of("cakes"))
    assert not is_valid(invalid, board, rules, "a")

def test_rule_edge_cases():
    alphabet = frozenset("abcdefghijklmnopqrstuvwxyz")
    rules = RuleSet(min_len=4, alphabet=alphabet)
    letters = Letters(required="a", others=("b", "c", "d", "e", "f", "g"))
    board_mask = mask_of("".join([letters.required, *letters.others]))
    
    board = GeneratedBoard(
        letters=letters,
        words=[],
        scores={},
        total_points=0,
        threshold=0,
        mask=board_mask
    )

    # Word with repeated letters but missing required
    repeat = WordEntry(text="deed", zipf=5.0, mask=mask_of("deed"))
    assert not is_valid(repeat, board, rules, "a")  # missing required 'a'

    # Long word using only valid letters including required
    long = WordEntry(text="fade", zipf=5.0, mask=mask_of("fade"))
    assert is_valid(long, board, rules, "a")    # Word with non-alphabet characters
    invalid = WordEntry(text="a'b'c", zipf=5.0, mask=mask_of("abc"))
    assert not is_valid(invalid, board, rules, "a")

def test_rule_required_letter():
    """Test required letter rules specifically"""
    alphabet = frozenset("abcdefghijklmnopqrstuvwxyz")
    rules = RuleSet(min_len=4, alphabet=alphabet)
    letters = Letters(required="a", others=("b", "c", "d", "e", "f", "g"))
    board_mask = mask_of("".join([letters.required, *letters.others]))
    
    board = GeneratedBoard(
        letters=letters,
        words=[],
        scores={},
        total_points=0,
        threshold=0,
        mask=board_mask
    )

        # Test words containing required letter in different positions
    # Only use words made from letters a,b,c,d,e,f,g
    valid_words = ["face", "bead", "cafe"]
    for word in valid_words:
        entry = WordEntry(text=word, zipf=5.0, mask=mask_of(word))
        assert is_valid(entry, board, rules, "a"), f"Word {word} should be valid"
    # Test another valid word
    entry = WordEntry(text="cage", zipf=5.0, mask=mask_of("cage"))
    assert is_valid(entry, board, rules, "a")