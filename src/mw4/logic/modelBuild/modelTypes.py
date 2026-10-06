# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from dataclasses import dataclass, field
from enum import IntEnum
from pathlib import Path


class ModelTiming(IntEnum):
    CONSERVATIVE = 0
    NORMAL = 1
    PROGRESSIVE = 2


@dataclass(frozen=True)
class ModelRunConfig:
    imageDir: Path = field(default_factory=Path)
    numberRetries: int = 0
    retriesReverse: bool = False
    waitTimeExposure: float = 0
    modelTiming: ModelTiming = ModelTiming.CONSERVATIVE
    plateSolveApp: str = ""
