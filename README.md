# Italian Spelling Bee (minimal MVP)

This is a minimal offline CLI implementation of the Italian Spelling Bee described in `ItBee_Plan.md`.

Run the CLI:

```bash
python -m it_spelling_bee.cli --seed 1234
```

Building the full offline lexicon (recommended):

1. Install requirements (preferably in a virtualenv):

```bash
python -m pip install -r requirements.txt
```

2. Build the SQLite lexicon (this will download wordfreq data the first time):

```bash
python -m it_spelling_bee.lexicon.build --out ~/.it_spelling_bee/lexicon.sqlite --limit 200000
```

3. The program will automatically use `~/.it_spelling_bee/lexicon.sqlite` if present.

The repository includes a tiny sample lexicon for quick testing; building the full lexicon produces a complete offline database used by the generator.
