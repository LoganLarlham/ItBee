# Italian Spelling Bee — Project Summary & Next Steps

This document summarizes the current repository state and the work completed so far, and then lists concrete, prioritized next steps with implementation details, acceptance criteria, and rough effort estimates.

---

## Current state (what's implemented)

- Package: `it_spelling_bee` — Python package with minimal Phase 1 MVP.
- Modules implemented:
  - `__init__.py` — package metadata
  - `config.py` — `Settings` dataclass with plan defaults
  - `typing.py` — TypedDict definitions (`Letters`, `WordEntry`, `Board`, `GeneratedBoard`)
  - `letters.py` — normalization, `mask_of`, `uses_only`, and `shuffle_letters`
  - `lexicon/store.py` — runtime lexicon store. Prefers SQLite DB at `~/.it_spelling_bee/lexicon.sqlite` if present; otherwise uses bundled `data/lexicon_sample.jsonl`.
  - `lexicon/build.py` — builder script that uses `wordfreq` to build a local SQLite lexicon (writes to `~/.it_spelling_bee/lexicon.sqlite` by default)
  - `rules.py` — `RuleSet` and `is_valid()` verification logic
  - `scoring.py` — `score_word()` implementing Zipf inverse scoring, length bonus, pangram bonus, cap
  - `generator.py` — basic board generator using random sampling and the lexicon store (deterministic via seed)
  - `engine.py` — `GameState` and `Engine` with `guess`, `progress`, `is_won`
  - `cli.py` — CLI entrypoint with REPL supporting commands: `help`, `shuffle`, `list`, `score`, `giveup`, `quit` (basic)
  - `persistence.py` — simple save/load helpers (stub)

- Data included:
  - `it_spelling_bee/data/lexicon_sample.jsonl` — tiny sample JSONL used as fallback for rapid testing

- Tests:
  - `tests/test_letters.py` and `tests/test_scoring.py` — small pytest unit tests; they currently pass in the workspace environment

- Build & tooling:
  - `requirements.txt` includes `wordfreq` (required for lexicon build)
  - `setup.py` minimal package metadata
  - `.gitignore`, `README.md` updated with build instructions

---

## Work performed in this session (high level)

- Created the initial package scaffold and core modules.
- Implemented mask-based utilities and normalization for Italian token handling.
- Added a simple JSONL-backed lexicon sample for immediate offline runs.
- Added a `wordfreq`-based lexicon builder that constructs a SQLite database of tokens, zipf scores, and bitmasks; ran it successfully locally to produce `~/.it_spelling_bee/lexicon.sqlite` (48k entries with limit=50k).
- Updated runtime lexicon store to use SQLite when present, with efficient SQL queries to filter by required letter via mask bit testing.
- Implemented a basic generator, engine, and CLI to exercise the functionality.
- Added minimal pytest tests and verified they pass.
- Initialized git and committed the work in logical steps.

---

## How to run the project locally (summary)

1. Optional: create and activate a virtualenv.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

2. Install requirements:

```bash
python -m pip install -r requirements.txt
```

3. Build the full offline lexicon (optional but recommended):

```bash
python -m it_spelling_bee.lexicon.build --out ~/.it_spelling_bee/lexicon.sqlite --limit 50000
```

4. Run the CLI:

```bash
python -m it_spelling_bee.cli --seed 1234
```

The CLI auto-detects `~/.it_spelling_bee/lexicon.sqlite` if present; otherwise it uses the tiny bundled sample.

---

## Next steps (prioritized, detailed)

I. Improve `generator` to match plan requirements (High priority)

- Goal: Replace the current naive random-letter picker with a robust rejection-sampling generator that produces fair puzzles and is deterministic with `--seed`.

- Subtasks:
  1. Build a fast per-letter inverted index (either in-memory on first load or via SQLite index/queries): for each letter, list the words that contain it (already partially supported by the SQLite table with mask index; implement a precomputed list or SQL cache to avoid scanning entire table for each candidate).
  2. Implement weighted sampling for letters using historical frequency: compute per-letter weights from the lexicon by averaging zipf or token counts; down-weight rare letters (J K W X Y) unless `allow_rare_letters` is set.
  3. Enforce vowel/consonant constraints during sampling (at least 2 vowels, 3 consonants). Use a small helper to classify letters as vowel/consonant and resample if constraints fail.
  4. When a candidate 7-letter board is created, query candidate words that (a) contain only those letters, (b) include the required letter, and (c) meet `min_len`. Use bitmask filtering in SQL: `mask & ~board_mask == 0 AND (mask & required_bit) != 0`.
  5. Compute scores for all candidate words using `scoring.score_word()` and compute total points `T` and valid word count. Accept or reject the board based on `min_valid_words`, `max_valid_words`, `min_total_points`, `max_total_points` (from `Settings`). Limit the number of resamples (e.g., 1000 tries) and fall back to best candidate.

- Acceptance criteria:
  - Generator returns boards with `min_valid_words <= count <= max_valid_words` and `min_total_points <= total_points <= max_total_points` for a diverse set of seeds.
  - Deterministic behavior with `--seed` (same seed -> same board).
  - Generation time is reasonable: target < 200 ms for cached queries / < 2s worst-case without cache.

- Estimated effort: 6-12 hours (depending on caching approach).

II. Improve `lexicon` and store performance (Medium priority)

- Goal: Ensure lexicon queries are fast and memory-efficient.

- Subtasks:
  1. Add SQL functions or materialized helper tables: store `first_letter` or `letters_signature` columns if helpful.
  2. Precompute per-letter lists and optionally export them into a compact on-disk JSON or sqlite table for fast iteration.
  3. Add a CLI option `--dump-board` to emit board JSON with full solution set for debugging and developer verification.

- Acceptance criteria:
  - `iter_by_required(letter)` returns results within a few milliseconds for common letters.
  - `--dump-board` outputs a JSON file containing board letters, all valid words and scores.

- Estimated effort: 3-6 hours.

III. Expand CLI to match plan (Medium priority)

- Goal: Implement the rest of the CLI features described in the plan: `hint`, `restart`, session persistence, `--dump-board`, `--new`, and better display formatting.

- Subtasks:
  1. Implement `hint` command: choose an undiscovered valid word, reveal first and last letters, and apply a point penalty (configurable in `Settings`). Decide and document penalty rules.
  2. Implement `restart` and `--new` to start a different seeded or random board and persist it to a session file.
  3. Implement session persistence using `persistence.py` storing minimal state in `~/.it_spelling_bee/session.json` so a player can resume.
  4. Implement `--dump-board` CLI flag that writes the current board's full solution set and scores to a JSON file.
  5. Add optional colorized output toggled by Settings (simple flag).

- Acceptance criteria:
  - CLI includes implemented commands and persists session on exit.
  - `hint` correctly penalizes score and reveals a hint for an undiscovered word.

- Estimated effort: 4-8 hours.

IV. Expand tests and add property tests (High priority)

- Goal: Increase confidence and coverage to match plan's testing strategy.

- Subtasks:
  1. Add unit tests for `letters.mask_of`, `uses_only`, and mask invariants.
  2. Add property tests with Hypothesis for mask computations and rule invariants (e.g., if `uses_only(mask, board_mask)` then `mask & ~board_mask == 0`).
  3. Add generator golden tests for a few fixed seeds to ensure stable totals and thresholds.
  4. Add CLI integration tests using `pexpect` or similar to simulate a REPL session.

- Acceptance criteria:
  - Tests increase coverage and the generator golden tests reproduce stable outputs for selected seeds.

- Estimated effort: 6-10 hours.

V. Polish scoring and word-frequency decisions (Low/Medium priority)

- Goal: Tune parameters (`alpha`, `pangram_bonus_points`, `min_len`) to produce balanced play.

- Subtasks:
  1. Run analysis on lexicon distributions to choose good defaults and adjust `wordfreq` cutoff.
  2. Provide a small CLI tool that computes expected total points for a given board for designers.

- Estimated effort: 3-6 hours.

VI. Optional: embed lexicon in repo (not recommended)

- If you want the repo to be completely self-contained (no build/run step), we can commit `~/.it_spelling_bee/lexicon.sqlite` into the repository. This will make the repo large (tens to hundreds of MB). If you want this, I can prepare a `data/lexicon.sqlite` and add it, but consider using Git LFS for large files.

---

## Acceptance criteria for the Phase 1 MVP (recap)

1. Running `python -m it_spelling_bee.cli --seed 20250101` starts instantly after lexicon is built.
2. `--dump-board` shows >= 30 valid words and a sensible total points value for a few sample seeds.
3. Player can win by reaching ~75% of the total points (threshold derived from the board's total possible points).
4. Tests pass locally; add more unit/property tests until coverage > 85%.

---

If you'd like, I can start immediately on the top-priority item (improving `generator`) and iterate until it meets the acceptance criteria. Tell me to proceed and I will (I will update the todo list to mark the generator improvements as in-progress and make the code changes, adding tests and committing them as I go).
