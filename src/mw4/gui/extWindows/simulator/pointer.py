# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from mw4.base.appProtocol import HasDevices
from mw4.gui.extWindows.simulator.materials import Materials
from mw4.gui.extWindows.simulator.tools import linkModel
from PySide6.QtCore import QObject, Slot
from PySide6.QtGui import QVector3D
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mw4.gui.extWindows.simulator.simulatorW import SimulatorWindow


class SimulatorPointer(QObject):
    def __init__(self, parent: "SimulatorWindow", app: HasDevices) -> None:
        super().__init__(parent)
        self.parentWindow = parent
        self.app = app
        self.parentWindow.ui.showPointer.checkStateChanged.connect(self.showEnable)

    @Slot()
    def showEnable(self) -> None:
        isVisible = self.parentWindow.ui.showPointer.isChecked()
        node = self.parentWindow.entityModel.get("pointerRoot")
        if node:
            node["entity"].setEnabled(isVisible)

    @Slot()
    def updatePositions(self) -> None:
        if not self.app.dReg.mount.stat:
            return

        mount = self.app.dReg.mount.instance
        _, _, intersect, _, _ = mount.calcTransformationMatricesActual()

        if intersect is None:
            return

        intersect *= 1000
        intersect[2] += 1000

        node = self.parentWindow.entityModel.get("pointerDot")
        if node:
            vec = QVector3D(intersect[0], intersect[1], intersect[2])
            node["trans"].setTranslation(vec)

    def create(self) -> None:
        model = {
            "pointerRoot": {
                "parent": "ref_fusion_m",
            },
            "pointerDot": {
                "parent": "pointerRoot",
                "source": ["sphere", 50, 30, 30],
                "scale": [1, 1, 1],
                "mat": Materials().pointer,
            },
        }
        linkModel(model, self.parentWindow.entityModel)
        self.updatePositions()
        self.showEnable()
