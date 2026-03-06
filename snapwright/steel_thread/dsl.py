"""Channel-frame DSL models for the Phase 0 steel thread.

This is throwaway scaffolding. The instrument-frame DSL gets designed in Phase 1.
"""

from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, model_validator
import yaml
from pathlib import Path


SOURCE_GROUP_MAP = {
    "stage-box": "A",
    "local": "B",      # local inputs on the desk itself
    "usb": "C",        # USB/computer playback
    "off": "OFF",
}


class InputConfig(BaseModel):
    source: str = "stage-box"
    input: int = 1

    def to_wing_conn(self) -> dict:
        grp = SOURCE_GROUP_MAP.get(self.source)
        if grp is None:
            raise ValueError(f"Unknown input source: {self.source!r}. Known: {list(SOURCE_GROUP_MAP)}")
        return {"grp": grp, "in": self.input, "altgrp": "OFF", "altin": 1}


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
    sends: dict[str, SendConfig] = {}

    @model_validator(mode="after")
    def _validate_sends(self) -> ChannelConfig:
        # Normalise send keys: accept "bus1" or "1", "MX1" etc.
        normalised: dict[str, SendConfig] = {}
        for key, val in self.sends.items():
            k = key.upper().removeprefix("BUS")  # "bus1" → "1", "MX1" → "MX1"
            normalised[k] = val
        self.sends = normalised
        return self


def load_channel_config(path: str | Path) -> ChannelConfig:
    """Load and validate a channel-frame DSL YAML file."""
    raw = yaml.safe_load(Path(path).read_text())
    return ChannelConfig.model_validate(raw)
