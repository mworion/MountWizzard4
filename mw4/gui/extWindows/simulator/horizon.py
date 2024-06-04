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
import numpy as np
from PySide6.QtGui import QVector3D
from PySide6.Qt3DExtras import Qt3DExtras
from PySide6.Qt3DCore import Qt3DCore

# local imports


class SimulatorHorizon:

    __all__ = ['SimulatorHorizon']
    WALL_RADIUS = 4
    WALL_SPACE = 5

    def __init__(self, parent, app):
        super().__init__()
        self.parent = parent
        self.app = app
        self.parent.ui.showHorizon.checkStateChanged.connect(self.showEnable)

    def showEnable(self):
        """
        """
        isVisible = self.parent.ui.showHorizon.isChecked()
        entity = self.parent.entityModel.get('horizon')
        if entity:
            entity.setEnabled(isVisible)

    def clear(self):
        """
        """
        horizonEntity = self.parent.entityModel.get('horizon')
        if horizonEntity is None:
            return False
        horizonEntity.setParent(None)
        del self.parent.entityModel['horizon']
        del horizonEntity
        return True

    def createWall(self, parentEntity, alt, az):
        """
        createWall draw a plane in radius distance to show the horizon. spacing
        is the angular spacing between this planes

        :param parentEntity:
        :param alt:
        :param az:
        :return: entity
        """
        e1 = Qt3DCore.QEntity()
        e1.setParent(parentEntity)
        trans1 = Qt3DCore.QTransform()
        trans1.setRotationZ(-az)
        e1.addComponent(trans1)

        e2 = Qt3DCore.QEntity()
        e2.setParent(e1)
        trans2 = Qt3DCore.QTransform()
        trans2.setTranslation(QVector3D(self.WALL_RADIUS, 0, 0))
        e2.addComponent(trans2)

        e3 = Qt3DCore.QEntity()
        e3.setParent(e2)
        height = self.WALL_RADIUS * np.tan(np.radians(alt)) + 1.35
        mesh = Qt3DExtras.QCuboidMesh()
        mesh.setXExtent(0.01)
        mesh.setYExtent(self.WALL_RADIUS * np.tan(np.radians(self.WALL_SPACE)))
        mesh.setZExtent(height)
        e3.addComponent(mesh)
        trans3 = Qt3DCore.QTransform()
        trans3.setTranslation(QVector3D(0, 0, height / 2))
        e3.addComponent(trans3)
        e3.addComponent(self.parent.materials.horizon)
        return e3

    def create(self):
        """
        createHorizon draws a horizon "wall" by circling over the horizon points
        and putting cuboid meshed around a circle with defined radius. the space
        is the angle width of a plane in degrees
        """
        if not self.app.data.horizonP:
            return False

        horizonAz = np.linspace(0, 360 - self.WALL_SPACE, int(360 / self.WALL_SPACE))
        alt = [x[0] for x in self.app.data.horizonP]
        az = [x[1] for x in self.app.data.horizonP]
        horizonAlt = np.interp(horizonAz, az, alt)

        self.clear()
        horizonEntity = Qt3DCore.QEntity()
        parent = self.parent.entityModel['ref_fusion']
        horizonEntity.setParent(parent)
        self.parent.entityModel['horizon'] = horizonEntity

        for alt, az in zip(horizonAlt, horizonAz):
            # self.createWall(horizonEntity, alt, az)
            pass
        self.showEnable()
        return True
