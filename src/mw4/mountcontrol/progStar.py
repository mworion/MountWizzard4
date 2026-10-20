# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import logging
from mw4.mountcontrol.convert import validatePierside
from skyfield.api import Angle, Star


class ProgStar:
    log = logging.getLogger("MW4")

    def __init__(self, mCoord: Star, sCoord: Star, sidereal: Angle, pierside: str) -> None:
        self.mCoord: Star = mCoord
        self.sCoord: Star = sCoord
        self.sidereal: Angle = sidereal
        self._pierside: str = "E"
        self.pierside = pierside

    @property
    def pierside(self) -> str:
        return self._pierside

    @pierside.setter
    def pierside(self, value: str) -> None:
        pierside = validatePierside(value)
        if pierside is None:
            self._pierside = "E"
            self.log.warning("Malformed value: %s", value)
        else:
            self._pierside = pierside
