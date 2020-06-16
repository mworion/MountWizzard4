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
from PyQt5.QtWidgets import QWidget
from PyQt5.Qt3DExtras import Qt3DWindow
from PyQt5.Qt3DExtras import QOrbitCameraController
from PyQt5.Qt3DExtras import QSphereMesh, QCylinderMesh, QCuboidMesh
from PyQt5.Qt3DExtras import QDiffuseSpecularMaterial, QMetalRoughMaterial, QPhongAlphaMaterial
from PyQt5.Qt3DRender import QMesh, QGeometryRenderer
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

        self.transparent = QPhongAlphaMaterial()
        self.transparent.setAmbient(QColor(1, 1, 1, 1))
        self.transparent.setDiffuse(QColor(1, 1, 1, 1))
        self.transparent.setSpecular(QColor(1, 1, 1, 1))
        self.transparent.setShininess(1)
        self.transparent.setAlpha(0.2)


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
        self.camera.setViewCenter(QVector3D(0.0, 1.5, 0.0))
        # self.camera.setUpVector(QVector3D(0.0, .00, 0.0))
        self.camController = QOrbitCameraController(self.rootEntity)
        self.camController.setCamera(self.camera)
        self.camController.setLinearSpeed(5.0)
        self.camController.setLookSpeed(90)
        self.view.setRootEntity(self.rootEntity)

        self.domeColumnTrans = None
        self.domeCompassRoseTrans = None
        self.domeCompassRoseCharTrans = None
        self.latTrans = None
        self.raTrans = None
        self.decTrans = None
        self.gemTrans = None
        self.gemCorrTrans = None
        self.gemMesh = None
        self.otaRingTrans = None
        self.otaTubeTrans = None
        self.otaImagetrainTrans = None

        self.domeWallTrans = None
        self.domeFloorTrans = None
        self.domeSphereTrans = None

        self.initConfig()
        self.showWindow()

        # connect functional signals
        self.app.redrawSimulator.connect(self.updateSettings)
        self.app.mount.signals.pointDone.connect(self.updatePositions)

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

        if 'cameraPositionX' in config:
            x = config['cameraPositionX']
            y = config['cameraPositionY']
            z = config['cameraPositionZ']
            self.camera.setPosition(QVector3D(x, y, z))

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

        pos = self.camera.position()
        config['cameraPositionX'] = pos.x()
        config['cameraPositionY'] = pos.y()
        config['cameraPositionZ'] = pos.z()

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
        self.updatePositions()
        self.updateSettings()
        self.show()

        return True

    def createOTA(self, rootEntity):
        """
        first transformation is from
            fusion360 (x is north, y is west, z is up), scale in mm
            Qt3D (-z is north, x is east, y is up) scale is m
        and set as reference. from there on we are in the fusion coordinate system

        dict {'name of model': {'parent': }}

        :param rootEntity: root of the 3D models
        :return:
        """

        model = {
            'name of model': {
                'parent': self,
                'source': None,
                'trans': None,
                'rot': None,
                'scale': None,
                'mat': None,
            }
        }

        ref = QEntity(rootEntity)
        refTrans = QTransform()
        refTrans.setScale(0.001)
        refTrans.setRotationY(90)
        refTrans.setRotationX(-90)
        ref.addComponent(refTrans)

        domeColumn = QEntity(ref)
        domeColumnMesh = QMesh()
        self.domeColumnTrans = QTransform()
        domeColumnMesh.setSource(QUrl('qrc:/model3D/dome-column.stl'))
        domeColumn.addComponent(domeColumnMesh)
        domeColumn.addComponent(self.domeColumnTrans)
        domeColumn.addComponent(Materials().aluminiumS)

        domeCompassRose = QEntity(ref)
        domeCompassRoseMesh = QMesh()
        self.domeCompassRoseTrans = QTransform()
        domeCompassRoseMesh.setSource(QUrl('qrc:/model3D/dome-rose.stl'))
        domeCompassRose.addComponent(self.domeCompassRoseTrans)
        domeCompassRose.addComponent(domeCompassRoseMesh)
        domeCompassRose.addComponent(Materials().stainless)

        domeCompassRoseChar = QEntity(ref)
        domeCompassRoseCharMesh = QMesh()
        self.domeCompassRoseCharTrans = QTransform()
        domeCompassRoseCharMesh.setSource(QUrl('qrc:/model3D/dome-rose-char.stl'))
        domeCompassRoseChar.addComponent(self.domeCompassRoseCharTrans)
        domeCompassRoseChar.addComponent(domeCompassRoseCharMesh)
        domeCompassRoseChar.addComponent(Materials().aluminiumB)

        mountBase = QEntity(domeColumn)
        mountBaseMesh = QMesh()
        mountBaseMesh.setSource(QUrl('qrc:/model3D/mont-base.stl'))
        mountBaseTrans = QTransform()
        mountBaseTrans.setTranslation(QVector3D(0.0, 0.0, 1000.0))
        mountBase.addComponent(mountBaseTrans)
        mountBase.addComponent(mountBaseMesh)
        mountBase.addComponent(Materials().aluminiumR)

        mountKnobs = QEntity(mountBase)
        mountKnobsMesh = QMesh()
        mountKnobsMesh.setSource(QUrl('qrc:/model3D/mont-base-knobs.stl'))
        mountKnobs.addComponent(mountKnobsMesh)
        mountKnobs.addComponent(Materials().stainless)

        lat = QEntity(mountBase)
        self.latTrans = QTransform()
        self.latTrans.setTranslation(QVector3D(0.0, 0.0, 70.0))
        self.latTrans.setRotationY(- (90 - 48))
        lat.addComponent(self.latTrans)

        montRa = QEntity(lat)
        montRaMesh = QMesh()
        montRaMesh.setSource(QUrl('qrc:/model3D/mont-ra.stl'))
        montRaTrans = QTransform()
        montRaTrans.setTranslation(QVector3D(0.0, 0.0, -70.0))
        montRa.addComponent(montRaTrans)
        montRa.addComponent(montRaMesh)
        montRa.addComponent(Materials().aluminiumS)

        ra = QEntity(montRa)
        self.raTrans = QTransform()
        self.raTrans.setTranslation(QVector3D(0.0, 0.0, 190.0))
        ra.addComponent(self.raTrans)

        montDec = QEntity(ra)
        montDecMesh = QMesh()
        montDecMesh.setSource(QUrl('qrc:/model3D/mont-dec.stl'))
        montDecTrans = QTransform()
        montDecTrans.setTranslation(QVector3D(0.0, 0.0, -190.0))
        montDec.addComponent(montDecTrans)
        montDec.addComponent(montDecMesh)
        montDec.addComponent(Materials().aluminiumS)

        montDecWeights = QEntity(ra)
        montDecWeightsMesh = QMesh()
        montDecWeightsMesh.setSource(QUrl('qrc:/model3D/mont-dec-weights.stl'))
        montDecWeightsTrans = QTransform()
        montDecWeightsTrans.setTranslation(QVector3D(0.0, 0.0, -190.0))
        montDecWeights.addComponent(montDecWeightsTrans)
        montDecWeights.addComponent(montDecWeightsMesh)
        montDecWeights.addComponent(Materials().stainless)

        dec = QEntity(montDec)
        self.decTrans = QTransform()
        self.decTrans.setTranslation(QVector3D(159.0, 0.0, 190.0))
        dec.addComponent(self.decTrans)

        montHead = QEntity(dec)
        montHeadMesh = QMesh()
        montHeadMesh.setSource(QUrl('qrc:/model3D/mont-dec-head.stl'))
        montHeadTrans = QTransform()
        montHeadTrans.setTranslation(QVector3D(-159.0, 0.0, -190.0))
        montHead.addComponent(montHeadTrans)
        montHead.addComponent(montHeadMesh)
        montHead.addComponent(Materials().aluminiumS)

        gem = QEntity(montHead)
        self.gemMesh = QCuboidMesh()
        self.gemMesh.setXExtent(100)
        self.gemMesh.setYExtent(60)
        self.gemMesh.setZExtent(10)
        self.gemTrans = QTransform()
        self.gemTrans.setTranslation(QVector3D(159.0, 0.0, 338.5 + 5.0))
        gem.addComponent(self.gemMesh)
        gem.addComponent(self.gemTrans)
        gem.addComponent(Materials().aluminiumB)

        gemCorr = QEntity(gem)
        self.gemCorrTrans = QTransform()
        self.gemCorrTrans.setTranslation(QVector3D(0.0, 0.0, 5.0))
        gemCorr.addComponent(self.gemCorrTrans)

        otaPlate = QEntity(gemCorr)
        otaPlateMesh = QMesh()
        otaPlateMesh.setSource(QUrl('qrc:/model3D/ota-plate.stl'))
        otaPlate.addComponent(otaPlateMesh)
        otaPlate.addComponent(Materials().aluminiumS)

        otaRing = QEntity(otaPlate)
        otaRingMesh = QMesh()
        otaRingMesh.setSource(QUrl('qrc:/model3D/ota-ring-s.stl'))
        self.otaRingTrans = QTransform()
        self.otaRingTrans.setScale3D(QVector3D(1.0, 1.0, 1.0))
        otaRing.addComponent(otaRingMesh)
        otaRing.addComponent(self.otaRingTrans)
        otaRing.addComponent(Materials().aluminiumR)

        otaTube = QEntity(otaPlate)
        otaTubeMesh = QMesh()
        otaTubeMesh.setSource(QUrl('qrc:/model3D/ota-tube-s.stl'))
        self.otaTubeTrans = QTransform()
        self.otaTubeTrans.setScale3D(QVector3D(1.0, 1.0, 1.0))
        otaTube.addComponent(otaTubeMesh)
        otaTube.addComponent(self.otaTubeTrans)
        otaTube.addComponent(Materials().white)

        otaImagetrain = QEntity(gemCorr)
        otaImagetrainMesh = QMesh()
        otaImagetrainMesh.setSource(QUrl('qrc:/model3D/ota-imagetrain.stl'))
        self.otaImagetrainTrans = QTransform()
        self.otaImagetrainTrans.setScale3D(QVector3D(1.0, 1.0, 1.0))
        otaImagetrain.addComponent(otaImagetrainMesh)
        otaImagetrain.addComponent(self.otaImagetrainTrans)
        otaImagetrain.addComponent(Materials().aluminiumS)

        otaCCD = QEntity(otaImagetrain)
        otaCCDMesh = QMesh()
        otaCCDMesh.setSource(QUrl('qrc:/model3D/ota-ccd.stl'))
        otaCCD.addComponent(otaCCDMesh)
        otaCCD.addComponent(Materials().aluminiumB)

        otaFocus = QEntity(otaImagetrain)
        otaFocusMesh = QMesh()
        otaFocusMesh.setSource(QUrl('qrc:/model3D/ota-focus.stl'))
        otaFocus.addComponent(otaFocusMesh)
        otaFocus.addComponent(Materials().aluminiumR)

        otaFocusTop = QEntity(otaImagetrain)
        otaFocusTopMesh = QMesh()
        otaFocusTopMesh.setSource(QUrl('qrc:/model3D/ota-focus-top.stl'))
        otaFocusTop.addComponent(otaFocusTopMesh)
        otaFocusTop.addComponent(Materials().white)

    def createWorld(self, rootEntity):
        """

        :param rootEntity:
        :return:
        """

        ref = QEntity(rootEntity)
        refTrans = QTransform()
        refTrans.setScale(0.001)
        refTrans.setRotationY(90)
        refTrans.setRotationX(-90)
        ref.addComponent(refTrans)

        environ = QEntity(ref)
        environMesh = QMesh()
        environMesh.setSource(QUrl('qrc:/model3D/dome-environ.stl'))
        environMat = QMetalRoughMaterial()
        environMat.setBaseColor(QColor(32, 128, 32))
        environMat.setAmbientOcclusion(QColor(64, 128, 32))
        environMat.setRoughness(1000)
        environMat.setTextureScale(100)
        environ.addComponent(environMat)
        environ.addComponent(environMesh)

        domeFloor = QEntity(ref)
        domeFloorMesh = QMesh()
        domeFloorMesh.setSource(QUrl('qrc:/model3D/dome-floor.stl'))
        self.domeFloorTrans = QTransform()
        domeFloorMat = QDiffuseSpecularMaterial()
        domeFloorMat.setAmbient(QColor(32, 144, 192))
        domeFloor.addComponent(domeFloorMesh)
        domeFloor.addComponent(self.domeFloorTrans)
        domeFloor.addComponent(domeFloorMat)

        domeWall = QEntity(ref)
        domeWallMesh = QMesh()
        domeWallMesh.setSource(QUrl('qrc:/model3D/dome-wall.stl'))
        self.domeWallTrans = QTransform()
        domeWall.addComponent(domeWallMesh)
        domeWall.addComponent(self.domeWallTrans)
        domeWall.addComponent(Materials().transparent)

        domeSphere = QEntity(ref)
        domeSphereMesh = QMesh()
        domeSphereMesh.setSource(QUrl('qrc:/model3D/dome-sphere.stl'))
        self.domeSphereTrans = QTransform()
        domeSphere.addComponent(domeSphereMesh)
        domeSphere.addComponent(self.domeSphereTrans)
        domeSphere.addComponent(Materials().transparent)

    def createScene(self, rootEntity):
        """

        :param rootEntity:
        :return:
        """

        self.createWorld(rootEntity)
        self.createOTA(rootEntity)

    def updateSettings(self):
        """

        :return:
        """

        if not self.app.mount.geometry.offGemPlate:
            return False

        # ota geometry
        offPlateOTA = self.app.mount.geometry.offPlateOTA * 1000
        lat = - self.app.mainW.ui.offLAT.value() * 1000

        self.gemMesh.setYExtent(abs(lat) + 80)
        self.gemTrans.setTranslation(QVector3D(159.0, lat / 2, 338.5))
        self.gemCorrTrans.setTranslation(QVector3D(0.0, lat / 2, 0.0))

        scaleRad = (offPlateOTA - 25) / 55
        scaleRad = max(scaleRad, 1)

        self.otaRingTrans.setScale3D(QVector3D(1.0, scaleRad, scaleRad))
        self.otaRingTrans.setTranslation(QVector3D(0.0, 0.0, - 10 * scaleRad + 10))
        self.otaTubeTrans.setScale3D(QVector3D(1.0, scaleRad, scaleRad))
        self.otaTubeTrans.setTranslation(QVector3D(0.0, 0.0, - 10 * scaleRad + 10))
        self.otaImagetrainTrans.setTranslation(QVector3D(0.0, 0.0, 65 * (scaleRad - 1)))

        # location of column

        if not self.domeColumnTrans:
            return False

        north = self.app.mainW.ui.domeNorthOffset.value() * 1000
        east = self.app.mainW.ui.domeEastOffset.value() * 1000
        vertical = self.app.mainW.ui.domeVerticalOffset.value() * 1000
        self.domeColumnTrans.setTranslation(QVector3D(north, -east, vertical))
        self.domeCompassRoseTrans.setTranslation(QVector3D(north, -east, 0))
        self.domeCompassRoseCharTrans.setTranslation(QVector3D(north, -east, 0))

        if not self.domeSphereTrans:
            return False

        radius = self.app.mainW.ui.domeRadius.value() * 1000
        scale = 1 + (radius - 1250) / 1250
        corrZ = - (scale - 1) * 1000
        self.domeFloorTrans.setScale3D(QVector3D(scale, scale, 1))
        self.domeWallTrans.setScale3D(QVector3D(scale, scale, 1))
        self.domeSphereTrans.setScale3D(QVector3D(scale, scale, scale))
        self.domeSphereTrans.setTranslation(QVector3D(0, 0, corrZ))

        return True

    def updatePositions(self):
        """

        :return:
        """

        if not (self.raTrans and self.decTrans):
            return False

        angRA = self.app.mount.obsSite.angularPosRA
        angDEC = self.app.mount.obsSite.angularPosDEC

        if not (angRA and angDEC):
            return False

        self.raTrans.setRotationX(- angRA.degrees + 90)
        self.decTrans.setRotationZ(- angDEC.degrees)

        return True
