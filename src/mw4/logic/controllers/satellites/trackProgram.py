# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import numpy as np
from collections.abc import Callable
from dataclasses import dataclass, field
from mw4.logic.controllers.satellites.trackCalculations import reduceTrajectory
from skyfield.api import Angle
from typing import Literal


@dataclass(frozen=True)
class TrajectoryResult:
    """
    result of the trajectory preparation. reason is empty on success, "noPass" if no start /
    end could be selected and "noData" if no trajectory points are left.
    """

    reason: Literal["", "noPass", "noData"] = ""
    start: float = 0
    end: float = 0
    alt: Angle = field(default_factory=lambda: Angle(degrees=0))
    az: Angle = field(default_factory=lambda: Angle(degrees=0))

    @property
    def isValid(self) -> bool:
        return not self.reason


def prepareTrajectory(
    *,
    select: Callable[[], tuple[float, float]],
    calc: Callable[[float, float], tuple[np.ndarray, np.ndarray]],
    horizon: Callable[
        [float, float, np.ndarray, np.ndarray], tuple[float, float, np.ndarray, np.ndarray]
    ],
) -> TrajectoryResult:
    """
    selects the pass, calculates the trajectory, removes the parts below the horizon and
    reduces it to the point count the mount accepts.
    """
    start, end = select()
    if not start or not end:
        return TrajectoryResult(reason="noPass")

    alt, az = calc(start, end)
    start, end, alt, az = horizon(start, end, alt, az)
    if len(alt) == 0:
        return TrajectoryResult(reason="noData")

    alt, az = reduceTrajectory(alt, az)
    return TrajectoryResult(start=start, end=end, alt=Angle(degrees=alt), az=Angle(degrees=az))
