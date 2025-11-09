from it_spelling_bee.letters import (
    mask_of, 
    uses_only, 
    mask_includes, 
    normalize_text,
    shuffle_letters,
    LETTER_TO_BIT
)
import random

def test_normalize_text():
    assert normalize_text("CIAO") == "ciao"
    assert normalize_text("è") == "e"
    assert normalize_text("perché") == "perche"
    assert normalize_text("l'amico") == "l'amico"  # preserves apostrophe for later filtering

def test_mask_operations():
    # Basic mask creation
    assert mask_of("abc") != 0
    assert mask_of("") == 0
    assert mask_of("aaa") == mask_of("a")  # repeated letters count once
    
    # uses_only validations
    board_mask = mask_of("abcdefg")
    assert uses_only(mask_of("abc"), board_mask)
    assert uses_only(mask_of(""), board_mask)  # empty string uses only board letters
    assert not uses_only(mask_of("xyz"), board_mask)
    assert not uses_only(mask_of("abcz"), board_mask)

def test_letter_bits():
    # Test each letter maps to unique bit
    seen_bits = set()
    for ch in "abcdefghijklmnopqrstuvwxyz":
        bit = LETTER_TO_BIT[ch]
        assert bit not in seen_bits, f"Duplicate bit for letter {ch}"
        seen_bits.add(bit)
        
        # Test mask_includes for each letter
        mask = mask_of(ch)
        assert mask_includes(mask, ch)
        assert not mask_includes(mask, chr(ord(ch) + 1))  # next letter

def test_shuffle_letters():
    rng = random.Random(42)  # fixed seed for deterministic test
    required = "a"
    others = ["b", "c", "d", "e", "f", "g"]
    
    # Test shuffle preserves required letter
    req, shuffled = shuffle_letters(required, others, rng)
    assert req == required
    assert set(shuffled) == set(others)
    assert len(shuffled) == len(others)
    
    # Multiple shuffles should give different orders
    _, shuffled2 = shuffle_letters(required, others, rng)
    assert shuffled != shuffled2  # very unlikely to be same with seed
