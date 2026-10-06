# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from mw4.base.appProtocol import AppProtocol
from mw4.gui.extWindows.simulator.tools import linkModel
from typing import Any


class SimulatorLight:
    def __init__(self, parent: Any, app: AppProtocol) -> None:
        super().__init__()
        self.parent = parent
        self.app = app
        self.parent.ui.lightIntensity.valueChanged.connect(self.setIntensity)

    def setIntensity(self) -> None:
        intensity = self.parent.ui.lightIntensity.value()
        for node in ["main", "dir", "spot"]:
            nodeL = self.parent.entityModel.get(node)
            if nodeL:
                nodeL["light"].setIntensity(intensity)

    def create(self) -> None:
        model = {
            "lightRoot": {
                "parent": "root",
            },
            "main": {
                "parent": "lightRoot",
                "light": ["point", 1.0, [255, 255, 255]],
                "trans": [5, 20, 5],
            },
            "direct": {
                "parent": "lightRoot",
                "light": ["direction", 0.1, [255, 255, 255], [1, 0, 1]],
                "trans": [-10, 1, -10],
            },
            "spot": {
                "parent": "lightRoot",
                "light": ["spot", 0.1, [255, 255, 255], 15, [1, 0, -1]],
                "trans": [-5, 1, 5],
            },
        }
        linkModel(model, self.parent.entityModel)
