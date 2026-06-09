from pathlib import Path

_DIR = Path(__file__).resolve().parent


def asset_path(name: str) -> str:
    return str(_DIR / name)
