# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from mw4.mountcontrol.mountTimeConnectivity import MountTimeConnectivity
from mw4.mountcontrol.obsSite import ObsSite


class MountData:
    """Derived mount values (pointing deltas, errors, clock and round trip
    time) collected cyclically for the GUI and the measurement logging.
    """

    def __init__(self, obsSite: ObsSite, mountTimeConnectivity: MountTimeConnectivity) -> None:
        self.obsSite = obsSite
        self.mountTimeConnectivity = mountTimeConnectivity
        self.data: dict = {}
        self.raRef: float = 0.0
        self.decRef: float = 0.0

    def reset(self) -> None:
        self.raRef = self.obsSite.raJNow.degrees
        self.decRef = self.obsSite.decJNow.degrees

    def collect(self) -> None:
        if self.obsSite.statusSlew:
            self.reset()

        self.data["deltaRaJNow"] = (self.obsSite.raJNow.degrees - self.raRef) * 3600
        self.data["deltaDecJNow"] = (self.obsSite.decJNow.degrees - self.decRef) * 3600
        self.data["errorAngularPosRA"] = self.obsSite.errorAngularPosRA.degrees * 3600
        self.data["errorAngularPosDEC"] = self.obsSite.errorAngularPosDEC.degrees * 3600
        self.data["status"] = self.obsSite.status
        self.data["timeDiff"] = self.mountTimeConnectivity.timeDiff * 1000
        self.data["rtt"] = self.mountTimeConnectivity.rtt * 1000
