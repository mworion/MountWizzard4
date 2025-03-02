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
import numpy as np
from PySide6.QtGui import QFont
from PySide6.QtGui import QVector3D
from PySide6.Qt3DExtras import Qt3DExtras
from PySide6.Qt3DCore import Qt3DCore
from skyfield import functions

# local import
from gui.extWindows.simulator.materials import Materials


class SimulatorBuildPoints:
    """ """

    LINE_RADIUS = 0.02
    POINT_SPHERE_RADIUS = 4
    POINT_ACTIVE_RADIUS = 0.07
    POINT_RADIUS = 0.05
    FONT_SIZE = 40

    def __init__(self, parent, app):
        super().__init__()
        self.parent = parent
        self.app = app
        self.points = []
        self.parent.ui.showBuildPoints.checkStateChanged.connect(self.showEnable)
        self.parent.ui.showNumbers.checkStateChanged.connect(self.create)
        self.parent.ui.showSlewPath.checkStateChanged.connect(self.create)
        self.app.updatePointMarker.connect(self.create)
        self.app.drawBuildPoints.connect(self.create)

    def showEnable(self):
        """ """
        isVisible = self.parent.ui.showBuildPoints.isChecked()
        node = self.parent.entityModel.get("buildPoints")
        if node:
            node["entity"].setEnabled(isVisible)

    def clear(self):
        """ """
        node = self.parent.entityModel.get("buildPoints")
        if not node:
            return

        node["entity"].setParent(None)
        del self.parent.entityModel["buildPoints"]["entity"]
        del self.parent.entityModel["buildPoints"]
        self.points = []

    def updatePositions(self):
        """ """
        if not self.app.mount.obsSite.haJNow:
            return

        _, _, _, PB, PD = self.app.mount.calcTransformationMatricesActual()

        if PB is None or PD is None:
            return
        PB[2] += 1

        node = self.parent.entityModel.get("buildPoints")
        if node:
            node["trans"].setTranslation(QVector3D(PB[0], PB[1], PB[2]))

    def createLine(self, parentEntity, dx, dy, dz):
        """
        create line draw a line between two point or better along dx, dy, dz.
        Therefore, three transformations are made and the resulting vector has
        to be translated half the length, because is will be drawn symmetrically
        to the starting point.

        :param parentEntity:
        :param dx:
        :param dy:
        :param dz:
        :return:
        """
        radius, alt, az = functions.to_spherical(np.array((dx, dy, dz)))
        az = np.degrees(az)
        alt = np.degrees(alt)

        e1 = Qt3DCore.QEntity(parentEntity)
        trans1 = Qt3DCore.QTransform()
        trans1.setRotationZ(az + 90)
        e1.addComponent(trans1)

        e2 = Qt3DCore.QEntity(e1)
        trans2 = Qt3DCore.QTransform()
        trans2.setRotationX(-alt)
        e2.addComponent(trans2)

        e3 = Qt3DCore.QEntity(e2)
        mesh3 = Qt3DExtras.QCylinderMesh()
        mesh3.setRadius(self.LINE_RADIUS)
        mesh3.setLength(radius)
        trans3 = Qt3DCore.QTransform()
        trans3.setTranslation(QVector3D(0, radius / 2, 0))
        e3.addComponent(mesh3)
        e3.addComponent(trans3)
        mat3 = Materials().lines
        e3.addComponent(mat3)

        return (e1, trans1, e2, trans2, e3, trans3, mesh3, mat3)

    def createPoint(self, parentEntity, alt, az, active):
        """
        the point is located in a distance of radius meters from the ota axis
        and positioned in azimuth and altitude correctly. its representation
        is a small ball mesh.

        :param parentEntity:
        :param alt:
        :param az:
        :param active:
        :return: entity, x, y, z coordinates
        """
        entity = Qt3DCore.QEntity(parentEntity)
        mesh = Qt3DExtras.QSphereMesh()
        if active:
            mesh.setRadius(self.POINT_ACTIVE_RADIUS)
        else:
            mesh.setRadius(self.POINT_RADIUS)
        mesh.setRings(30)
        mesh.setSlices(30)
        trans = Qt3DCore.QTransform()
        x, y, z = functions.from_spherical(self.POINT_SPHERE_RADIUS, alt, az)
        trans.setTranslation(QVector3D(x, y, z))
        entity.addComponent(mesh)
        entity.addComponent(trans)
        if active:
            mat = Materials().pointsActive
        else:
            mat = Materials().points

        entity.addComponent(mat)

        return (entity, mesh, trans, mat), x, y, z

    def createAnnotation(self, parentEntity, alt, az, text, active, faceIn=False):
        """
        the annotation - basically the number of the point - is positioned
        relative to the build point in its local coordinate system. to face the
        text to the viewer (azimuth), the text is first rotated to be upright
        and secondly to turn is fac according to the altitude of the viewer.
        it is done in two entities to simplify the rotations as they are in
        this case relative to each other.
        faceIn changes the behaviour to have the text readable from inside or
        outside.

        :param parentEntity:
        :param alt:
        :param az:
        :param text:
        :param active:
        :param faceIn: direction of the text face (looking from inside or outside)
        :return: entity
        """
        e1 = Qt3DCore.QEntity(parentEntity)
        trans1 = Qt3DCore.QTransform()
        if faceIn:
            trans1.setRotationZ(az - 90)
        else:
            trans1.setRotationZ(az + 90)
        e1.addComponent(trans1)

        e3 = Qt3DCore.QEntity(e1)
        trans3 = Qt3DCore.QTransform()
        trans3.setTranslation(QVector3D(0.05, 0.0, 0.05))
        e3.addComponent(trans3)

        e2 = Qt3DCore.QEntity(e3)
        mesh2 = Qt3DExtras.QExtrudedTextMesh()
        mesh2.setText(text)
        mesh2.setDepth(0.05)
        mesh2.setFont(QFont("Arial", self.FONT_SIZE))
        trans2 = Qt3DCore.QTransform()
        if faceIn:
            trans2.setRotationX(90 + alt)
        else:
            trans2.setRotationX(90 - alt)
        trans2.setScale(0.15)
        e2.addComponent(mesh2)
        e2.addComponent(trans2)
        if active:
            mat2 = Materials().numbersActive
        else:
            mat2 = Materials().numbers
        e2.addComponent(mat2)

        return (e1, trans1, e2, trans2, mesh2, mat2, e3, trans3)

    def loopCreate(self, buildPointEntity):
        """
        :param buildPointEntity:
        :return:
        """
        isNumber = self.parent.ui.showNumbers.isChecked()
        isSlewPath = self.parent.ui.showSlewPath.isChecked()

        for index, point in enumerate(self.app.data.buildP):
            active = point[2]
            e, x, y, z = self.createPoint(
                buildPointEntity, np.radians(point[0]), np.radians(-point[1]), active
            )

            if isNumber:
                a = self.createAnnotation(
                    e[0], point[0], -point[1], f"{index + 1:02d}", active
                )
            else:
                a = None

            if index and isSlewPath:
                x0 = self.points[-1]["x"]
                y0 = self.points[-1]["y"]
                z0 = self.points[-1]["z"]
                dx = x - x0
                dy = y - y0
                dz = z - z0
                line = self.createLine(e[0], dx, dy, dz)
            else:
                line = None

            element = {"x": x, "y": y, "z": z, "a": a, "e": e, "l": line}
            self.points.append(element)

    def create(self):
        """
        buildPointsCreate show the point in the sky if checked, in addition if
        selected the slew path between the points and in addition if checked
        the point numbers as the azimuth (second element in tuple) is turning
        clockwise, it's opposite to the right turning coordinate system (z is
        upwards), which means angle around z (which is azimuth) turns
        counterclockwise. so we have to set - azimuth for coordinate calculation

        :return: success
        """
        if len(self.app.data.buildP) == 0:
            return False

        ref_fusion = self.parent.entityModel.get("ref_fusion")
        if not ref_fusion:
            return False

        self.clear()
        buildPointEntity = Qt3DCore.QEntity()
        parent = ref_fusion.get("entity")
        buildPointEntity.setParent(parent)

        buildPointTransform = Qt3DCore.QTransform()
        buildPointEntity.addComponent(buildPointTransform)
        self.parent.entityModel["buildPoints"] = {
            "entity": buildPointEntity,
            "trans": buildPointTransform,
        }

        self.loopCreate(buildPointEntity)
        self.updatePositions()
        self.showEnable()
        return True
