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
# written in python3, (c) 2019-2021 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages
import numpy as np
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QVector3D
from PyQt5.Qt3DExtras import QSphereMesh
from PyQt5.Qt3DExtras import QExtrudedTextMesh, QCylinderMesh
from PyQt5.Qt3DCore import QEntity, QTransform
from skyfield import functions

# local import
from gui.extWindows.simulator.materials import Materials


class SimulatorBuildPoints:

    __all__ = ['SimulatorBuildPoints',
               ]

    def __init__(self, app):
        self.app = app
        self.points = []
        self.pointRoot = None

    @staticmethod
    def createLine(rEntity, dx, dy, dz):
        """
        create line draw a line between two point or better along dx, dy, dz. Therefore three
        transformations are made and the resulting vector has to be translated half the
        length, because is will be drawn symmetrically to the starting point.

        :param rEntity:
        :param dx:
        :param dy:
        :param dz:
        :return:
        """

        radius, alt, az = functions.to_spherical(np.array((dx, dy, dz)))
        az = np.degrees(az)
        alt = np.degrees(alt)

        e1 = QEntity(rEntity)
        trans1 = QTransform()
        trans1.setRotationZ(az + 90)
        e1.addComponent(trans1)

        e2 = QEntity(e1)
        trans2 = QTransform()
        trans2.setRotationX(-alt)
        e2.addComponent(trans2)

        e3 = QEntity(e2)
        mesh = QCylinderMesh()
        mesh.setRadius(0.008)
        mesh.setLength(radius)
        trans3 = QTransform()
        trans3.setTranslation(QVector3D(0, radius / 2, 0))
        e3.addComponent(mesh)
        e3.addComponent(trans3)
        e3.addComponent(Materials().lines)

        return e3

    @staticmethod
    def createPoint(rEntity, alt, az):
        """
        the point is located in a distance of radius meters from the ota axis and
        positioned in azimuth and altitude correctly. it's representation is a small
        small ball mesh.

        :param rEntity:
        :param alt:
        :param az:
        :return: entity, x, y, z coordinates
        """

        radius = 4
        entity = QEntity(rEntity)
        mesh = QSphereMesh()
        mesh.setRadius(0.035)
        mesh.setRings(30)
        mesh.setSlices(30)
        trans = QTransform()
        x, y, z = functions.from_spherical(radius, alt, az)
        trans.setTranslation(QVector3D(x, y, z + 1.35))
        entity.addComponent(mesh)
        entity.addComponent(trans)
        entity.addComponent(Materials().points)

        return entity, x, y, z

    @staticmethod
    def createAnnotation(rEntity, alt, az, text, faceIn=False):
        """
        the annotation - basically the number of the point - is positioned relative to the
        build point in its local coordinate system. to face the text to the viewer (azimuth),
        the text is first rotated to be upright and secondly to turn is fac according to
        the altitude of the viewer.
        it is done in two entities to simplify the rotations as they are in this case
        relative to each other.
        faceIn changes the behaviour to have the text readable from inside or outside.

        :param rEntity:
        :param alt:
        :param az:
        :param text:
        :param faceIn: direction of the text face (looking from inside or outside)
        :return: entity
        """

        e1 = QEntity(rEntity)
        trans1 = QTransform()
        if faceIn:
            trans1.setRotationZ(az - 90)
        else:
            trans1.setRotationZ(az + 90)
        e1.addComponent(trans1)

        e2 = QEntity(e1)
        mesh = QExtrudedTextMesh()
        mesh.setText(text)
        mesh.setDepth(0.05)
        mesh.setFont(QFont('Arial', 36))
        trans2 = QTransform()
        if faceIn:
            trans2.setRotationX(90 + alt)
        else:
            trans2.setRotationX(90 - alt)
        trans2.setScale(0.12)
        e2.addComponent(mesh)
        e2.addComponent(trans2)
        e2.addComponent(Materials().numbers)

        return e2

    def create(self, rEntity, show, numbers=False, path=False):
        """
        buildPointsCreate show the point in the sky if checked, in addition if selected the
        slew path between the points and in addition if checked the point numbers
        as the azimuth (second element in tuple) is turning clockwise, it's opposite to the
        right turning coordinate system (z is upwards), which means angle around z
        (which is azimuth) turns counterclockwise. so we have to set - azimuth for coordinate
        calculation

        :return: success
        """

        if self.points:
            self.pointRoot.setParent(None)

        self.points.clear()

        if not show:
            return False

        if not self.app.data.buildP:
            return False

        self.pointRoot = QEntity(rEntity)

        for index, point in enumerate(self.app.data.buildP):
            e, x, y, z = self.createPoint(self.pointRoot,
                                          np.radians(point[0]),
                                          np.radians(-point[1]))

            if numbers:
                a = self.createAnnotation(e, point[0], -point[1], f'{index:02d}')
            else:
                a = None

            if index and path:
                x0 = self.points[-1]['x']
                y0 = self.points[-1]['y']
                z0 = self.points[-1]['z']
                dx = x - x0
                dy = y - y0
                dz = z - z0
                li = self.createLine(e, dx, dy, dz)
            else:
                li = None

            element = {'e': e, 'a': a, 'li': li, 'x': x, 'y': y, 'z': z}

            self.points.append(element)

        return True
