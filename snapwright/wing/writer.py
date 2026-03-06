"""Write Wing .snap files (JSON)."""

import json
from pathlib import Path


def save_snap(data: dict, path: str | Path) -> None:
    """Write a Wing snapshot dict to a .snap file."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(data, f, separators=(",", ":"))


def set_channel(snap: dict, number: int, channel: dict) -> None:
    """Replace a channel in-place by 1-based number."""
    snap["ae_data"]["ch"][str(number)] = channel
