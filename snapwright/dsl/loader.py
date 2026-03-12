"""DSL loader: resolve inheritance stacks into merged dicts, validate with Pydantic."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from snapwright.dsl.schema import AssemblyDef, InstrumentLayer, MusicianEntry

# PyYAML uses YAML 1.1 which treats `on`/`off`/`yes`/`no` as booleans.
# When used as dict keys (e.g. `on: true`) they become Python True/False keys.
# We remap them back to their intended string form after loading.
_YAML11_BOOL_KEYS = {True: "on", False: "off"}


def _load_yaml(path: Path) -> dict:
    """Load a YAML file, fixing YAML 1.1 boolean key coercion."""
    raw = yaml.safe_load(path.read_text()) or {}
    return _fix_bool_keys(raw)


def _fix_bool_keys(obj: object) -> object:
    """Recursively convert boolean dict keys back to their YAML 1.1 string form.

    Uses a strict `type() is bool` check to avoid the Python gotcha where
    `True == 1` and `False == 0` would incorrectly remap integer keys.
    """
    if isinstance(obj, dict):
        return {
            (_YAML11_BOOL_KEYS[k] if type(k) is bool else k): _fix_bool_keys(v)
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [_fix_bool_keys(i) for i in obj]
    return obj


def load_assembly(path: str | Path) -> tuple[AssemblyDef, Path]:
    """Load and validate an assembly file.

    Returns (assembly, dsl_root) where dsl_root is the ancestor directory
    that contains musicians/, overlays/, teams/, etc.

    Convention: assembly lives at <dsl_root>/teams/<team>/assembly.yaml.
    """
    path = Path(path).resolve()
    dsl_root = path.parent.parent.parent
    raw = _load_yaml(path)
    assembly = AssemblyDef.model_validate(raw)
    return assembly, dsl_root


def resolve_musician(entry: MusicianEntry, dsl_root: Path) -> dict[str, Any]:
    """Fully resolve a musician entry.

    Merges the inherits stack, applies overrides + offsets.
    Returns a merged dict: name, color, icon, mute, fader, sends, processing.
    """
    # 1. Resolve inherits stack
    inherits = entry.inherits or []
    merged: dict[str, Any] = {}
    for ref in inherits:
        file_dict = _resolve_file(dsl_root / ref, dsl_root)
        merged = _deep_merge(merged, file_dict)
    for field in ("name", "color", "icon", "mute", "fader", "trim", "main_on",
                   "mute_groups", "dcas"):
        val = getattr(entry, field)
        if val is not None:
            merged[field] = val
    # 3. Merge entry sends on top of musician-file sends (last writer wins per key)
    if entry.sends:
        merged_sends = dict(merged.get("sends", {}))
        merged_sends.update(entry.sends)
        merged["sends"] = merged_sends

    # 4. Apply processing overrides
    if entry.overrides:
        override_dict = entry.overrides.model_dump(exclude_none=True)
        if override_dict:
            existing = merged.get("processing", {})
            merged["processing"] = _deep_merge(existing, override_dict)
    # 5. Apply level offsets
    if entry.offsets:
        if entry.offsets.fader != 0.0:
            merged["fader"] = merged.get("fader", 0.0) + entry.offsets.fader
        if entry.offsets.gain != 0.0:
            proc = merged.setdefault("processing", {})
            flt = proc.setdefault("filters", {})
            flt["gain"] = flt.get("gain", 0.0) + entry.offsets.gain
    return merged


def _resolve_file(path: Path, dsl_root: Path) -> dict[str, Any]:
    """Load a YAML file and recursively resolve its own inherits."""
    raw: dict = _load_yaml(path)

    # Validate to normalise types (e.g. single string inherits → list)
    layer = InstrumentLayer.model_validate(raw)
    inherits = layer.inherits or []

    # Recursively resolve inherited files
    merged: dict[str, Any] = {}
    for ref in inherits:
        child = _resolve_file(dsl_root / ref, dsl_root)
        merged = _deep_merge(merged, child)

    # Merge this file's content on top (excluding the inherits key itself)
    this_dict = layer.model_dump(exclude_none=True, exclude={"inherits"})
    return _deep_merge(merged, this_dict)


def _deep_merge(base: dict, override: dict) -> dict:
    """Deep merge override into base.

    Rules:
    - Scalars:  override wins
    - Dicts:    recurse
    - Lists:    override wins (replacement, not element-wise merge)
    - None:     skipped (treated as "not set" — never clobbers base)
    """
    result = dict(base)
    for key, val in override.items():
        if val is None:
            pass  # "not set" — leave base value intact
        elif key in result and isinstance(result[key], dict) and isinstance(val, dict):
            result[key] = _deep_merge(result[key], val)
        else:
            result[key] = val
    return result
