############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# License APL2.0
#
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
