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
from skyfield import functions
import numpy as np

# local import
from gui.extWindows.simulator.tools import linkModel
from gui.extWindows.simulator.materials import Materials


class SimulatorLaser:
    """ """

    def __init__(self, parent, app):
        super().__init__()
        self.parent = parent
        self.app = app
        self.parent.ui.showLaser.checkStateChanged.connect(self.showEnable)

    def showEnable(self):
        """ """
        isVisible = self.parent.ui.showLaser.isChecked()
        node = self.parent.entityModel.get("laserRoot")
        if node:
            node["entity"].setEnabled(isVisible)

    def updatePositions(self):
        """ """
        if not self.app.deviceStat["mount"]:
            return

        _, _, _, PB, PD = self.app.mount.calcTransformationMatricesActual()

        if PB is None or PD is None:
            return

        PB *= 1000
        PB[2] += 1000
        radius, alt, az = functions.to_spherical(-PD)
        az = np.degrees(az)
        alt = np.degrees(alt)

        node = self.parent.entityModel.get("displacement")
        if node:
            node["trans"].setTranslation(QVector3D(PB[0], PB[1], PB[2]))

        node = self.parent.entityModel.get("az")
        if node:
            node["trans"].setRotationZ(az + 90)

        node = self.parent.entityModel.get("alt")
        if node:
            node["trans"].setRotationX(-alt)

    def create(self):
        """ """
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
        linkModel(model, self.parent.entityModel)
        self.updatePositions()
        self.showEnable()
