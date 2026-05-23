############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# License APL2.0
#
###########################################################
from mw4.gui.extWindows.simulator.materials import Materials
from mw4.gui.extWindows.simulator.tools import linkModel
from PySide6.QtGui import QVector3D
from typing import Any


class SimulatorDome:
    def __init__(self, parent: Any, app: Any) -> None:
        super().__init__()
        self.parent = parent
        self.app = app
        self.app.dome.signals.deviceConnected.connect(lambda: self.showEnable(True))
        self.app.dome.signals.deviceDisconnected.connect(lambda: self.showEnable(False))
        self.app.dome.signals.azimuth.connect(self.updateAzimuth)
        self.app.update1s.connect(self.updateShutter)
        self.parent.ui.domeTransparent.checkStateChanged.connect(self.setTransparency)

    def setTransparency(self) -> None:
        showTransparent = self.parent.ui.domeTransparent.isChecked()
        alpha = 0.5 if showTransparent else 1
        for node in [
            "domeWall",
            "domeSphere",
            "domeSlit1",
            "domeSlit2",
            "domeDoor1",
            "domeDoor2",
        ]:
            nodeM = self.parent.entityModel.get(node)
            if nodeM:
                nodeM["material"].setAlpha(alpha)

    def showEnable(self, show: bool) -> None:
        node = self.parent.entityModel.get("domeRoot")
        if node:
            node["entity"].setEnabled(show)
            self.app.updateDomeSettings.connect(self.updateSize)
        else:
            self.app.updateDomeSettings.disconnect(self.updateSize)

    def updateSize(self) -> None:
        """
        updateSettings resize parts depending on the setting made in the dome tab.
        likewise some transformations have to be reverted as they are propagated
        through entity linking.
        """
        radius = self.app.mount.geometry.domeRadius * 1000
        scale = 1 + (radius - 1250) / 1250
        corrZ = -(scale - 1) * 800

        for node in ["domeFloor", "domeWall"]:
            nodeT = self.parent.entityModel[node]["trans"]
            nodeT.setScale3D(QVector3D(scale, scale, 1))

        nodeT = self.parent.entityModel["domeSphere"]["trans"]
        nodeT.setScale3D(QVector3D(scale, scale, scale))
        nodeT.setTranslation(QVector3D(0, 0, corrZ))

    def updateAzimuth(self, azimuth: float) -> None:
        node = self.parent.entityModel.get("domeSphere")
        if node:
            node["trans"].setRotationZ(-azimuth)

    def updateShutter(self) -> None:
        if "DOME_SHUTTER.SHUTTER_OPEN" not in self.app.dome.data:
            return

        isOpen = self.app.dome.data["DOME_SHUTTER.SHUTTER_OPEN"]
        radius = self.app.mount.geometry.domeRadius * 1000
        scale = 1 + (radius - 1250) / 1250
        width = self.app.dome.clearOpening * 1000
        scaleSlit = (1 + (width - 600) / 600 / 2) * 0.9
        shiftShutter = width / 2 / scale if isOpen else 0

        for nodeItem in ["domeSlit1", "domeSlit2"]:
            node = self.parent.entityModel.get(nodeItem)
            if node:
                node["trans"].setScale3D(QVector3D(1, scaleSlit, 1))

        for nodeItem in ["domeDoor1"]:
            node = self.parent.entityModel.get(nodeItem)
            if node:
                node["trans"].setTranslation(QVector3D(0, shiftShutter, 0))

        for nodeItem in ["domeDoor2"]:
            node = self.parent.entityModel.get(nodeItem)
            if node:
                node["trans"].setTranslation(QVector3D(0, -shiftShutter, 0))

    def create(self) -> None:
        model = {
            "domeRoot": {
                "parent": "ref_fusion_m",
            },
            "domeSphere": {
                "parent": "domeRoot",
                "source": "dome-sphere.stl",
                "scale": [1, 1, 1],
                "mat": Materials().domeSphere,
            },
            "domeSlit1": {
                "parent": "domeSphere",
                "source": "dome-slit1.stl",
                "scale": [1, 1, 1],
                "mat": Materials().domeSlit,
            },
            "domeSlit2": {
                "parent": "domeSphere",
                "source": "dome-slit2.stl",
                "scale": [1, 1, 1],
                "mat": Materials().domeSlit,
            },
            "domeDoor1": {
                "parent": "domeSphere",
                "source": "dome-door1.stl",
                "scale": [1, 1, 1],
                "mat": Materials().domeDoor,
            },
            "domeDoor2": {
                "parent": "domeSphere",
                "source": "dome-door2.stl",
                "scale": [1, 1, 1],
                "trans": [0, 5, 0],
                "mat": Materials().domeDoor,
            },
            "domeFloor": {
                "parent": "domeRoot",
                "source": "dome-floor.stl",
                "scale": [1, 1, 1],
                "mat": Materials().aluminiumGrey,
            },
            "domeWall": {
                "parent": "domeRoot",
                "source": "dome-wall.stl",
                "scale": [1, 1, 1],
                "mat": Materials().walls,
            },
        }
        linkModel(model, self.parent.entityModel)
        self.showEnable(self.app.deviceStat["dome"] is True)
        self.updateAzimuth(0)
        self.updateShutter()
        self.updateSize()
