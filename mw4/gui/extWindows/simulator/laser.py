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
# written in python3, (c) 2019-2022 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages
from PyQt5.QtGui import QVector3D
from PyQt5.Qt3DCore import QEntity
from PyQt5.Qt3DExtras import QCylinderMesh
from skyfield import functions
import numpy as np

# local import
from gui.extWindows.simulator.materials import Materials
from gui.extWindows.simulator import tools


class SimulatorLaser:

    __all__ = ['SimulatorLaser',
               ]

    def __init__(self, app):
        super().__init__()

        self.app = app
        self.model = {}
        self.modelRoot = None

    def create(self, rEntity, show):
        """
        dict {'name of model': {'parent': }}

        :param rEntity: root of the 3D models
        :param show: root of the 3D models
        :return: success
        """
        if self.model:
            self.modelRoot.setParent(None)

        self.model.clear()
        if not show:
            return False

        self.modelRoot = QEntity(rEntity)

        self.model = {
            'ref': {
                'parent': None,
                'scale': [1, 1, 1],
            },
            'az': {
                'parent': 'ref',
                'scale': [1, 1, 1],
            },
            'alt': {
                'parent': 'az',
                'scale': [1, 1, 1],
            },
            'laser': {
                'parent': 'alt',
                'source': [QCylinderMesh(), 4500, 10, 20, 20],
                'trans': [0, 2250, 0],
                'mat': Materials().laser,
            },
        }
        for name in self.model:
            tools.linkModel(self.model, name, self.modelRoot)

        self.updatePositions()
        return True

    def updatePositions(self):
        """
        :return:
        """
        if not self.model:
            return False
        if not self.app.mount.obsSite.haJNow:
            return False

        _, _, _, PB, PD = self.app.mount.calcTransformationMatricesActual()
        PB *= 1000
        PB[2] += 1000
        radius, alt, az = functions.to_spherical(-PD)
        az = np.degrees(az)
        alt = np.degrees(alt)
        self.model['ref']['t'].setTranslation(QVector3D(PB[0], PB[1], PB[2]))
        self.model['az']['t'].setRotationZ(az + 90)
        self.model['alt']['t'].setRotationX(-alt)
        return True
