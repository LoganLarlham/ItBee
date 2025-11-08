import json
from pathlib import Path
from typing import Iterable, Dict

from ..typing import WordEntry
from ..letters import mask_of, normalize_text


class Lexicon:
    def __init__(self, db_path: Path | None = None):
        # If no path provided, use bundled sample
        if db_path is None:
            here = Path(__file__).parent
            db_path = here / "data" / "lexicon_sample.jsonl"
        self._path = Path(db_path)
        self._entries = []  # type: list[WordEntry]
        self._by_required: Dict[str, list[WordEntry]] = {}
        self._load()

    def _load(self):
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
                entry: WordEntry = {"text": text, "zipf": zipf, "mask": mask}
                self._entries.append(entry)
                # index by each unique letter in the word
                used = set(text)
                for ch in used:
                    self._by_required.setdefault(ch, []).append(entry)

    def iter_all(self) -> Iterable[WordEntry]:
        yield from self._entries

    def iter_by_required(self, letter: str) -> Iterable[WordEntry]:
        yield from self._by_required.get(letter.lower(), [])
