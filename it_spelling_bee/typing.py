from typing import TypedDict, Iterable, Tuple, Dict


class Letters(TypedDict):
    required: str
    others: Tuple[str, ...]


class WordEntry(TypedDict):
    text: str
    zipf: float
    mask: int


class Board(TypedDict):
    letters: Letters
    mask: int


class GeneratedBoard(TypedDict):
    letters: Letters
    words: Iterable[WordEntry]
    scores: Dict[str, int]
    total_points: int
    threshold: int
