import json
from pathlib import Path
from typing import Any, Dict, Optional

def save_session(path: Path, data: Dict[str, Any]):
    """Save the game session data to a JSON file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf8") as fh:
        json.dump(data, fh, indent=2)


def load_session(path: Path) -> Optional[Dict[str, Any]]:
    """Load the game session data from a JSON file."""
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError):
        return None
