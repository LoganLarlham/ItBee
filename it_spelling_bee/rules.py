from dataclasses import dataclass
from typing import FrozenSet

from .typing import WordEntry, Board
from .letters import normalize_text, mask_of, uses_only


@dataclass
class RuleSet:
    min_len: int
    alphabet: FrozenSet[str]


def is_valid(entry: WordEntry, board: Board, rules: RuleSet, required: str) -> bool:
    text = normalize_text(entry["text"])
    if len(text) < rules.min_len:
        return False
    # only letters
    if any(ch not in rules.alphabet for ch in text):
        return False
    # uses only board letters
    if not uses_only(entry["mask"], board["mask"]):
        return False
    # includes required
    if required.lower() not in text:
        return False
    return True
