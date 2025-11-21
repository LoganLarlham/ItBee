import json
import sqlite3
from pathlib import Path
from typing import Iterable, Dict

from ..typing import WordEntry
from ..letters import mask_of, normalize_text
from ..config import Settings


class Lexicon:
    def __init__(self, db_path: Path | None = None):
        # Prefer a sqlite DB in user data path if available
        settings = Settings()
        default_db = settings.data_path / "lexicon.sqlite"
        if db_path is None and default_db.exists():
            db_path = default_db
        if db_path is None:
            # fallback to bundled sample
            here = Path(__file__).parent
            db_path = here / "data" / "lexicon_sample.jsonl"

        self._path = Path(db_path)
        self._use_sqlite = self._path.suffix == ".sqlite" and self._path.exists()
        self._entries = []  # type: list[WordEntry]
        self._by_required: Dict[str, list[WordEntry]] = {}
        self._conn = None
        if self._use_sqlite:
            self._conn = sqlite3.connect(str(self._path))
        else:
            self._load_jsonl()

    def _load_jsonl(self):
        if not self._path.exists():
            return
        with self._path.open("r", encoding="utf8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                text = obj.get("clean_form") or obj.get("text")
                if not text:
                    continue
                text = normalize_text(text)
                zipf = float(obj.get("zipf", 4.0))
                mask = int(obj.get("mask", 0))
                if mask == 0:
                    mask = mask_of(text)
                entry = WordEntry(text=text, zipf=zipf, mask=mask)
                self._entries.append(entry)
                # index by each unique letter in the word
                used = set(text)
                for ch in used:
                    self._by_required.setdefault(ch, []).append(entry)

    def iter_all(self) -> Iterable[WordEntry]:
        if self._use_sqlite and self._conn is not None:
            cur = self._conn.cursor()
            for row in cur.execute("SELECT clean_form, zipf, mask FROM words"):
                yield WordEntry(text=row[0], zipf=float(row[1]), mask=int(row[2]))
        else:
            yield from self._entries


    def iter_by_required(self, letter: str) -> Iterable[WordEntry]:
        l = letter.lower()
        # Check cache first
        if l in self._by_required:
            yield from self._by_required[l]
            return

        if self._use_sqlite and self._conn is not None:
            bit = 0
            # compute bit for letter
            if len(l) == 1 and 'a' <= l <= 'z':
                bit = 1 << (ord(l) - ord('a'))
            
            entries = []
            cur = self._conn.cursor()
            # mask & bit != 0
            for row in cur.execute("SELECT clean_form, zipf, mask FROM words WHERE (mask & ?) != 0", (bit,)):
                entry = WordEntry(text=row[0], zipf=float(row[1]), mask=int(row[2]))
                entries.append(entry)
            
            # Cache the result
            self._by_required[l] = entries
            yield from entries
        else:
            yield from self._by_required.get(l, [])
