# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from __future__ import annotations

from pathlib import Path
from PySide6.QtCore import QObject, Signal
from skyfield.api import EarthSatellite
from skyfield.timelib import Time
from skyfield.toposlib import GeographicPosition


class UiSignals(QObject):
    """Signals for messages, sound, images and general UI state."""

    msg = Signal(int, str, str, str)
    colorChange = Signal()
    playSound = Signal(str)
    showImage = Signal(Path)
    showAnalyse = Signal(Path)
    operationRunning = Signal(int)
    remoteCommand = Signal(str)


class HemisphereSignals(QObject):
    """Signals for the hemisphere display and build points."""

    redrawHemisphere = Signal()
    redrawHorizon = Signal()
    updatePointMarker = Signal()
    drawBuildPoints = Signal()
    drawHorizonPoints = Signal()
    buildPointsChanged = Signal()


class ModelSignals(QObject):
    """Signals for model data, satellites and dome settings."""

    refreshModel = Signal()
    refreshName = Signal()
    sendSatelliteData = Signal(object, object)
    updateSatellite = Signal(Time, GeographicPosition)
    showSatellite = Signal(EarthSatellite, object, object, object, str)
    updateDomeSettings = Signal()


class SystemSignals(QObject):
    """Signals for system wide mode and state changes."""

    timebaseChanged = Signal()
    onlineModeChanged = Signal()
    hidModeChanged = Signal()
    relayChanged = Signal()
    parkChanged = Signal()


class AppSignals:
    """All application signals grouped by topic. To add a signal, put it in
    the matching group class above and use it as app.signals.<group>.<name>.
    """

    def __init__(self) -> None:
        self.ui = UiSignals()
        self.hemisphere = HemisphereSignals()
        self.model = ModelSignals()
        self.system = SystemSignals()
