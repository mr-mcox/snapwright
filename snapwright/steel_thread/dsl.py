"""Channel-frame DSL models for the Phase 0 steel thread.

This is throwaway scaffolding. The instrument-frame DSL gets designed in Phase 1.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, model_validator

SOURCE_GROUP_MAP = {
    "stage-box": "A",
    "local": "B",  # local inputs on the desk itself
    "usb": "C",  # USB/computer playback
    "off": "OFF",
}


class InputConfig(BaseModel):
    source: str = "stage-box"
    input: int = 1

    def to_wing_conn(self) -> dict:
        grp = SOURCE_GROUP_MAP.get(self.source)
        if grp is None:
            raise ValueError(
                f"Unknown input source: {self.source!r}. Known: {list(SOURCE_GROUP_MAP)}"
            )
        return {"grp": grp, "in": self.input, "altgrp": "OFF", "altin": 1}


class FiltersConfig(BaseModel):
    hpf_on: bool = False
    hpf_freq: float = 80.0  # Hz
    lpf_on: bool = False
    lpf_freq: float = 20000.0  # Hz
    tilt_on: bool = False


class EqBand(BaseModel):
    gain: float = 0.0  # dB
    freq: float = 1000.0  # Hz
    q: float = 1.0


class EqShelf(BaseModel):
    gain: float = 0.0  # dB
    freq: float = 1000.0  # Hz


class EqConfig(BaseModel):
    on: bool = False
    model: str = "STD"
    low_shelf: EqShelf = EqShelf()
    bands: list[EqBand] = []  # up to 4 bands; omitted bands stay at defaults
    high_shelf: EqShelf = EqShelf()


class LevelerConfig(BaseModel):
    on: bool = False
    threshold: float = -10.0  # dB
    recovery: int = 50  # ms
    fast: bool = False


class CompressorConfig(BaseModel):
    on: bool = False
    threshold: float = -10.0  # dB
    ratio: float = 3.0
    recovery: int = 100  # ms
    fast: bool = False


class DynamicsConfig(BaseModel):
    on: bool = False
    model: str = "COMP"
    # ECL33-specific sub-sections (ignored for other models)
    leveler: LevelerConfig = LevelerConfig()
    compressor: CompressorConfig = CompressorConfig()


class GateConfig(BaseModel):
    on: bool = False
    threshold: float = -40.0  # dB
    range: float = 40.0  # dB
    attack: float = 10.0  # ms
    hold: float = 10.0  # ms
    release: float = 200.0  # ms


class SendConfig(BaseModel):
    on: bool = False
    level: float = -144.0
    mode: Literal["PRE", "POST"] = "POST"


class ChannelConfig(BaseModel):
    channel: int
    name: str = ""
    color: int = 0
    icon: int = 0
    input: InputConfig = InputConfig()
    fader: float = 0.0
    mute: bool = False
    filters: FiltersConfig = FiltersConfig()
    eq: EqConfig = EqConfig()
    dynamics: DynamicsConfig = DynamicsConfig()
    gate: GateConfig = GateConfig()
    sends: dict[str, SendConfig] = {}

    @model_validator(mode="after")
    def _normalise_sends(self) -> ChannelConfig:
        # Accept "bus1" or "1", "MX1" etc.
        normalised: dict[str, SendConfig] = {}
        for key, val in self.sends.items():
            k = key.upper().removeprefix("BUS")
            normalised[k] = val
        self.sends = normalised
        return self


def load_channel_config(path: str | Path) -> ChannelConfig:
    """Load and validate a channel-frame DSL YAML file."""
    raw = yaml.safe_load(Path(path).read_text())
    return ChannelConfig.model_validate(raw)
