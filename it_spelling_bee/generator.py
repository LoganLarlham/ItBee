import random
from typing import List, Tuple, FrozenSet

from .lexicon.store import Lexicon
from .config import Settings
from .letters import mask_of, LETTER_TO_BIT
from .typing import Letters, GeneratedBoard, WordEntry
from .rules import RuleSet, is_valid
from .scoring import score_word

# Italian letter frequencies (approximate) for weighted sampling
# Source: standard Italian frequency analysis
LETTER_WEIGHTS = {
    'a': 11.74, 'b': 0.92, 'c': 4.50, 'd': 3.73, 'e': 11.79, 'f': 0.95,
    'g': 1.64, 'h': 1.54, 'i': 11.28, 'l': 6.51, 'm': 2.51, 'n': 6.88,
    'o': 9.83, 'p': 3.05, 'q': 0.51, 'r': 6.37, 's': 4.98, 't': 5.62,
    'u': 3.01, 'v': 2.10, 'z': 0.49,
    # Rare/Foreign
    'j': 0.01, 'k': 0.01, 'w': 0.01, 'x': 0.01, 'y': 0.01
}

VOWELS = frozenset("aeiou")

class WeightedLetterSampler:
    def __init__(self, allow_rare: bool = False):
        self.weights = LETTER_WEIGHTS.copy()
        if not allow_rare:
            for ch in "jkwxy":
                self.weights[ch] = 0.0
        
        self.population = list(self.weights.keys())
        self.cum_weights = []
        total = 0.0
        for ch in self.population:
            total += self.weights[ch]
            self.cum_weights.append(total)
            
    def sample_set(self, rng: random.Random) -> Tuple[str, List[str]]:
        """
        Sample 7 distinct letters with constraints:
        - At least 2 vowels
        - At least 3 consonants
        Returns (required_letter, other_6_letters)
        """
        while True:
            # Sample 7 distinct letters using weights
            # random.choices is with replacement, so we need to loop until we get 7 distinct
            candidates = set()
            while len(candidates) < 7:
                # Sample a batch to reduce loops
                batch = rng.choices(self.population, cum_weights=self.cum_weights, k=10)
                for ch in batch:
                    candidates.add(ch)
                    if len(candidates) == 7:
                        break
            
            letters = list(candidates)
            vowels = sum(1 for c in letters if c in VOWELS)
            consonants = 7 - vowels
            
            if vowels >= 2 and consonants >= 3:
                # Valid set. Pick required letter from them using weights again?
                # Or just uniform from the set? Uniform is fine for the required one 
                # once the set is picked, but let's stick to the plan:
                # "Sample required letter... Sample remaining 6..."
                # Actually, the plan says:
                # 1. Sample required
                # 2. Sample others
                # But sampling a set and then picking required is equivalent and easier to validate constraints.
                
                rng.shuffle(letters)
                return letters[0], letters[1:]


def generate_board(lex: Lexicon, settings: Settings, rng: random.Random) -> GeneratedBoard:
    sampler = WeightedLetterSampler(allow_rare=settings.allow_rare_letters)
    alphabet = frozenset(LETTER_TO_BIT.keys())
    rules = RuleSet(min_len=settings.min_len, alphabet=alphabet)
    
    best_board = None
    best_score_diff = float('inf') # To find board closest to target range if we fail
    
    # Try up to 1000 times to find a valid board
    for _ in range(1000):
        required, others = sampler.sample_set(rng)
        letters = Letters(required=required, others=tuple(others))
        
        board_mask = 0
        for ch in (required, *others):
            board_mask |= LETTER_TO_BIT[ch]
            
        # 1. Get candidates containing required letter
        # This is now cached in memory by Lexicon
        candidates = list(lex.iter_by_required(required))
        
        valid = []
        scores = {}
        total_points = 0
        
        # 2. Filter candidates
        for entry in candidates:
            # Fast bitmask check: word must use ONLY board letters
            if (entry.mask | board_mask) == board_mask:
                # Detailed check (length, etc)
                # We create a temp board just for the signature, or pass mask directly if we optimized is_valid
                # is_valid signature: (entry, board, rules, required)
                # We can construct a lightweight object or just trust the mask check + length check
                if len(entry.text) < settings.min_len:
                    continue
                    
                # Double check invalid chars not in mask (already covered by mask check usually)
                # but let's use the official is_valid to be safe and consistent
                # We need a dummy board object or change is_valid. 
                # Let's make a minimal dummy board to satisfy type checker if needed, 
                # but actually we can just compute score.
                
                # Optimization: We know it has required letter (from iter_by_required)
                # We know it uses only board letters (from mask check)
                # We checked min_len.
                # So it is valid.
                
                # Calculate score
                # score_word needs entry, board_mask, settings
                sc = score_word(entry, board_mask, settings)
                valid.append(entry)
                scores[entry.text] = sc
                total_points += sc
        
        count = len(valid)
        
        # 3. Check constraints
        if (settings.min_valid_words <= count <= settings.max_valid_words and 
            settings.min_total_points <= total_points <= settings.max_total_points):
            
            threshold = int((total_points * settings.win_fraction) + 0.9999)
            return GeneratedBoard(
                letters=letters, 
                words=valid, 
                scores=scores, 
                total_points=total_points, 
                threshold=threshold, 
                mask=board_mask
            )
            
        # Track best failure just in case
        # We prefer boards that have ENOUGH words/points over those with too few
        if count > 0:
            # Heuristic: distance to center of ranges
            target_words = (settings.min_valid_words + settings.max_valid_words) / 2
            target_points = (settings.min_total_points + settings.max_total_points) / 2
            diff = abs(count - target_words) + abs(total_points - target_points) / 10.0
            
            if diff < best_score_diff:
                best_score_diff = diff
                threshold = int((total_points * settings.win_fraction) + 0.9999)
                best_board = GeneratedBoard(
                    letters=letters, 
                    words=valid, 
                    scores=scores, 
                    total_points=total_points, 
                    threshold=threshold, 
                    mask=board_mask
                )

    # If we failed to find a perfect board, return the best one we found
    if best_board:
        return best_board
        
    # Should be very rare to find NOTHING, but handle it
    return GeneratedBoard(
        letters=letters, 
        words=[], 
        scores={}, 
        total_points=0, 
        threshold=0, 
        mask=board_mask
    )
