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


class SimulatorPointer:
    """ """

    def __init__(self, parent, app):
        super().__init__()
        self.parent = parent
        self.app = app
        self.parent.ui.showPointer.checkStateChanged.connect(self.showEnable)

    def showEnable(self):
        """ """
        isVisible = self.parent.ui.showPointer.isChecked()
        node = self.parent.entityModel.get("pointerRoot")
        if node:
            node["entity"].setEnabled(isVisible)

    def updatePositions(self):
        """ """
        if not self.app.deviceStat["mount"]:
            return

        _, _, intersect, _, _ = self.app.mount.calcTransformationMatricesActual()

        if intersect is None:
            return

        intersect *= 1000
        intersect[2] += 1000

        node = self.parent.entityModel.get("pointerDot")
        if node:
            vec = QVector3D(intersect[0], intersect[1], intersect[2])
            node["trans"].setTranslation(vec)

    def create(self):
        """ """
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
