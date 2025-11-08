"""Build a local SQLite lexicon from wordfreq for Italian.

Usage:
    python -m it_spelling_bee.lexicon.build --out /path/to/lexicon.sqlite --limit 200000

This script requires the `wordfreq` package.
"""
import argparse
import sqlite3
from pathlib import Path
import sys

from ..letters import normalize_text, mask_of


def build(out_path: Path, limit: int = 200000):
    try:
        from wordfreq import top_n_list, zipf_frequency
    except Exception as e:
        print("wordfreq is required. Install with: pip install wordfreq")
        raise

    out_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(out_path))
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS words")
    cur.execute("CREATE TABLE words(clean_form TEXT PRIMARY KEY, zipf REAL, mask INTEGER)")

    # top_n_list returns most frequent tokens; we filter to Italian ones
    toks = top_n_list("it", limit)
    inserted = 0
    for tok in toks:
        text = normalize_text(tok)
        if not text.isalpha():
            continue
        if len(text) < 2:
            continue
        zipf = zipf_frequency(tok, "it")
        mask = mask_of(text)
        try:
            cur.execute("INSERT OR REPLACE INTO words(clean_form, zipf, mask) VALUES (?, ?, ?)", (text, zipf, mask))
            inserted += 1
        except Exception:
            continue

    conn.commit()
    cur.execute("CREATE INDEX IF NOT EXISTS idx_mask ON words(mask)")
    conn.commit()
    conn.close()
    print(f"Wrote {inserted} entries to {out_path}")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path.home() / ".it_spelling_bee" / "lexicon.sqlite")
    parser.add_argument("--limit", type=int, default=200000)
    args = parser.parse_args(argv)
    build(args.out, args.limit)


if __name__ == "__main__":
    main()
