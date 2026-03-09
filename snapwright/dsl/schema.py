"""Pydantic models for the instrument-frame DSL (Phase 1).

File types in the DSL:
  - musicians/   — person+instrument configs (e.g. james-vox.yaml)
  - overlays/    — positional/environmental adjustments (e.g. near-drums.yaml)
  - templates/   — instrument-type baselines (future; not used in Phase 1)

All three share the InstrumentLayer schema. The assembly (teams/*/assembly.yaml)
references them via `inherits` lists in each MusicianEntry.

Merge semantics (Kustomize-style):
  - `inherits` lists are resolved depth-first, merged in order, last writer wins
  - Dicts merge recursively; lists are replaced as a unit
  - Inline `overrides` in a MusicianEntry mask the full resolved stack
  - `offsets` are applied additively after the stack resolves (level params only)
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# ---------------------------------------------------------------------------
# Processing sub-schemas — all fields Optional; these are partial merge layers
# ---------------------------------------------------------------------------


class FiltersConfig(BaseModel):
    hpf_on: bool | None = None
    hpf_freq: float | None = None
    hpf_slope: str | None = None  # Wing lcs: "12" | "18" | "24" dB/oct
    lpf_on: bool | None = None
    lpf_freq: float | None = None
    tilt_on: bool | None = None
    tilt: float | None = None  # tilt amount in dB (positive = high boost)


class EqBand(BaseModel):
    """One parametric EQ band (STD model only)."""

    freq: float
    gain: float = 0.0
    q: float = 1.0


class EqShelf(BaseModel):
    gain: float = 0.0
    freq: float = 80.0


class EqConfig(BaseModel):
    """EQ block.

    STD model: use typed bands / low_shelf / high_shelf fields.
    Other models (SOUL, PULSAR, E88, …): write Wing param names as extra fields
    and they pass through directly to Wing JSON.
    """

    model_config = ConfigDict(extra="allow")

    on: bool | None = None
    model: str | None = None
    low_shelf: EqShelf | None = None
    bands: list[EqBand] | None = None  # STD only — replaced as a unit in merges
    high_shelf: EqShelf | None = None


class LevelerConfig(BaseModel):
    """ECL33 leveler sub-section."""

    on: bool | None = None
    threshold: float | None = None
    recovery: int | None = None
    fast: bool | None = None


class CompressorConfig(BaseModel):
    """ECL33 compressor sub-section."""

    on: bool | None = None
    threshold: float | None = None
    ratio: float | None = None
    recovery: int | None = None
    fast: bool | None = None


class DynamicsConfig(BaseModel):
    """Dynamics block.

    ECL33: use typed leveler / compressor sub-sections.
    Other models (LA, NSTR, COMP, 9000C, …): write Wing param names as extra
    fields and they pass through directly to Wing JSON.
    """

    model_config = ConfigDict(extra="allow")

    on: bool | None = None
    model: str | None = None
    leveler: LevelerConfig | None = None  # ECL33
    compressor: CompressorConfig | None = None  # ECL33


class GateConfig(BaseModel):
    """Gate block.

    GATE model: use typed threshold / range / attack / hold / release / ratio.
    Other models (PSE, RIDE, 9000G, …): write Wing param names as extra fields.
    """

    model_config = ConfigDict(extra="allow")

    on: bool | None = None
    model: str | None = None  # GATE | PSE | RIDE | 9000G | …
    threshold: float | None = None
    range: float | None = None
    attack: float | None = None
    hold: float | None = None
    release: float | None = None
    ratio: int | str | None = None  # GATE: "1:3" string; RIDE: integer


class ProcessingConfig(BaseModel):
    filters: FiltersConfig | None = None
    eq: EqConfig | None = None
    dynamics: DynamicsConfig | None = None
    gate: GateConfig | None = None


# ---------------------------------------------------------------------------
# File-level schema (musician / overlay / template YAML files)
# ---------------------------------------------------------------------------


class InstrumentLayer(BaseModel):
    """Schema for musician, overlay, and template YAML files.

    `inherits` is consumed by the loader during merge-stack resolution and is
    not preserved in the resolved output.
    """

    inherits: list[str] | str | None = None
    name: str | None = None
    color: int | None = None
    icon: int | None = None
    mute: bool | None = None
    fader: float | None = None
    trim: float | None = None
    main_on: bool | None = None  # send to main L/R output directly
    main_2_on: bool | None = None  # send to main.2 (stream) — infra channels
    main_2_lvl: float | None = None  # main.2 routing level in dB
    preins: str | None = None  # pre-insert effect slot name (e.g. 'FX10')
    ptap: int | None = None  # Wing tap point (4=post-insert, 5=post-EQ; default=5)
    sends: dict[str, float] = Field(default_factory=dict)  # logical bus name → dB level
    processing: ProcessingConfig | None = None

    @model_validator(mode="before")
    @classmethod
    def _normalise_inherits(cls, data: Any) -> Any:
        if isinstance(data, dict) and isinstance(data.get("inherits"), str):
            data = dict(data)
            data["inherits"] = [data["inherits"]]
        return data


# ---------------------------------------------------------------------------
# Assembly-level schemas
# ---------------------------------------------------------------------------


class LevelOffsets(BaseModel):
    """Additive adjustments applied after the inheritance stack resolves.
    Values are in dB. Only level-type params (fader, gain) may be offset.
    """

    fader: float = 0.0
    gain: float = 0.0


class InputAssignment(BaseModel):
    source: str = "stage-box"
    input: int


class MusicianEntry(BaseModel):
    """A musician slot in an assembly file.

    Merge order:
      1. Files listed in `inherits` (depth-first, in order, last wins)
      2. Inline identity fields (name, color, icon, mute, fader)
      3. `overrides` processing block (masks the full stack)
      4. `offsets` applied additively to resolved level values
    """

    inherits: list[str] | str | None = None
    name: str | None = None
    color: int | None = None
    icon: int | None = None
    mute: bool | None = None
    fader: float | None = None
    trim: float | None = None
    main_on: bool | None = None
    main_2_on: bool | None = None  # send to main.2 (stream)
    main_2_lvl: float | None = None  # main.2 routing level in dB
    preins: str | None = None  # pre-insert effect slot name (e.g. 'FX10')
    ptap: int | None = None  # Wing tap point (4=post-insert, 5=post-EQ)
    # Processing
    overrides: ProcessingConfig | None = None
    offsets: LevelOffsets | None = None
    sends: dict[str, float] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def _normalise_inherits(cls, data: Any) -> Any:
        if isinstance(data, dict) and isinstance(data.get("inherits"), str):
            data = dict(data)
            data["inherits"] = [data["inherits"]]
        return data


class AssemblyDef(BaseModel):
    team_name: str
    musicians: dict[str, MusicianEntry]
    channels: dict[int, str]  # channel number → musician name
    inputs: dict[str, InputAssignment]  # musician name → stage input
    buses: dict[int, str]  # bus number → logical name
    monitors: dict[
        str, dict[str, float]
    ]  # monitor name → {musician: additive-dB offset}

    @field_validator("inputs", mode="before")
    @classmethod
    def _coerce_input_shorthand(cls, v: Any) -> Any:
        """Allow `kick: 2` shorthand for `kick: {source: stage-box, input: 2}`."""
        if not isinstance(v, dict):
            return v
        result = {}
        for musician, assignment in v.items():
            if isinstance(assignment, int):
                result[musician] = {"source": "stage-box", "input": assignment}
            else:
                result[musician] = assignment
        return result
