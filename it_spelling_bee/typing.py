from dataclasses import dataclass, field, asdict
from typing import Iterable, Tuple, Dict, List


@dataclass
class Letters:
    required: str
    others: Tuple[str, ...]


@dataclass
class WordEntry:
    text: str
    zipf: float
    mask: int

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class GeneratedBoard:
    letters: Letters
    words: List[WordEntry] = field(default_factory=list)
    scores: Dict[str, int] = field(default_factory=dict)
    total_points: int = 0
    threshold: int = 0
    mask: int = 0

    def to_dict(self) -> Dict:
        return {
            "letters": asdict(self.letters),
            "words": [w.to_dict() for w in self.words],
            "scores": self.scores,
            "total_points": self.total_points,
            "threshold": self.threshold,
            "mask": self.mask,
        }

