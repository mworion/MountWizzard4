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
from PyQt6.QtGui import QVector3D

# local import
from gui.extWindows.simulator.materials import Materials
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
        first transformation is from fusion360 to Qt3D fusion360 (x is north,
        y is west, z is up), scale in mm Qt3D (-z is north, x is east, y is up)
        scale is m and set as reference. from there on we are in the fusion
        coordinate system

        'ref' is the fusion360 coordinate system, please be aware that rotations
        around the z axis for azimuth is clockwise and not counterclockwise as a
        right-handed coordinate system would propose.

        for the sake of simplifying there is another reference, which only has
        the corrections in coordinates and not for scaling, this is called
        'ref1000'

        beside defining the references, createWorld build the foundation for the
        positioning of a raw telescope column and a compass rose.

        :return:
        """
        model = {
            'environ': {
                'parent': 'ref',
            },
            'domeBase': {
                'parent': 'environ',
                'source': 'dome-base.stl',
                'scale': [2, 2, 1],
                'mat': Materials().environ1,
            },
            'domeColumn': {
                'parent': 'environ',
                'source': 'dome-column.stl',
                'scale': [1, 1, 1],
                'mat': Materials().aluminiumS,
            },
            'domeCompassRose': {
                'parent': 'environ',
                'source': 'dome-rose.stl',
                'scale': [1, 1, 1],
                'mat': Materials().aluminiumR,
            },
            'domeCompassRoseChar': {
                'parent': 'environ',
                'source': 'dome-rose-char.stl',
                'scale': [1, 1, 1],
                'mat': Materials().white,
            },
        }
        linkModel(model, self.parent.entityModel)
        self.updatePositions()
