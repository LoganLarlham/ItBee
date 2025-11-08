import json
from pathlib import Path

def save_session(path: Path, data: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf8") as fh:
        json.dump(data, fh)


def load_session(path: Path) -> dict | None:
    if not path.exists():
        return None
    with path.open("r", encoding="utf8") as fh:
        return json.load(fh)
