from .typing import WordEntry, GeneratedBoard
from .config import Settings
from .letters import mask_of


def score_word(entry: WordEntry, board_mask: int, settings: Settings) -> int:
    # zipf in [1..8], higher is more common
    zipf = float(entry.zipf)
    alpha = settings.alpha
    freq_points = max(1, round(alpha * (8.0 - zipf)))
    text = entry.text
    min_len = settings.min_len
    len_points = max(0, len(text) - min_len)
    pangram_bonus = 0
    
    # if word uses all letters
    if board_mask != 0 and (entry.mask & board_mask) == board_mask:
        pangram_bonus = settings.pangram_bonus_points
    s = freq_points + len_points + pangram_bonus
    if s > 50:
        s = 50
    return s
