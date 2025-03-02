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

# local import
from gui.extWindows.simulator.tools import linkModel


class SimulatorLight:
    __all__ = ["SimulatorLight"]

    def __init__(self, parent, app):
        super().__init__()
        self.parent = parent
        self.app = app
        self.parent.ui.lightIntensity.valueChanged.connect(self.setIntensity)

    def setIntensity(self):
        """ """
        intensity = self.parent.ui.lightIntensity.value()
        for node in ["main", "dir", "spot"]:
            nodeL = self.parent.entityModel.get(node)
            if nodeL:
                nodeL["light"].setIntensity(intensity)

    def create(self):
        """ """
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
