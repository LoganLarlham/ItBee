# Italian Spelling Bee (minimal MVP)

This is a minimal offline CLI implementation of the Italian Spelling Bee described in `ItBee_Plan.md`.

Run the CLI:

```bash
python -m it_spelling_bee.cli --seed 1234
```

Useful flags / commands:

- `printseed` (in-game command) — Print the current game's seed (decimal and hex). Useful for reproducing a board later with `python -m it_spelling_bee.cli --seed <value>`.

Building the full offline lexicon (recommended):

1. Install requirements (preferably in a virtualenv):

```bash
python -m pip install -r requirements.txt
```

2. Build the SQLite lexicon (this will download wordfreq data the first time):

```bash
# Required: point to an Italian hunspell .dic file via --dict or the ITBEE_DICT env var
python -m it_spelling_bee.lexicon.build --dict /path/to/it_IT.dic --out ~/.it_spelling_bee/lexicon.sqlite --limit 200000
```

Optional args:
- `--whitelist path/to/whitelist.txt` to force-include specific tokens
- `--blacklist path/to/blacklist.txt` to force-exclude specific tokens

You can also set environment variables as fallbacks: `ITBEE_DICT`, `ITBEE_WHITELIST`, `ITBEE_BLACKLIST`.

3. The program will automatically use `~/.it_spelling_bee/lexicon.sqlite` if present.

The repository includes a tiny sample lexicon for quick testing; building the full lexicon produces a complete offline database used by the generator.
