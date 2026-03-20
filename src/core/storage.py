"""Persistência JSON simples — salva/carrega dados em %APPDATA%/Vantage."""
import json
import os
import sys
from pathlib import Path


def get_data_dir() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", str(Path.home())))
    else:
        base = Path.home() / ".local" / "share"
    data_dir = base / "Vantage"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def save_json(filename: str, data) -> None:
    path = get_data_dir() / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_json(filename: str, default=None):
    path = get_data_dir() / filename
    if not path.exists():
        return default if default is not None else []
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
