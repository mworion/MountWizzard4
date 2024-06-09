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
from PySide6.QtGui import QVector3D

# local import
from gui.extWindows.simulator.tools import linkModel, getTransformation


class SimulatorWorld:

    __all__ = ['SimulatorWorld']

    def __init__(self, parent, app):
        super().__init__()
        self.parent = parent
        self.app = app
        self.app.updateDomeSettings.connect(self.updatePositions)

    def updatePositions(self):
        """
        :return:
        """
        north = self.app.mount.geometry.offNorth * 1000
        east = self.app.mount.geometry.offEast * 1000
        vertical = self.app.mount.geometry.offVert * 1000
        scale = (960 + vertical) / 960

        translation = QVector3D(north, -east, 0)

        for node in ['domeColumn', 'domeCompassRose', 'domeCompassRoseChar']:
            nodeT = getTransformation(self.parent.entityModel.get(node))
            if nodeT:
                nodeT.setTranslation(translation)

        nodeT = getTransformation(self.parent.entityModel.get('domeColumn'))
        if nodeT:
            nodeT.setScale3D(QVector3D(1, 1, scale))

    def create(self):
        """
        """
        model = {
            'environRoot': {
                'parent': 'ref_fusion_m',
            },
            'ground': {
                'parent': 'environRoot',
                'source': 'dome-base.stl',
#                'mat': self.parent.materials.environ1,
            },
            'domeColumn': {
                'parent': 'environRoot',
                'source': 'dome-column.stl',
#                'mat': self.parent.materials.domeColumn,
            },
            'domeCompassRose': {
                'parent': 'environRoot',
                'source': 'dome-rose.stl',
#                'mat': self.parent.materials.aluRed,
            },
            'domeCompassRoseChar': {
                'parent': 'environRoot',
                'source': 'dome-rose-char.stl',
#                'mat': self.parent.materials.white,
            },
        }
        linkModel(model, self.parent.entityModel)
        self.updatePositions()
