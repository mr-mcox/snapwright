"""Parse Wing .snap files (JSON) into Python dicts."""

import json
from pathlib import Path


def load_snap(path: str | Path) -> dict:
    """Load a Wing .snap file. Returns the full parsed dict."""
    path = Path(path)
    with path.open() as f:
        data = json.load(f)
    _validate(data, path)
    return data


def get_channel(snap: dict, number: int) -> dict:
    """Extract a single channel dict by 1-based number."""
    return snap["ae_data"]["ch"][str(number)]


# Wing snapshots report 'wing'; BCF files (e.g. Base.snap) report 'ngc-full'.
_KNOWN_MODELS = {"wing", "ngc-full"}


def _validate(data: dict, path: Path) -> None:
    model = data.get("creator_model")
    if model not in _KNOWN_MODELS:
        raise ValueError(
            f"{path}: unrecognised creator_model={model!r}"
            f" (expected one of {_KNOWN_MODELS})"
        )
    if "ae_data" not in data or "ch" not in data["ae_data"]:
        raise ValueError(f"{path}: missing ae_data.ch")
