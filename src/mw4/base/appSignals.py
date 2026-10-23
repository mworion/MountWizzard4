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
    """Signals for messages, sound, images and general UI state.

    msg:              emitted by any component (device drivers, tabs,
                      deviceRegistry, mainApp); listener: mainApp
                      (writeMessageQueue).
    colorChange:      emitted by tabSettGui; listeners: all windows and tabs
                      that restyle themselves.
    playSound:        emitted by tabSettAudio, tabAnalysis, tabModel,
                      mainWindow; listener: audioManager.
    showImage:        emitted by camera driver and imageW; listener: imageW.
    showAnalyse:      emitted by tabModel_Manage; listener: analyseW.
    operationRunning: emitted by tabModel, tabAnalysis, imageW; listeners:
                      those three, hemisphereDraw and mainApp.
    remoteCommand:    emitted by the remote driver; listener: mainWindow.
    """

    msg = Signal(int, str, str, str)
    colorChange = Signal()
    playSound = Signal(str)
    showImage = Signal(Path)
    showAnalyse = Signal(Path)
    operationRunning = Signal(int)
    remoteCommand = Signal(str)


class HemisphereSignals(QObject):
    """Signals for the hemisphere display and build points.

    redrawHemisphere:  emitted by hemisphereDraw, tabModel_BuildPoints;
                       listener: hemisphereDraw.
    redrawHorizon:     emitted by horizonDraw; listeners: hemisphereDraw,
                       horizonDraw, analyseW, satelliteHorW.
    updatePointMarker: forwarded from modelData.pointMarkersChanged (tabModel);
                       listeners: hemisphereDraw, simulator buildPoints.
    drawBuildPoints:   emitted by tabModel_BuildPoints; listener: simulator
                       buildPoints.
    buildPointsChanged: emitted by hemisphereDraw; listener:
                       tabModel_BuildPoints.
    drawHorizonPoints: currently unused (no emitter, no listener).
    """

    redrawHemisphere = Signal()
    redrawHorizon = Signal()
    updatePointMarker = Signal()
    drawBuildPoints = Signal()
    drawHorizonPoints = Signal()
    buildPointsChanged = Signal()


class ModelSignals(QObject):
    """Signals for model data, satellites and dome settings.

    refreshModel:      emitted by tabModel and mountcontrol mount; listener:
                       tabModel_Manage.
    refreshName:       emitted by mountcontrol mount; listener:
                       tabModel_Manage.
    sendSatelliteData: emitted by satelliteHorW, satelliteMapW; listener:
                       tabSat_Track.
    updateSatellite:   emitted by tabSat_Track; listeners: satelliteHorW,
                       satelliteMapW.
    showSatellite:     emitted by tabSat_Track; listeners: satelliteHorW,
                       satelliteMapW.
    updateDomeSettings: emitted by tabSettDome; listeners: simulator dome,
                       telescope, world.
    """

    refreshModel = Signal()
    refreshName = Signal()
    sendSatelliteData = Signal(object, object)
    updateSatellite = Signal(Time, GeographicPosition)
    showSatellite = Signal(EarthSatellite, object, object, object, str)
    updateDomeSettings = Signal()


class SystemSignals(QObject):
    """Signals for system wide mode and state changes.

    All are emitted by a settings tab and consumed by the working tabs.
    timebaseChanged:   tabSettUpdate -> tabAlmanac, tabEnviron_Seeing,
                       tabSat_Track.
    onlineModeChanged: tabSettUpdate -> tabSettUpdate, tabModel_BuildPoints.
    hidModeChanged:    tabSettGui -> tabMount.
    relayChanged:      tabSettRelay -> tabRelay.
    parkChanged:       tabSettPark -> tabMount_Park.
    """

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
