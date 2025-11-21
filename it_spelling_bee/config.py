from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Settings:
    min_len: int = 4
    alpha: float = 2.0
    pangram_bonus_points: int = 7
    min_valid_words: int = 20
    max_valid_words: int = 200
    min_total_points: int = 80
    max_total_points: int = 1200
    win_fraction: float = 0.75
    allow_rare_letters: bool = False
    hint_cost: int = 2
    use_colors: bool = True
    seed: Optional[int] = None
    data_path: Path = Path("~/.it_spelling_bee").expanduser()
