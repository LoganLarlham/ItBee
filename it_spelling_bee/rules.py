from dataclasses import dataclass
from typing import FrozenSet

from .typing import WordEntry
from .letters import normalize_text, mask_of, uses_only


@dataclass
class RuleSet:
    min_len: int
    alphabet: FrozenSet[str]


def is_valid(entry: WordEntry, board: dict | object, rules: RuleSet, required: str) -> bool:
    """Check if a word entry is valid for the given board and rules.
    
    Args:
        entry: The word entry to validate
        board: Board configuration (dict or GeneratedBoard)
        rules: Rule constraints
        required: The required letter that must be present
        
    Returns:
        bool: True if the word is valid, False otherwise
    """
    text = normalize_text(entry.text)
    # Get allowed letters set
    allowed_letters = None
    if isinstance(board, dict):
        allowed_letters = frozenset([board["letters"]["required"]] + list(board["letters"]["others"]))
    else:
        allowed_letters = frozenset([board.letters.required] + list(board.letters.others))
    
    # Basic validations
    if len(text) < rules.min_len:
        return False
    if required.lower() not in text:
        return False
    if any(ch not in rules.alphabet for ch in text):
        return False
    if any(ch not in allowed_letters for ch in text):
        return False
    
    return True
