# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from mw4.base.appProtocol import AppProtocol
from mw4.gui.extWindows.simulator.materials import Materials
from mw4.gui.extWindows.simulator.tools import linkModel
from PySide6.QtGui import QVector3D
from typing import Any


class SimulatorWorld:
    def __init__(self, parent: Any, app: AppProtocol) -> None:
        super().__init__()
        self.parent = parent
        self.app = app
        self.app.updateDomeSettings.connect(self.updatePositions)

    def updatePositions(self) -> None:
        """
        :return:
        """
        north = self.app.dReg["mount"].geometry.offNorth * 1000
        east = self.app.dReg["mount"].geometry.offEast * 1000
        vertical = self.app.dReg["mount"].geometry.offVert * 1000
        scale = (960 + vertical) / 960

        translation = QVector3D(north, -east, 0)
        for nodeItem in ["domeColumn", "domeCompassRose", "domeCompassRoseChar"]:
            node = self.parent.entityModel.get(nodeItem)
            if node:
                node["trans"].setTranslation(translation)

        node = self.parent.entityModel.get("domeColumn")
        if node:
            node["trans"].setScale3D(QVector3D(1, 1, scale))

    def create(self) -> None:
        model = {
            "environRoot": {
                "parent": "ref_fusion_m",
            },
            "ground": {
                "parent": "environRoot",
                "source": "dome-base.stl",
                "scale": [1, 1, 1],
                "mat": Materials().environ,
            },
            "domeColumn": {
                "parent": "environRoot",
                "source": "dome-column.stl",
                "scale": [1, 1, 1],
                "mat": Materials().domeColumn,
            },
            "domeCompassRose": {
                "parent": "environRoot",
                "source": "dome-rose.stl",
                "scale": [1, 1, 1],
                "mat": Materials().aluRed,
            },
            "domeCompassRoseChar": {
                "parent": "environRoot",
                "source": "dome-rose-char.stl",
                "scale": [1, 1, 1],
                "mat": Materials().white,
            },
        }
        linkModel(model, self.parent.entityModel)
        self.updatePositions()
