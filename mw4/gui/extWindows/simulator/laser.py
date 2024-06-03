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
from PySide6.Qt3DExtras import Qt3DExtras
from skyfield import functions
import numpy as np

# local import
from gui.extWindows.simulator.tools import linkModel, getTransformation


class SimulatorLaser:

    __all__ = ['SimulatorLaser']

    def __init__(self, parent, app):
        super().__init__()
        self.parent = parent
        self.app = app
        self.app.mount.signals.pointDone.connect(self.updatePositions)
        self.parent.ui.showLaser.checkStateChanged.connect(self.showEnable)

    def showEnable(self):
        """
        """
        isVisible = self.parent.ui.showLaser.isChecked()
        entity = self.parent.entityModel.get('laser')
        if entity:
            entity.setEnabled(isVisible)

    def updatePositions(self):
        """
        """
        _, _, _, PB, PD = self.app.mount.calcTransformationMatricesActual()

        if PB is None or PD is None:
            return False

        PB *= 1000
        PB[2] += 1000
        radius, alt, az = functions.to_spherical(-PD)
        az = np.degrees(az)
        alt = np.degrees(alt)

        nodeT = getTransformation(self.parent.entityModel.get('displacement'))
        if nodeT:
            nodeT.setTranslation(QVector3D(PB[0], PB[1], PB[2]))

        nodeT = getTransformation(self.parent.entityModel.get('az'))
        if nodeT:
            nodeT.setRotationZ(az + 90)

        nodeT = getTransformation(self.parent.entityModel.get('alt'))
        if nodeT:
            nodeT.setRotationX(-alt)

        return True

    def create(self):
        """
        """
        model = {
            'laser': {
                'parent': 'ref_fusion_m',
            },
            'displacement': {
                'parent': 'laser',
                'scale': [1, 1, 1],
            },
            'az': {
                'parent': 'displacement',
                'scale': [1, 1, 1],
            },
            'alt': {
                'parent': 'az',
                'scale': [1, 1, 1],
            },
            'laserBeam': {
                'parent': 'alt',
                'source': [Qt3DExtras.QCylinderMesh(), 4500, 10, 20, 20],
                'trans': [0, 2250, 0],
                'mat': self.parent.materials.laser,
            },
        }
        linkModel(model, self.parent.entityModel)
        self.updatePositions()
        self.showEnable()
