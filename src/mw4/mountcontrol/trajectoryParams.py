# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from dataclasses import dataclass
from mw4.mountcontrol.jdParamMixin import JdParamsMixin
from mw4.mountcontrol.obsSite import ObsSite


@dataclass
class TrajectoryParams(JdParamsMixin):
    obsSite: ObsSite
    flip: bool = False
    message: str = ""
    offsetRA: float = 0
    offsetDEC: float = 0
    offsetDECcorr: float = 0
    offsetTime: float = 0
