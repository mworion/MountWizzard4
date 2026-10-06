# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from mw4.base.signalsDevices import Signals
from mw4.mountcontrol.firmware import Firmware
from mw4.mountcontrol.model import Model
from mw4.mountcontrol.obsSite import ObsSite
from mw4.mountcontrol.setting import Setting
from mw4.mountcontrol.tleParams import TLEParams
from mw4.mountcontrol.trajectoryParams import TrajectoryParams
from PySide6.QtCore import Signal


class MountSignals(Signals):
    pointDone = Signal(ObsSite)
    settingDone = Signal(Setting)
    getModelDone = Signal(Model)
    namesDone = Signal(Model)
    firmwareDone = Signal(Firmware)
    locationDone = Signal(ObsSite)
    calcTLEdone = Signal(TLEParams)
    statTLEdone = Signal(TLEParams)
    getTLEdone = Signal(TLEParams)
    calcTrajectoryDone = Signal(TrajectoryParams)
    mountIsUp = Signal(bool)
    slewed = Signal()
    alert = Signal()
