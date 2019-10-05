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
# Python  v3.7.4
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
import datetime
# external packages
import PyQt5.QtCore
import PyQt5.QtWidgets
import PyQt5.uic
# local import
from mw4.base import transform
from PyQt5.Qt3DCore import QEntity, QTransform
from PyQt5.Qt3DExtras import QTorusMesh, QPhongMaterial, \
    QSphereMesh, Qt3DWindow, \
    QOrbitCameraController
from PyQt5.QtGui import QVector3D, QQuaternion, QMatrix4x4
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QPropertyAnimation, pyqtProperty


def fuzzyCompareDouble(p1, p2):
    """
    compares 2 double as points
    """
    return abs(p1 - p2) * 100000. <= min(abs(p1), abs(p2))


class OrbitTransformController(QTransform):
    targetChanged = pyqtSignal()
    angleChanged = pyqtSignal()
    radiusChanged = pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.m_target = QTransform()
        self.m_matrix = QMatrix4x4()
        self.m_radius = 1.0
        self.m_angle = 0.0

    def target(self):
        return self.m_target

    def setTarget(self, target):
        if self.m_target == target:
            return
        self.m_target = target
        self.targetChanged.emit()

    def setRadius(self, radius):
        if fuzzyCompareDouble(radius, self.m_radius):
            return
        self.m_radius = radius
        self.radiusChanged.emit()

    def radius(self, ):
        return self.m_radius

    def setAngle(self, angle):
        if fuzzyCompareDouble(angle, self.m_angle):
            return
        self.m_angle = angle
        self.updateMatrix()
        self.angleChanged.emit()

    def angle(self):
        return self.m_angle

    def updateMatrix(self, ):
        self.m_matrix.setToIdentity()
        self.m_matrix.rotate(self.m_angle, QVector3D(0.0, 1.0, 0.0))
        self.m_matrix.translate(self.m_radius, 0.0, 0.0)
        self.m_target.setMatrix(self.m_matrix)

    # angle = pyqtProperty(float, fget=angle, fset=setAngle, notify=angleChanged)
    # radius = pyqtProperty(float, fget=radius, fset=setRadius, notify=radiusChanged)
    # target = pyqtProperty(float, fget=target, fset=setTarget, notify=angleChanged)


class View3D(PyQt5.QtCore.QObject):
    def __init__(self, parent=None):
        super().__init__()

        self.view = PyQt5.Qt3DExtras.Qt3DWindow(parent)
        self.scene = self.createScene()

        # Camera
        self.camera = self.view.camera()
        self.camera.lens().setPerspectiveProjection(45.0, 16.0 / 9.0, 0.1, 1000.0)
        self.camera.setPosition(QVector3D(0, 0, 40.0))
        self.camera.setViewCenter(QVector3D(0, 0, 0))

        # For camera controls
        self.camController = QOrbitCameraController(self.scene)
        self.camController.setLinearSpeed(50.0)
        self.camController.setLookSpeed(180.0)
        self.camController.setCamera(self.camera)

        self.view.defaultFrameGraph().setClearColor(PyQt5.QtGui.QColor(60, 250, 60))
        self.view.setRootEntity(self.scene)

    @staticmethod
    def createScene():
        # Root entity
        rootEntity = QEntity()

        # Material
        material = QPhongMaterial(rootEntity)

        # Torus
        torusEntity = QEntity(rootEntity)
        # Qt3DExtras.QTorusMesh *
        torusMesh = QTorusMesh()
        torusMesh.setRadius(5)
        torusMesh.setMinorRadius(1)
        torusMesh.setRings(100)
        torusMesh.setSlices(20)

        # Qt3DCore.QTransform *
        torusTransform = QTransform()
        torusTransform.setScale3D(QVector3D(1.5, 1, 0.5))
        torusTransform.setRotation(QQuaternion.fromAxisAndAngle(QVector3D(1, 0, 0), 45.0))

        torusEntity.addComponent(torusMesh)
        torusEntity.addComponent(torusTransform)
        torusEntity.addComponent(material)

        # Sphere
        sphereEntity = QEntity(rootEntity)
        sphereMesh = QSphereMesh()
        sphereMesh.setRadius(3)

        # Qt3DCore.QTransform *
        sphereTransform = QTransform()
        # OrbitTransformController *
        controller = OrbitTransformController(sphereTransform)
        controller.setTarget(sphereTransform)
        controller.setRadius(20.0)
        # QPropertyAnimation *
        sphereRotateTransformAnimation = QPropertyAnimation(sphereTransform)
        sphereRotateTransformAnimation.setTargetObject(controller)
        sphereRotateTransformAnimation.setPropertyName(b"angle")
        sphereRotateTransformAnimation.setStartValue(0)
        sphereRotateTransformAnimation.setEndValue(360)
        sphereRotateTransformAnimation.setDuration(10000)
        sphereRotateTransformAnimation.setLoopCount(-1)
        sphereRotateTransformAnimation.start()

        sphereEntity.addComponent(sphereMesh)
        sphereEntity.addComponent(sphereTransform)
        sphereEntity.addComponent(material)

        return rootEntity
