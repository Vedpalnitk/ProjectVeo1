"""Simple JSON file storage for expense manager data."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict

DEFAULT_DATA_FILE = Path("expense_data.json")


def load_data(file_path: Path = DEFAULT_DATA_FILE) -> Dict[str, Any]:
    """Load the application data from a JSON file."""
    if not file_path.exists():
        return {"wallets": []}
    with file_path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def save_data(data: Dict[str, Any], file_path: Path = DEFAULT_DATA_FILE) -> None:
    """Persist the application data to a JSON file."""
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with file_path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, sort_keys=True)
        fh.write("\n")


def resolve_data_file(custom_path: str | None) -> Path:
    """Return the data file path given a user-supplied value."""
    if not custom_path:
        return DEFAULT_DATA_FILE
    expanded = os.path.expanduser(custom_path)
    return Path(expanded)
