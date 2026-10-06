# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from mw4.base.appProtocol import AppProtocol
from mw4.gui.extWindows.simulator.materials import Materials
from mw4.gui.extWindows.simulator.tools import linkModel
from PySide6.QtGui import QVector3D
from typing import Any


class SimulatorPointer:
    def __init__(self, parent: Any, app: AppProtocol) -> None:
        super().__init__()
        self.parent = parent
        self.app = app
        self.parent.ui.showPointer.checkStateChanged.connect(self.showEnable)

    def showEnable(self) -> None:
        isVisible = self.parent.ui.showPointer.isChecked()
        node = self.parent.entityModel.get("pointerRoot")
        if node:
            node["entity"].setEnabled(isVisible)

    def updatePositions(self) -> None:
        if not self.app.dReg["mount"].stat:
            return

        mount = self.app.dReg["mount"].instance
        _, _, intersect, _, _ = mount.calcTransformationMatricesActual()

        if intersect is None:
            return

        intersect *= 1000
        intersect[2] += 1000

        node = self.parent.entityModel.get("pointerDot")
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
        linkModel(model, self.parent.entityModel)
        self.updatePositions()
        self.showEnable()
