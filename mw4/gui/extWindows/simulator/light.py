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
# GUI with PyQT5 for python
#
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages
from PyQt6.QtGui import QColor, QVector3D
from PyQt6.Qt3DRender import QPointLight, QDirectionalLight, QSpotLight

# local import
from gui.extWindows.simulator.tools import linkModel, getLight


class SimulatorLight:

    __all__ = ['SimulatorLight']

    def __init__(self, parent, app):
        super().__init__()
        self.parent = parent
        self.app = app
        self.parent.ui.lightIntensity.valueChanged.connect(self.setIntensity)

    def setIntensity(self):
        """
        """
        intensity = self.parent.ui.lightIntensity.value()
        for light in ['main', 'dir', 'spot']:
            nodeL = getLight(self.parent.entityModel.get(light))
            if nodeL:
                nodeL.setIntensity(intensity)

    def create(self):
        """
        """
        model = {
            'lights': {
                'parent': 'root_qt3d',
            },
            'main': {
                'parent': 'lights',
                'light': [QPointLight(), 1.0, QColor(255, 0, 0)],
                'trans': [10, 40, 10],
            },
            'dir': {
                'parent': 'lights',
                'light': [QDirectionalLight(), 0.1, QColor(0, 255, 0), QVector3D(1, 0, 1)],
                'trans': [-10, 1, -10],
            },
            'spot': {
                'parent': 'lights',
                'light': [QSpotLight(), 1, QColor(0, 255, 255), 5, QVector3D(1, 0, -1)],
                'trans': [-5, 1, 5],
            },
        }
        linkModel(model, self.parent.entityModel)
