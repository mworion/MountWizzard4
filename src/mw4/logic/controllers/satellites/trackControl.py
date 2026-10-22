# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from collections.abc import Callable
from typing import Any


class SatelliteTrackController:
    """mount state transitions for satellite tracking, without any GUI dependency."""

    def __init__(self, mount: Any, dome: Any, notify: Callable[[int, str, str, str], Any]) -> None:
        self.mount = mount
        self.dome = dome
        self.notify = notify

    def start(self) -> bool:
        """unparks the mount if needed, slews to the TLE start and sets the offsets."""
        if not self.mount.stat:
            self.notify(2, "TLE", "Program", "Mount is not online")
            return False

        obsSite = self.mount.obsSite
        if obsSite.isParked:
            if obsSite.unpark():
                self.notify(0, "TLE", "Command", "Mount unparked")
            else:
                self.notify(2, "TLE", "Command error", "Cannot unpark mount")

        self.dome.instance.avoidFirstOvershoot()
        suc, message = self.mount.satellite.slewTLE()
        if not suc:
            self.notify(2, "TLE", "Command error", f"{message}")
            return False

        self.notify(0, "TLE", "Command ", f"{message}")
        self.mount.satellite.setTrackingOffsets()
        return True

    def stop(self) -> bool:
        """stops the satellite tracking by returning the mount to normal tracking."""
        if not self.mount.stat:
            self.notify(2, "TLE", "Command", "Mount is not online")
            return False

        if not self.mount.obsSite.startTracking():
            self.notify(2, "TLE", "Command", "Cannot stop tracking")
            return False

        self.notify(0, "TLE", "Command", "Stopped tracking")
        return True
