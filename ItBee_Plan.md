Italian Spelling Bee — CLI Project Plan & Spec

1) Project overview

A command‑line Italian word game inspired by the NYT Spelling Bee. Players create as many valid Italian words as possible using 7 letters, where one letter is required in every word. Points depend on word frequency in Italian: rarer words are worth more. The game ends when the player reaches a configurable score threshold derived from the total possible points for the current letter set.

Goals
	•	Fast, offline‑capable CLI game with clean UX
	•	Deterministic, testable core engine
	•	Modular design so the same engine can power a future web UI
	•	Configurable rules, sources, and scoring

Non‑goals (Phase 1)
	•	No graphics or web UI
	•	No online leaderboards
	•	No multiplayer

⸻

2) Game rules
	1.	The board has 7 distinct letters. One is the required letter.
	2.	A valid word:
	•	Uses only the 7 letters (repetition allowed)
	•	Includes the required letter at least once
	•	Meets a minimum length (default 4)
	•	Appears in the Italian lexicon (inflected forms allowed)
	•	Contains only plain letters a‑z (no apostrophes, hyphens, digits)
	•	Optional rule: disallow proper nouns and abbreviations
	3.	Scoring
	•	Base points from inverse frequency (rarer words score higher)
	•	Length bonus
	•	Pangram bonus if the word uses all 7 letters at least once
	4.	Duplicate submissions are not allowed
	5.	Win condition: reach threshold = ceil(total_possible_points * 0.75) by default

Edge cases and Italian specifics
	•	Letters J K W X Y are allowed if present in the lexicon, but the generator will heavily down‑weight them
	•	Accents and elisions are normalized away; words with apostrophes (e.g., l’amico) are not allowed in Phase 1
	•	Case‑insensitive matching

⸻

3) Data sources

Two interchangeable strategies, selectable via config:

A) “wordfreq” library (default)
	•	Use wordfreq (it) for token frequencies (Zipf scale) and inflected forms
	•	Pros: easy, broad coverage, frequency baked in
	•	Cons: noisy entries possible

B) Morph‑it! + frequency list
	•	Use Morph‑it! (Italian morphological lexicon) for inflected forms
	•	Join with external frequency list (e.g., itWaC/itTenTen derived lists)
	•	Pros: structured morphology
	•	Cons: extra preprocessing

Phase 1 default: wordfreq

Preprocessing steps (one‑time script)
	•	Build an on‑disk JSONL or SQLite lexicon table:
	•	lemma, form, clean_form, zipf, flags
	•	Filter by allowed alphabet, min length
	•	Deduplicate by clean_form keeping max zipf
	•	Store also per‑letter index to accelerate board generation

⸻

4) Scoring model

Define final score S(word) as:
	•	Frequency weight:
	•	zipf = wordfreq Zipf value in [1, 8] (higher = more common)
	•	freq_points = max(1, round(alpha * (8 - zipf)))
	•	Length bonus:
	•	len_points = max(0, length - min_len)
	•	Pangram bonus:
	•	pangram_bonus = pangram_bonus_points if uses all 7 letters else 0
	•	Final:
	•	S = freq_points + len_points + pangram_bonus

Default parameters
	•	alpha = 2.0
	•	min_len = 4
	•	pangram_bonus_points = 7
	•	Cap: S <= 50 to avoid outliers

Rationale
	•	Smooth inverse relation to frequency using Zipf scale
	•	Reward longer words modestly
	•	Keep a satisfying pangram moment

⸻

5) Board generation

Objective: pick 7 distinct letters and a required center letter that yield a fair puzzle: enough valid words and a healthy point budget.

Algorithm (rejection sampling)
	1.	Sample required letter from weighted distribution favoring mid‑frequency consonants and vowels. Down‑weight rare letters and those that produce too few words in historical stats.
	2.	Sample remaining 6 distinct letters from the same distribution with constraints to mix vowels/consonants (at least 2 vowels, 3 consonants), avoid duplicates.
	3.	Build candidate word list from lexicon index; filter by rules and required letter.
	4.	Compute total points T; require:
	•	min_valid_words <= count <= max_valid_words (defaults 20..200)
	•	min_total_points <= T <= max_total_points (defaults 80..1200)
	5.	If constraints fail, resample.

Determinism: allow a --seed to reproduce boards.

Performance: keep a per‑letter inverted index: for each letter set signature, quickly filter words using bit masks.

Bitmasking trick
	•	Map letters a..z to bits 0..25
	•	For a word, precompute mask(word)
	•	For a board, compute mask(board) and require mask(word) & ~mask(board) == 0 and mask(word) includes the required letter bit

⸻

6) CLI user experience

Commands during play
	•	Plain input: a word guess
	•	help: show rules summary
	•	shuffle: reshuffle display order of the 6 outer letters
	•	hint: reveal one undiscovered valid word’s first and last letter for a point penalty
	•	score: show current score and threshold
	•	list: show found words
	•	giveup: reveal all remaining words and end
	•	restart: start a new board
	•	quit: exit

Display
	•	Show letters as: [X]  a e i l n r t where X is required
	•	Show progress bar: #####----- 65% of goal
	•	Show counts: Found 12/73 words, Score 134 / 180

Persistence
	•	Store last session to a small JSON file in user config dir
	•	Optionally store daily seed for “daily puzzle”

Accessibility
	•	Clear messages, no colors required; optional color output can be toggled

⸻

7) Architecture & modules

Package name: it_spelling_bee

it_spelling_bee/
  __init__.py
  config.py            # load/validate settings
  letters.py           # letter utilities, masks, shuffling
  lexicon/
    __init__.py
    build.py           # preprocessing pipeline
    store.py           # read-only access to SQLite/JSONL
    filters.py         # normalization, alphabet checks
  scoring.py           # score functions
  rules.py             # validity checks
  generator.py         # board generator
  engine.py            # game state, turn logic
  cli.py               # argparse + main loop
  persistence.py       # save/load sessions
  telemetry.py         # optional simple metrics
  typing.py            # TypedDicts/Protocol

 tests/
  test_scoring.py
  test_rules.py
  test_letters.py
  test_generator.py
  test_engine.py
  test_cli.py
  fixtures/

Key data types
	•	Letters: NamedTuple(required: str, others: Tuple[str, ...])
	•	Board: TypedDict('Board', {'letters': Letters, 'mask': int})
	•	WordEntry: TypedDict('WordEntry', {'text': str, 'zipf': float, 'mask': int})
	•	GameState: score, found set, remaining words count, threshold, history

⸻

8) Core APIs (Python signatures)

# config.py
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
    seed: Optional[int] = None
    data_path: Path = Path("~/.it_spelling_bee").expanduser()

# letters.py
LetterMask = int

def mask_of(text: str) -> LetterMask: ...

def uses_only(word_mask: LetterMask, board_mask: LetterMask) -> bool: ...

# lexicon/store.py
class Lexicon:
    def __init__(self, db_path: Path): ...
    def iter_all(self) -> Iterable[WordEntry]: ...
    def iter_by_required(self, letter: str) -> Iterable[WordEntry]: ...

# rules.py
@dataclass
class RuleSet:
    min_len: int
    alphabet: FrozenSet[str]

def is_valid(entry: WordEntry, board: Board, rules: RuleSet, required: str) -> bool: ...

# scoring.py
def score_word(entry: WordEntry, letters: Letters, settings: Settings) -> int: ...

# generator.py
@dataclass
class GeneratedBoard:
    letters: Letters
    words: list[WordEntry]
    scores: dict[str, int]
    total_points: int
    threshold: int

def generate_board(lex: Lexicon, settings: Settings, rng: random.Random) -> GeneratedBoard: ...

# engine.py
@dataclass
class GameState:
    board: GeneratedBoard
    found: set[str]
    score: int

class Engine:
    def guess(self, word: str) -> tuple[bool, str | None, int | None]: ...  # ok?, message, points
    def progress(self) -> dict: ...
    def is_won(self) -> bool: ...

# cli.py
# argparse entry; runs the REPL

---

## 9) Preprocessing pipeline (lexicon/build.py)
1. Load from `wordfreq` all entries for Italian
2. Normalize:
   - Lowercase
   - Strip accents with Unicode NFD and keep ASCII letters
   - Remove tokens with non‑letters
3. Filter by length ≥ 2 to keep options for long boards
4. Compute and store:
   - `clean_form`, `zipf`, `mask`
5. Deduplicate by `clean_form` keeping highest Zipf
6. Save to SQLite:
   - Table `words(clean_form TEXT PRIMARY KEY, zipf REAL, mask INTEGER)`
   - Index on `mask`, and on `clean_form` prefix for lookups
7. Optional: precompute per‑letter lists to speed `iter_by_required`

Script outputs database at `~/.it_spelling_bee/lexicon.sqlite`

---

## 10) Game flow
1. Startup: load settings and lexicon
2. Generate board via `generate_board`
3. Show letters, totals, and prompt
4. For each input:
   - If command, execute
   - Else validate and score via engine
   - Update `found`, `score`, display feedback
5. If `score >= threshold`, show win screen and offer restart
6. Persist session on exit

---

## 11) Configuration
YAML file at `~/.it_spelling_bee/config.yml` with defaults:
```yaml
min_len: 4
alpha: 2.0
pangram_bonus_points: 7
min_valid_words: 20
max_valid_words: 200
min_total_points: 80
max_total_points: 1200
win_fraction: 0.75
allow_rare_letters: false
color: true
seed: null

Environment variables override: ITBEE_* (e.g., ITBEE_ALPHA=2.5)

⸻

12) Testing strategy
	•	Unit tests with pytest
	•	Property tests with Hypothesis for mask math and rule invariants
	•	Golden tests for a fixed seed to ensure stable totals and threshold
	•	CLI tests using pexpect for REPL behavior
	•	Performance test: board generation under 200 ms on a laptop for cached lexicon

Sample tests
	•	test_scoring.py: monotonicity with respect to zipf
	•	test_rules.py: required letter is enforced
	•	test_generator.py: constraints respected for given seed
	•	test_engine.py: duplicate guesses rejected, pangram bonus applied once

⸻

13) Performance considerations
	•	Bitmask filtering for letter inclusion
	•	SQLite query narrowing by required letter
	•	Caching candidate lists during generation
	•	Optional in‑memory cache after first load

⸻

14) Observability
	•	--verbose flag to print generation stats (candidate count, total points)
	•	--dump-board to emit JSON with letters and full solution set for debugging

⸻

15) Future work (Phase 2 web)
	•	Reuse engine, rules, scoring, generator
	•	Build a REST or local API facade
	•	Svelte/React client with honeycomb UI and keyboard input
	•	Daily puzzle publishing via seed derived from date
	•	Optional server‑side validation

⸻

16) Risks and mitigations
	•	Noisy lexicon: add stoplists and frequency thresholds, allow user toggles
	•	Too few words for some boards: generator rejection sampling with constraints
	•	Italian elisions and accents: keep Phase 1 simple; later add tokenization rules for elisions if desired

⸻

17) Minimal CLI spec

Command: itbee
Options:
	•	--new start new board
	•	--seed 1234 deterministic board
	•	--dump-board board.json export solution set

REPL:

[È]  a e i l n r t   Found 0/??   Score 0 / 0   Goal 0
> cane
+2  OK (length 4, zipf 5.1)
> shuffle
> list
> hint
> giveup


⸻

18) Deliverables
	•	Python package it_spelling_bee with modules above
	•	lexicon_build CLI to preprocess word list
	•	Test suite with coverage ≥ 85%
	•	README with install and usage instructions
	•	Example config and sample seeds

⸻

19) Acceptance criteria
	•	itbee --seed 20250101 starts a game instantly after lexicon is built
	•	dump-board shows ≥ 30 valid words and sensible total points
	•	Player can win by reaching 75 percent of total
	•	All tests pass locally