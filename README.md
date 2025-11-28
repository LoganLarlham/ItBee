# Italian Spelling Bee (minimal MVP)

This is a minimal offline CLI implementation of the Italian Spelling Bee described in `ItBee_Plan.md`.

Overview
--------

This repository contains a small CLI game plus tools to build a local offline Italian lexicon. The core idea: generate a 7-letter board with a required center letter and score Italian words that use those letters.

Project layout
--------------

- `it_spelling_bee/` - main package
	- `cli.py` - command-line interface and REPL
	- `engine.py` - game engine, state, guesses, progress
	- `generator.py` - board generator (uses lexicon)
	- `letters.py` - normalization, masks, shuffle helpers
	- `lexicon/` - lexicon tooling
		- `build.py` - build local SQLite lexicon from wordfreq + Hunspell + overrides
		- `store.py` - small runtime lexicon store used by the generator
	- `rules.py` - validation rules (length, required letter, allowed letters)
	- `scoring.py` - scoring heuristics (zipf-based + length + pangram bonus)
	- `typing.py` - dataclasses for board/word types
	- `persistence.py` - (future) save/load game state
- `data/` - small sample resources and example whitelist/blacklist (not authoritative)
- `tests/` - pytest unit tests
- `PROJECT_SUMMARY.md`, `ItBee_Plan.md`, `README.md` - docs and notes

Quick start
-----------

1. Create and activate a virtualenv (recommended):

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install requirements:

```bash
python -m pip install -r requirements.txt
```

3. Build the full offline lexicon (recommended if you want a complete game):

```bash
# Required: point at an Italian Hunspell .dic file (LibreOffice or wooorm mirror)
python -m it_spelling_bee.lexicon.build \
	--dict /path/to/it_IT.dic \
	--whitelist data/whitelist.txt \
	--blacklist data/blacklist.txt \
	--out ~/.it_spelling_bee/lexicon.sqlite \
	--limit 200000
```

Notes:
- The builder intersects `wordfreq` tokens with an authoritative Hunspell `.dic` and applies blacklist/whitelist overrides. Precedence: blacklist > whitelist > dictionary.
- If you don't want to build, the repo includes a tiny sample lexicon used for quick testing.

4. Run the CLI:

```bash
python -m it_spelling_bee.cli
```

CLI tips
--------
- In-game commands: `help`, `shuffle`, `hint`, `list`, `score`, `giveup`, `printseed`, `quit`.
- `printseed` prints the current game's seed (decimal and hex) so you can reproduce the board with `--seed`.
- Accented letters are normalized by stripping diacritics (e.g. `è` -> `e`). Enter words without accents or they will be treated as their base letters.

Testing
-------

Run the unit test suite from the repository root (PYTHONPATH required if running from source):

```bash
PYTHONPATH=$(pwd) python -m pytest -q
```

Development notes
-----------------
- Hunspell `.dic` files are large and are ignored by `.gitignore` in this repo; keep authoritative dictionaries local and record their SHA256 in lexicon meta.
- The lexicon builder does not expand `.aff` rules. If you need inflected word forms, either provide an expanded list or add common inflections to `data/whitelist.txt`.
- The builder records provenance (paths + SHA256 + wordfreq limit/version + timestamp) in the SQLite `meta` table for reproducibility.

Updating Whitelist/Blacklist and Deploying to Web
--------------------------------------------------

To update the word lists used in the web application:

1. **Edit the lists**:
   - Add words to `data/whitelist.txt` (one word per line)
   - Add words to `data/blacklist.txt` (one word per line)

2. **Download Italian dictionary** (if needed):
   ```bash
   curl -L -o /tmp/it_IT.dic "https://cgit.freedesktop.org/libreoffice/dictionaries/plain/it_IT/it_IT.dic"
   ```

3. **Rebuild the lexicon**:
   ```bash
   python3 -m it_spelling_bee.lexicon.build \
       --dict /tmp/it_IT.dic \
       --whitelist data/whitelist.txt \
       --blacklist data/blacklist.txt \
       --out ~/.it_spelling_bee/lexicon.sqlite \
       --limit 200000
   ```

4. **Export to JSON for web**:
   ```bash
   python3 scripts/export_lexicon_to_json.py
   ```

5. **Deploy to Cloudflare Pages**:
   ```bash
   cd web && wrangler pages deploy . --project-name ape-italiana
   ```

The whitelist takes precedence over the dictionary, and the blacklist excludes words even if they're in the dictionary or whitelist.

If you want, I can add a short troubleshooting section or an example workflow for producing a reproducible board and sharing the seed with another player.
