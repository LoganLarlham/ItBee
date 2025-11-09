from dataclasses import dataclass, field
import json
import random
from typing import Set, Tuple, Dict, Any, Optional

from .typing import GeneratedBoard
from .letters import normalize_text


@dataclass
class GameState:
    board: GeneratedBoard
    found: Set[str] = field(default_factory=set)
    score: int = 0


class Engine:
    def __init__(self, board: GeneratedBoard):
        self.state = GameState(board=board)

    def guess(self, word: str) -> Tuple[bool, str | None, int | None]:
        """Process a guess and return (ok, message, points).

        Messages:
          - 'duplicate' when word already found
          - 'missing required letter' when required letter not present
          - 'contains invalid letter' when guess uses letters outside the board
          - 'not in solution' when guess passes above checks but isn't a valid word
        """
        text = normalize_text(word)
        if text in self.state.found:
            return False, "duplicate", None

        # access board via dataclass attribute
        board = self.state.board

        # prepare allowed letters set
        required = board.letters.required.lower()
        allowed = {required} | {c.lower() for c in board.letters.others}

        # check required letter
        if required not in text:
            return False, "missing required letter", None

        # check allowed letters
        for ch in text:
            if ch not in allowed:
                return False, "contains invalid letter", None

        # finally, check if the word is in the board's valid words
        if text not in board.scores:
            return False, "not in solution", None

        points = board.scores[text]
        self.state.found.add(text)
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
