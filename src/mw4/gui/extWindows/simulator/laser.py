# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import numpy as np
from mw4.base.appProtocol import HasDevices
from mw4.gui.extWindows.simulator.materials import Materials
from mw4.gui.extWindows.simulator.tools import linkModel
from PySide6.QtCore import QObject, Slot
from PySide6.QtGui import QVector3D
from skyfield import functions
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mw4.gui.extWindows.simulator.simulatorW import SimulatorWindow


class SimulatorLaser(QObject):
    def __init__(self, parent: "SimulatorWindow", app: HasDevices) -> None:
        super().__init__(parent)
        self.parentWindow = parent
        self.app = app
        self.parentWindow.ui.showLaser.checkStateChanged.connect(self.showEnable)

    @Slot()
    def showEnable(self) -> None:
        isVisible = self.parentWindow.ui.showLaser.isChecked()
        node = self.parentWindow.entityModel.get("laserRoot")
        if node:
            node["entity"].setEnabled(isVisible)

    @Slot()
    def updatePositions(self) -> None:
        if not self.app.dReg.mount.stat:
            return

        _, _, _, PB, PD = self.app.dReg.mount.instance.calcTransformationMatricesActual()

        if PB is None or PD is None:
            return

        PB *= 1000
        PB[2] += 1000
        _radius, alt, az = functions.to_spherical(-PD)
        az = np.degrees(az)
        alt = np.degrees(alt)

        node = self.parentWindow.entityModel.get("displacement")
        if node:
            node["trans"].setTranslation(QVector3D(PB[0], PB[1], PB[2]))

        node = self.parentWindow.entityModel.get("az")
        if node:
            node["trans"].setRotationZ(az + 90)

        node = self.parentWindow.entityModel.get("alt")
        if node:
            node["trans"].setRotationX(-alt)

    def create(self) -> None:
        model = {
            "laserRoot": {
                "parent": "ref_fusion_m",
            },
            "displacement": {
                "parent": "laserRoot",
                "scale": [1, 1, 1],
            },
            "az": {
                "parent": "displacement",
                "scale": [1, 1, 1],
            },
            "alt": {
                "parent": "az",
                "scale": [1, 1, 1],
            },
            "laserBeam": {
                "parent": "alt",
                "source": ["cylinder", 4500, 10, 20, 20],
                "trans": [0, 2250, 0],
                "mat": Materials().laser,
            },
        }
        linkModel(model, self.parentWindow.entityModel)
        self.updatePositions()
        self.showEnable()
