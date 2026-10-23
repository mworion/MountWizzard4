# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from mw4.mountcontrol.setting import Setting


def activeTrackingMode(status: int | None, isFollowingSatellite: bool, sett: Setting) -> str | None:
    """Names the button of the active tracking mode, None if the mount state is unknown."""
    if status is None:
        return None
    if isFollowingSatellite:
        return "followSat"
    if sett.checkRateLunar():
        return "setLunarTracking"
    if sett.checkRateSidereal():
        return "setSiderealTracking"
    if sett.checkRateSolar():
        return "setSolarTracking"
    return "unchanged"
