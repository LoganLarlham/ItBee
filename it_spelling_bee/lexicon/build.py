"""Build a local SQLite lexicon from wordfreq for Italian.

Usage:
    python -m it_spelling_bee.lexicon.build --out /path/to/lexicon.sqlite --limit 200000

This script requires the `wordfreq` package.
"""
import argparse
import hashlib
import os
import sqlite3
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Optional, Set

from ..letters import normalize_text, mask_of


def _sha256_of_file(path: Path) -> str:
    if not path or not path.exists():
        return ""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def _parse_dic(path: Path, min_len: int = 2) -> Set[str]:
    s: Set[str] = set()
    if not path or not path.exists():
        return s
    with path.open(encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # split on first / (flags) and take left side
            tok = line.split("/", 1)[0]
            text = normalize_text(tok)
            if not text.isalpha():
                continue
            if len(text) < min_len:
                continue
            s.add(text)
    return s


def _parse_list(path: Optional[Path], min_len: int = 2) -> Set[str]:
    s: Set[str] = set()
    if path is None or not path.exists():
        return s
    with path.open(encoding="utf-8", errors="ignore") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            text = normalize_text(line)
            if not text.isalpha():
                continue
            if len(text) < min_len:
                continue
            s.add(text)
    return s


def build(out_path: Path, dict_path: Optional[Path], whitelist_path: Optional[Path], blacklist_path: Optional[Path], limit: int = 200000, min_len: int = 2):
    try:
        from wordfreq import top_n_list, zipf_frequency, __version__ as wordfreq_version
    except Exception:
        print("wordfreq is required. Install with: pip install wordfreq")
        raise

    if dict_path is None:
        raise ValueError("--dict PATH is required (or set ITBEE_DICT environment variable)")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(out_path))
    cur = conn.cursor()
    # schema with source and meta for provenance
    cur.execute("DROP TABLE IF EXISTS words")
    cur.execute("CREATE TABLE words(clean_form TEXT PRIMARY KEY, zipf REAL, mask INTEGER, source TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT)")

    # load authoritative dictionary and lists
    dict_set = _parse_dic(dict_path, min_len=min_len)
    whitelist = _parse_list(whitelist_path, min_len=min_len)
    blacklist = _parse_list(blacklist_path, min_len=min_len)

    toks = top_n_list("it", limit)

    counts = {
        "dict_entries": len(dict_set),
        "whitelist_entries": len(whitelist),
        "blacklist_entries": len(blacklist),
        "tokens_examined": 0,
        "accepted_whitelist": 0,
        "accepted_dictionary": 0,
        "excluded_blacklist": 0,
        "rows_written": 0,
    }

    for tok in toks:
        counts["tokens_examined"] += 1
        norm = normalize_text(tok)
        if not norm.isalpha():
            continue
        if len(norm) < min_len:
            continue

        if norm in blacklist:
            counts["excluded_blacklist"] += 1
            continue

        source = None
        if norm in whitelist:
            source = "whitelist"
            counts["accepted_whitelist"] += 1
        elif norm in dict_set:
            source = "dictionary"
            counts["accepted_dictionary"] += 1
        else:
            continue

        # compute zipf and mask and insert
        try:
            zipf = zipf_frequency(tok, "it")
        except Exception:
            zipf = 0.0
        mask = mask_of(norm)
        try:
            cur.execute("INSERT OR REPLACE INTO words(clean_form, zipf, mask, source) VALUES (?, ?, ?, ?)", (norm, zipf, mask, source))
            counts["rows_written"] += 1
        except Exception:
            continue

    # indices
    conn.commit()
    cur.execute("CREATE INDEX IF NOT EXISTS idx_mask ON words(mask)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_zipf ON words(zipf)")

    # write provenance
    cur.execute("INSERT OR REPLACE INTO meta(key, value) VALUES (?, ?)", ("dict_path", str(dict_path)))
    cur.execute("INSERT OR REPLACE INTO meta(key, value) VALUES (?, ?)", ("dict_sha256", _sha256_of_file(dict_path)))
    cur.execute("INSERT OR REPLACE INTO meta(key, value) VALUES (?, ?)", ("whitelist_path", str(whitelist_path) if whitelist_path else ""))
    cur.execute("INSERT OR REPLACE INTO meta(key, value) VALUES (?, ?)", ("whitelist_sha256", _sha256_of_file(whitelist_path) if whitelist_path else ""))
    cur.execute("INSERT OR REPLACE INTO meta(key, value) VALUES (?, ?)", ("blacklist_path", str(blacklist_path) if blacklist_path else ""))
    cur.execute("INSERT OR REPLACE INTO meta(key, value) VALUES (?, ?)", ("blacklist_sha256", _sha256_of_file(blacklist_path) if blacklist_path else ""))
    cur.execute("INSERT OR REPLACE INTO meta(key, value) VALUES (?, ?)", ("wordfreq_limit", str(limit)))
    cur.execute("INSERT OR REPLACE INTO meta(key, value) VALUES (?, ?)", ("wordfreq_version", str(wordfreq_version)))
    cur.execute("INSERT OR REPLACE INTO meta(key, value) VALUES (?, ?)", ("build_ts_utc", datetime.now(timezone.utc).isoformat()))

    conn.commit()
    conn.close()

    # logging
    print("Build summary:")
    for k, v in counts.items():
        print(f"  {k}: {v}")
    print(f"Wrote {counts['rows_written']} entries to {out_path}")


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path.home() / ".it_spelling_bee" / "lexicon.sqlite")
    parser.add_argument("--limit", type=int, default=200000)
    args = parser.parse_args(argv)
    build(args.out, args.limit)


if __name__ == "__main__":
    main()
