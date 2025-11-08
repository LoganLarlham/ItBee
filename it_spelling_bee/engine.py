from dataclasses import dataclass, field
from typing import Set, Tuple

from .typing import GeneratedBoard


@dataclass
class GameState:
    board: GeneratedBoard
    found: Set[str] = field(default_factory=set)
    score: int = 0


class Engine:
    def __init__(self, board: GeneratedBoard):
        self.state = GameState(board=board)

    def guess(self, word: str) -> Tuple[bool, str | None, int | None]:
        w = word.lower()
        if w in self.state.found:
            return False, "duplicate", None
        if w not in self.state["board"]["scores"]:
            return False, "not in solution", None
        points = self.state["board"]["scores"][w]
        self.state.found.add(w)
        self.state.score += points
        return True, "ok", points

    def progress(self):
        board = self.state["board"]
        total = board["total_points"]
        return {"found": len(self.state.found), "total_words": len(board["words"]), "score": self.state.score, "threshold": board["threshold"], "total_points": total}

    def is_won(self) -> bool:
        return self.state.score >= self.state["board"]["threshold"]
