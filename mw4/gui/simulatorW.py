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
# written in python3 , (c) 2019, 2020 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages
from PyQt5.QtCore import QSize, QUrl
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QVector3D
from PyQt5.QtGui import QQuaternion
from PyQt5.QtWidgets import QWidget
from PyQt5.Qt3DExtras import Qt3DWindow
from PyQt5.Qt3DExtras import QOrbitCameraController
from PyQt5.Qt3DExtras import QSphereMesh, QPlaneMesh, QConeMesh, QCylinderMesh
from PyQt5.Qt3DExtras import QDiffuseSpecularMaterial, QMetalRoughMaterial
from PyQt5.Qt3DRender import QGeometryRenderer, QMesh
from PyQt5.Qt3DCore import QEntity, QTransform

# local import
from mw4.gui import widget
from mw4.gui.widgets import simulator_ui


class Materials():
    def __init__(self):
        self.aluminiumS = QMetalRoughMaterial()
        self.aluminiumS.setBaseColor(QColor(127, 127, 127))
        self.aluminiumS.setMetalness(0.7)
        self.aluminiumS.setRoughness(0.1)

        self.aluminiumB = QDiffuseSpecularMaterial()
        self.aluminiumB.setAmbient(QColor(64, 64, 128))
        self.aluminiumB.setDiffuse(QColor(64, 64, 128))
        self.aluminiumB.setSpecular(QColor(192, 192, 255))

        self.aluminiumR = QDiffuseSpecularMaterial()
        self.aluminiumR.setAmbient(QColor(192, 64, 64))
        self.aluminiumR.setDiffuse(QColor(128, 64, 64))
        self.aluminiumR.setSpecular(QColor(255, 192, 192))

        self.white = QDiffuseSpecularMaterial()
        self.white.setAmbient(QColor(228, 228, 228))
        self.white.setShininess(0.7)

        self.glass = QDiffuseSpecularMaterial()
        self.glass.setAlphaBlendingEnabled(True)
        self.glass.setAmbient(QColor(0, 0, 112))
        self.glass.setDiffuse(QColor(128, 128, 192, 220))

        self.stainless = QDiffuseSpecularMaterial()
        self.stainless.setAmbient(QColor(224, 223, 219))
        self.stainless.setDiffuse(QColor(145, 148, 152))
        self.stainless.setSpecular(QColor(255, 255, 230))
        self.stainless.setShininess(0.9)


class SimulatorWindow(widget.MWidget):

    __all__ = ['SimulatorWindow',
               ]

    def __init__(self, app):
        super().__init__()

        self.app = app
        self.threadPool = app.threadPool

        self.ui = simulator_ui.Ui_SimulatorDialog()
        self.ui.setupUi(self)
        self.initUI()

        self.view = Qt3DWindow()
        self.container = QWidget.createWindowContainer(self.view)
        # adding it to window widget
        self.ui.simulator.addWidget(self.container)
        self.rootEntity = QEntity()
        self.camera = self.view.camera()
        self.camera.lens().setPerspectiveProjection(45.0, 16.0 / 9.0, 0.1, 1000.0)
        self.camera.setPosition(QVector3D(2, 3, 2))
        self.camera.setViewCenter(QVector3D(0.0, 0.0, 0.0))
        self.camController = QOrbitCameraController(self.rootEntity)
        self.camController.setCamera(self.camera)
        self.view.setRootEntity(self.rootEntity)

        self.tubeTrans = None
        self.mountTrans = None
        self.domeMesh = None

        self.initConfig()
        self.showWindow()

        self.app.update1s.connect(self.updateGeometry)

    def initConfig(self):
        """
        initConfig read the key out of the configuration dict and stores it to the gui
        elements. if some initialisations have to be proceeded with the loaded persistent
        data, they will be launched as well in this method.

        :return: True for test purpose
        """

        if 'simulatorW' not in self.app.config:
            self.app.config['simulatorW'] = {}
        config = self.app.config['simulatorW']
        x = config.get('winPosX', 100)
        y = config.get('winPosY', 100)
        if x > self.screenSizeX:
            x = 0
        if y > self.screenSizeY:
            y = 0
        self.move(x, y)
        height = config.get('height', 600)
        width = config.get('width', 800)
        self.resize(width, height)

        return True

    def storeConfig(self):
        """
        storeConfig writes the keys to the configuration dict and stores. if some
        saving has to be proceeded to persistent data, they will be launched as
        well in this method.

        :return: True for test purpose
        """
        if 'simulatorW' not in self.app.config:
            self.app.config['simulatorW'] = {}
        config = self.app.config['simulatorW']
        config['winPosX'] = self.pos().x()
        config['winPosY'] = self.pos().y()
        config['height'] = self.height()
        config['width'] = self.width()

        return True

    def closeEvent(self, closeEvent):
        """
        closeEvent is overloaded to be able to store the data before the windows is close
        and all it's data is garbage collected

        :param closeEvent:
        :return:
        """
        self.storeConfig()

        # gui signals
        super().closeEvent(closeEvent)

    def showWindow(self):
        """
        showWindow starts constructing the main window for satellite view and shows the
        window content

        :return: True for test purpose
        """

        # background color
        self.view.defaultFrameGraph().setClearColor(QColor(20, 20, 20))
        self.createScene(self.rootEntity)
        self.show()

        return True

    def createOTA(self, rootEntity):
        """

        :param rootEntity:
        :return:
        """

        mount = QEntity(rootEntity)
        self.mountTrans = QTransform()
        self.mountTrans.setTranslation(QVector3D(0, 1, 0))
        self.mountTrans.setRotationX(-60)
        mount.addComponent(self.mountTrans)

        f1 = QEntity(mount)
        f1Mesh = QMesh()
        f1Mesh.setSource(QUrl('qrc:/model3D/test1.stl'))
        f1Trans = QTransform()
        f1Trans.setScale(0.001)
        f1.addComponent(f1Trans)
        f1.addComponent(f1Mesh)
        f1.addComponent(Materials().aluminiumS)

        f2 = QEntity(mount)
        f2Mesh = QMesh()
        f2Mesh.setSource(QUrl('qrc:/model3D/test2.stl'))
        f2Trans = QTransform()
        f2Trans.setScale(0.001)
        f2.addComponent(f2Trans)
        f2.addComponent(f2Mesh)
        f2.addComponent(Materials().white)

        f3 = QEntity(mount)
        f3Mesh = QMesh()
        f3Mesh.setSource(QUrl('qrc:/model3D/test3.stl'))
        f3Trans = QTransform()
        f3Trans.setScale(0.001)
        f3.addComponent(f3Trans)
        f3.addComponent(f3Mesh)
        f3.addComponent(Materials().aluminiumB)

        f4 = QEntity(mount)
        f4Mesh = QMesh()
        f4Mesh.setSource(QUrl('qrc:/model3D/test4.stl'))
        f4Trans = QTransform()
        f4Trans.setScale(0.001)
        f4.addComponent(f4Trans)
        f4.addComponent(f4Mesh)
        f4.addComponent(Materials().aluminiumR)

    def createWorld(self, rootEntity):
        """

        :param rootEntity:
        :return:
        """

        floor = QEntity(rootEntity)
        floorMesh = QPlaneMesh()
        floorMesh.setWidth(20)
        floorMesh.setHeight(20)
        floorTrans = QTransform()
        floorTrans.setTranslation(QVector3D(0.0, 0.0, -1.0))
        floorMat = QDiffuseSpecularMaterial()
        floorMat.setAmbient(QColor(0, 64, 0))
        floor.addComponent(floorTrans)
        floor.addComponent(floorMat)
        floor.addComponent(floorMesh)

        dome = QEntity(rootEntity)
        self.domeMesh = QSphereMesh()
        self.domeMesh.setRadius(1.5)
        self.domeMesh.setPrimitiveType(QGeometryRenderer.Lines)
        self.domeMesh.setRings(18)
        self.domeMesh.setSlices(24)
        domeTrans = QTransform()
        domeTrans.setTranslation(QVector3D(0, 0, 0.0))
        domeMat = QDiffuseSpecularMaterial()
        domeMat.setAmbient(self.COLOR_3D)
        dome.addComponent(self.domeMesh)
        dome.addComponent(domeMat)

    def createScene(self, rootEntity):
        """

        :param rootEntity:
        :return:
        """

        self.createWorld(rootEntity)
        self.createOTA(rootEntity)

    def updateGeometry(self):
        """

        :return:
        """

        if self.mountTrans:
            north = self.app.mainW.ui.domeNorthOffset.value()
            east = self.app.mainW.ui.domeEastOffset.value()
            vertical = self.app.mainW.ui.domeVerticalOffset.value()
            self.mountTrans.setTranslation(QVector3D(east, vertical, -north))

        if self.tubeTrans:
            angRA = self.app.mount.obsSite.angularPosRA
            angDEC = self.app.mount.obsSite.angularPosDEC
            if angRA and angDEC:
                # self.tubeTrans.setRotationY(angRA.degrees)
                self.tubeTrans.setRotationZ(- angDEC.degrees)

        if self.domeMesh:
            radius = self.app.mainW.ui.domeRadius.value()
            self.domeMesh.setRadius(radius)

