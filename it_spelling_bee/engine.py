from dataclasses import dataclass, field
import json
import random
from typing import Set, Tuple, Dict, Any, Optional

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
        # access board via dataclass attribute
        board = self.state.board
        if w not in board.scores:
            return False, "not in solution", None
        points = board.scores[w]
        self.state.found.add(w)
        self.state.score += points
        return True, "ok", points

    def progress(self):
        board = self.state.board
        total = board.total_points
        return {"found": len(self.state.found), "total_words": len(board.words), "score": self.state.score, "threshold": board.threshold, "total_points": total}

    def is_won(self) -> bool:
        return self.state.score >= self.state.board.threshold

    def get_hint(self) -> Optional[str]:
        """Get a random unguessed word hint showing first 2 letters and length."""
        unguessed = sorted([w.text for w in self.state.board.words if w.text not in self.state.found])
        if not unguessed:
            return None
        word = random.choice(unguessed)
        return f"Hint: {word[:2]}{'_' * (len(word) - 2)} ({len(word)} letters)"

    def get_board_data(self) -> Dict[str, Any]:
        """Get board data in JSON-friendly format."""
        board = self.state.board
        return {
            "required": board.letters.required,
            "others": list(board.letters.others),
            "total_words": len(board.words),
            "total_points": board.total_points,
            "threshold": board.threshold,
            "words": {w.text: board.scores[w.text] for w in board.words}
        }

    def dump_board(self) -> str:
        """Get board data as formatted JSON string."""
        return json.dumps(self.get_board_data(), indent=2)
