"""Wing defaults derived from Base.snap.

Base.snap is the BCF (Base Configuration File) — the Wing's clean-slate state.
We use it as the default starting point for any channel we render, so that
params not expressed in the DSL are filled with known Wing values rather than
invented ones.

Note: Base.snap predates the `tapwid` param. We add it with value 100 (Wing
default for this firmware version) when it's absent.
"""

import copy
from pathlib import Path
from functools import cache

from snapwright.wing.parser import load_snap

_BASE_SNAP_PATH = Path(__file__).parent.parent.parent / "data" / "reference" / "Base.snap"

# Wing default for tapwid — observed in all James/Levin/Priscilla snapshots
_TAPWID_DEFAULT = 100


@cache
def _load_base() -> dict:
    return load_snap(_BASE_SNAP_PATH)


def channel_defaults(number: int) -> dict:
    """Return a deep copy of the default channel state for channel `number`.

    Starts from Base.snap, then patches in any known params that Base predates.
    """
    base = _load_base()
    ch = copy.deepcopy(base["ae_data"]["ch"][str(number)])
    if "tapwid" not in ch:
        ch["tapwid"] = _TAPWID_DEFAULT
    return ch


def snap_template() -> dict:
    """Return a deep copy of Base.snap as a starting point for a full snapshot.

    Callers should update ae_data.ch entries and metadata as needed.
    """
    return copy.deepcopy(_load_base())
