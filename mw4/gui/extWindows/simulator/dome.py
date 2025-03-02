############################################################
# -*- coding: utf-8 -*-
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide for python
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages
from PySide6.QtGui import QVector3D

# local import
from gui.extWindows.simulator.tools import linkModel
from gui.extWindows.simulator.materials import Materials


class SimulatorDome:
    """ """

    def __init__(self, parent, app):
        super().__init__()
        self.parent = parent
        self.app = app
        self.app.dome.signals.deviceConnected.connect(lambda: self.showEnable(True))
        self.app.dome.signals.deviceDisconnected.connect(lambda: self.showEnable(False))
        self.app.updateDomeSettings.connect(self.updateSize)
        self.app.update1s.connect(self.updateAzimuth)
        self.app.update1s.connect(self.updateShutter)
        self.parent.ui.domeTransparent.checkStateChanged.connect(self.setTransparency)

    def setTransparency(self):
        """
        :return:
        """
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

    def showEnable(self, show):
        """
        :param show:
        :return:
        """
        node = self.parent.entityModel.get("domeRoot")
        if node:
            node["entity"].setEnabled(show)

    def updateSize(self):
        """
        updateSettings resize parts depending on the setting made in the dome tab.
        likewise some transformations have to be reverted as they are propagated
        through entity linking.

        :return:
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

    def updateAzimuth(self):
        """
        :return: success
        """
        if "ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION" not in self.app.dome.data:
            return

        az = self.app.dome.data["ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION"]
        node = self.parent.entityModel.get("domeSphere")
        if node:
            node["trans"].setRotationZ(-az)

    def updateShutter(self):
        """
        :return:
        """
        if "DOME_SHUTTER.SHUTTER_OPEN" not in self.app.dome.data:
            return

        isOpen = self.app.dome.data["DOME_SHUTTER.SHUTTER_OPEN"]
        radius = self.app.mount.geometry.domeRadius * 1000
        scale = 1 + (radius - 1250) / 1250
        width = self.app.dome.clearOpening * 1000
        scaleSlit = (1 + (width - 600) / 600 / 2) * 0.9
        shiftShutter = width / 2 / scale if isOpen else 0

        for node in ["domeSlit1", "domeSlit2"]:
            node = self.parent.entityModel.get(node)
            if node:
                node["trans"].setScale3D(QVector3D(1, scaleSlit, 1))

        for node in ["domeDoor1"]:
            node = self.parent.entityModel.get(node)
            if node:
                node["trans"].setTranslation(QVector3D(0, shiftShutter, 0))

        for node in ["domeDoor2"]:
            node = self.parent.entityModel.get(node)
            if node:
                node["trans"].setTranslation(QVector3D(0, -shiftShutter, 0))

    def create(self):
        """
        :return:
        """
        model = {
            "domeRoot": {
                "parent": "ref_fusion_m",
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
                "mat": Materials().domeDoor,
            },
        }
        linkModel(model, self.parent.entityModel)
        self.showEnable(self.app.deviceStat["dome"] is True)
        self.updateAzimuth()
        self.updateShutter()
        self.updateSize()
