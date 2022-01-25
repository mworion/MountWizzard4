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
import numpy as np
from PyQt5.QtGui import QVector3D
from PyQt5.Qt3DExtras import QCuboidMesh
from PyQt5.Qt3DCore import QEntity, QTransform

# local import
from gui.extWindows.simulator.materials import Materials


class SimulatorHorizon:

    __all__ = ['SimulatorHorizon',
               ]

    def __init__(self, app):
        self.app = app
        self.horizon = []
        self.horizonRoot = None

    @staticmethod
    def createWall(rEntity, alt, az, space):
        """
        createWall draw a plane in radius distance to show the horizon. spacing
        is the angular spacing between this planes

        :param rEntity:
        :param alt:
        :param az:
        :param space:
        :return: entity
        """
        radius = 4
        e1 = QEntity(rEntity)
        trans1 = QTransform()
        trans1.setRotationZ(-az)
        e1.addComponent(trans1)

        e2 = QEntity(e1)
        trans2 = QTransform()
        trans2.setTranslation(QVector3D(radius, 0, 0))
        e2.addComponent(trans2)

        e3 = QEntity(e2)
        height = radius * np.tan(np.radians(alt)) + 1.35
        mesh = QCuboidMesh()
        mesh.setXExtent(0.01)
        mesh.setYExtent(radius * np.tan(np.radians(space)))
        mesh.setZExtent(height)
        trans3 = QTransform()
        trans3.setTranslation(QVector3D(0, 0, height / 2))
        e3.addComponent(mesh)
        e3. addComponent(trans3)
        e3.addComponent(Materials().horizon)
        return e3

    def create(self, rEntity, show):
        """
        createHorizon draws a horizon "wall" by circling over the horizon points
        and putting cuboid meshed around a circle with defined radius. the space
        is the angle width of a plane in degrees

        :return: success
        """
        if self.horizon:
            self.horizonRoot.setParent(None)

        self.horizon.clear()

        if not show:
            return False

        if not self.app.data.horizonP:
            return False

        self.horizonRoot = QEntity(rEntity)

        space = 5
        horizonAz = np.linspace(0, 360 - space, int(360 / space))
        alt = [x[0] for x in self.app.data.horizonP]
        az = [x[1] for x in self.app.data.horizonP]
        horizonAlt = np.interp(horizonAz, az, alt)

        for alt, az in zip(horizonAlt, horizonAz):
            e = self.createWall(self.horizonRoot, alt, az, space)
            element = {'e': e}
            self.horizon.append(element)
        return True
