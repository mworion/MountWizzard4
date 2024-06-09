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
from PySide6.Qt3DRender import Qt3DRender

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
            'lightRoot': {
                'parent': 'root',
            },
            'main': {
                'parent': 'lightRoot',
                'light': ['point', 1.0, [255, 255, 255]],
                'trans': [5, 20, 5],
            },
        }
        linkModel(model, self.parent.entityModel)
        # self.app.material.emit(self.parent.entityModel['main'], 'main')

"""

            'dir': {
                'parent': 'lightRoot',
                'light': ['direction', 1, [0, 255, 0], [1, 0, 1]],
                'trans': [-10, 1, -10],
            },
            'spot': {
                'parent': 'lightRoot',
                'light': ['spot', 1, [0, 255, 255], 5, [1, 0, -1]],
                'trans': [-5, 1, 5],
            },

"""