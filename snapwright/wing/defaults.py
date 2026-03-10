"""Wing defaults derived from Init.snap (Wing factory reset).

Init.snap is the Wing's factory-reset state — a clean slate with no
configuration. We use it as the default starting point for any channel
we render, so that params not expressed in the DSL are filled with
known Wing factory values rather than accumulated debris from Base.snap.

Note: Init.snap predates the `tapwid` param. We add it with value 100
(Wing default for this firmware version) when it's absent.
"""

import copy
from functools import cache
from pathlib import Path

from snapwright.dsl.infrastructure import apply_firmware_patches, apply_infrastructure
from snapwright.wing.parser import load_snap

_INIT_SNAP_PATH = (
    Path(__file__).parent.parent.parent / "data" / "reference" / "Init.snap"
)

# Wing default for tapwid — observed in all James/Levin/Priscilla snapshots
_TAPWID_DEFAULT = 100


@cache
def _load_base() -> dict:
    return load_snap(_INIT_SNAP_PATH)


def channel_defaults(number: int) -> dict:
    """Return a deep copy of the default channel state for channel `number`.
    Starts from Init.snap (factory reset), then patches in any known params
    that Init.snap predates.
    """
    base = _load_base()
    ch = copy.deepcopy(base["ae_data"]["ch"][str(number)])
    if "tapwid" not in ch:
        ch["tapwid"] = _TAPWID_DEFAULT
    return ch


def snap_template() -> dict:
    """Return a deep copy of Init.snap with firmware patches and infrastructure applied.

    This is the canonical starting point for all snapshot rendering. It enforces
    the invariant that every rendered snapshot is based on Init.snap + infrastructure
    rather than the legacy Base.snap.
    """
    snap = copy.deepcopy(_load_base())
    apply_firmware_patches(snap)
    apply_infrastructure(snap)
    return snap
