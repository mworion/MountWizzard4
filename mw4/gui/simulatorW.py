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
import numpy as np
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtGui import QVector3D
from PyQt5.QtWidgets import QWidget
from PyQt5.Qt3DExtras import Qt3DWindow, QCuboidMesh, QSphereMesh
from PyQt5.Qt3DExtras import QOrbitCameraController, QExtrudedTextMesh
from PyQt5.Qt3DExtras import QDiffuseSpecularMaterial, QMetalRoughMaterial
from PyQt5.Qt3DExtras import QPhongAlphaMaterial, QPhongMaterial
from PyQt5.Qt3DRender import QMesh, QPointLight, QEnvironmentLight, QDirectionalLight
from PyQt5.Qt3DCore import QEntity, QTransform

# local import
from mw4.base import transform
from mw4.gui import widget
from mw4.gui.widgets import simulator_ui


class Materials():
    def __init__(self):
        self.aluminiumS = QMetalRoughMaterial()
        self.aluminiumS.setBaseColor(QColor(127, 127, 127))
        self.aluminiumS.setMetalness(0.7)
        self.aluminiumS.setRoughness(0.5)

        self.aluminiumGrey = QMetalRoughMaterial()
        self.aluminiumGrey.setBaseColor(QColor(164, 164, 192))
        self.aluminiumGrey.setMetalness(0.3)
        self.aluminiumGrey.setRoughness(0.5)

        self.aluminiumB = QDiffuseSpecularMaterial()
        self.aluminiumB.setAmbient(QColor(64, 64, 128))
        self.aluminiumB.setDiffuse(QColor(64, 64, 128))
        # self.aluminiumB.setSpecular(QColor(192, 192, 255))

        self.aluminiumR = QDiffuseSpecularMaterial()
        self.aluminiumR.setAmbient(QColor(192, 64, 64))
        self.aluminiumR.setDiffuse(QColor(128, 64, 64))
        # self.aluminiumR.setSpecular(QColor(255, 192, 192))

        self.aluminiumG = QDiffuseSpecularMaterial()
        self.aluminiumG.setAmbient(QColor(64, 192, 64))
        self.aluminiumG.setDiffuse(QColor(64, 128, 64))
        # self.aluminiumG.setSpecular(QColor(192, 255, 192))

        self.aluminium = QDiffuseSpecularMaterial()
        self.aluminium.setAmbient(QColor(164, 164, 164))
        self.aluminium.setDiffuse(QColor(164, 164, 164))
        # self.aluminiumG.setSpecular(QColor(192, 255, 192))

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

        self.dome1 = QPhongMaterial()
        self.dome1.setAmbient(QColor(164, 164, 192))
        self.dome1.setDiffuse(QColor(164, 164, 192))
        self.dome1.setSpecular(QColor(164, 164, 192))
        self.dome1.setShininess(0.5)

        self.dome2 = QPhongMaterial()
        self.dome2.setAmbient(QColor(128, 128, 192))
        self.dome2.setDiffuse(QColor(128, 128, 192))
        self.dome2.setSpecular(QColor(128, 128, 192))
        self.dome2.setShininess(0.7)

        self.transparent = QPhongAlphaMaterial()
        self.transparent.setAmbient(QColor(16, 16, 16))
        self.transparent.setDiffuse(QColor(16, 16, 16, 255))
        self.transparent.setSpecular(QColor(16, 16, 16))
        self.transparent.setShininess(0.8)
        self.transparent.setAlpha(0.8)

        self.points = QPhongAlphaMaterial()
        self.points.setAmbient(QColor(128, 128, 16))
        self.points.setDiffuse(QColor(128, 128, 16, 255))
        self.points.setSpecular(QColor(128, 128, 16))
        self.points.setShininess(0.8)
        self.points.setAlpha(0.8)


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
        self.camera.setPosition(QVector3D(5.0, 15.0, 3.0))
        self.camera.setUpVector(QVector3D(0.0, 1.0, 0.0))
        self.camController = QOrbitCameraController(self.rootEntity)
        self.camController.setCamera(self.camera)
        self.camController.setLinearSpeed(5.0)
        self.camController.setLookSpeed(90)
        self.view.setRootEntity(self.rootEntity)
        self.view.defaultFrameGraph().setClearColor(QColor(40, 40, 40))

        self.pL0E = QEntity(self.rootEntity)
        self.pL0 = QPointLight(self.pL0E)
        self.pL0.setIntensity(0.8)
        self.pL0ETransform = QTransform()
        self.pL0ETransform.setTranslation(QVector3D(3, 20, 3))
        self.pL0E.addComponent(self.pL0)
        self.pL0E.addComponent(self.pL0ETransform)

        self.pL1E = QEntity(self.rootEntity)
        self.pL1 = QPointLight(self.pL1E)
        self.pL1.setIntensity(0.5)
        self.pL1ETransform = QTransform()
        self.pL1ETransform.setTranslation(QVector3D(-5, 20, -5))
        self.pL1E.addComponent(self.pL1)
        self.pL1E.addComponent(self.pL1ETransform)

        self.model = None
        self.world = None
        self.points = []
        self.pointRoot = None

        self.initConfig()
        self.showWindow()

        # connect to gui
        self.ui.checkDomeTransparent.clicked.connect(self.updateSettings)
        self.ui.topView.clicked.connect(self.topView)
        self.ui.topEastView.clicked.connect(self.topEastView)
        self.ui.topWestView.clicked.connect(self.topWestView)
        self.ui.eastView.clicked.connect(self.eastView)
        self.ui.westView.clicked.connect(self.westView)
        self.ui.checkPL.clicked.connect(self.setPL)

        # connect functional signals
        self.app.update1s.connect(self.updateDome)
        self.app.redrawSimulator.connect(self.updateSettings)
        self.app.sendBuildPoints.connect(self.createBuildPoints)
        self.app.mount.signals.pointDone.connect(self.updateMount)

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
            self.camera.setUpVector(QVector3D(0.0, 1.0, 0.0))

        self.ui.checkDomeTransparent.setChecked(config.get('checkDomeTransparent', False))
        self.ui.checkDomeDisable.setChecked(config.get('checkDomeDisable', False))
        self.ui.checkShowPointer.setChecked(config.get('checkShowPointer', False))

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

        config['checkDomeTransparent'] = self.ui.checkDomeTransparent.isChecked()
        config['checkDomeDisable'] = self.ui.checkDomeDisable.isChecked()
        config['checkShowPointer'] = self.ui.checkShowPointer.isChecked()

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

        self.createScene(self.rootEntity)
        self.setPL()
        self.setDomeTransparency()
        self.show()

        return True

    def setPL(self):

        self.pL0E.setEnabled(self.ui.checkPL.isChecked())
        self.pL1E.setEnabled(not self.ui.checkPL.isChecked())

    def topView(self):
        """

        :return: True for test purpose
        """

        self.camera.setViewCenter(QVector3D(0.0, 1.5, 0.0))
        self.camera.setPosition(QVector3D(0.0, 10.0, 0.0))

        return True

    def topEastView(self):
        """

        :return: True for test purpose
        """

        self.camera.setViewCenter(QVector3D(0.0, 1.5, 0.0))
        self.camera.setPosition(QVector3D(5.0, 5.0, 0.0))
        self.camera.setUpVector(QVector3D(0.0, 1.0, 0.0))

        return True

    def topWestView(self):
        """

        :return: True for test purpose
        """

        self.camera.setViewCenter(QVector3D(0.0, 1.5, 0.0))
        self.camera.setPosition(QVector3D(-5.0, 5.0, 0.0))
        self.camera.setUpVector(QVector3D(0.0, 1.0, 0.0))

        return True

    def eastView(self):
        """

        :return: True for test purpose
        """

        self.camera.setViewCenter(QVector3D(0.0, 1.5, 0.0))
        self.camera.setPosition(QVector3D(5.0, 1.5, 0.0))
        self.camera.setUpVector(QVector3D(0.0, 1.0, 0.0))

        return True

    def westView(self):
        """

        :return: True for test purpose
        """

        self.camera.setViewCenter(QVector3D(0.0, 1.5, 0.0))
        self.camera.setPosition(QVector3D(-5.0, 1.5, 0.0))
        self.camera.setUpVector(QVector3D(0.0, 1.0, 0.0))

        return True

    @staticmethod
    def linkModel(model, name, rootEntity):
        """

        :param model:
        :param name:
        :param rootEntity:
        :return:
        """

        currMod = model[name]

        parent = currMod.get('parent', None)
        if parent and model.get(parent, None):
            currMod['e'] = QEntity(model[parent]['e'])
        else:
            currMod['e'] = QEntity(rootEntity)

        source = currMod.get('source', None)
        if source:
            if isinstance(source, str):
                mesh = QMesh()
                mesh.setSource(QUrl(f'qrc:/model3D/{source}'))
            elif isinstance(source[0], QCuboidMesh):
                mesh = source[0]
                mesh.setXExtent(source[1])
                mesh.setYExtent(source[2])
                mesh.setZExtent(source[3])
            elif isinstance(source[0], QSphereMesh):
                mesh = source[0]
                mesh.setRadius(source[1])
                mesh.setRings(source[2])
                mesh.setSlices(source[3])
            elif isinstance(source[0], QExtrudedTextMesh):
                mesh = source[0]
                mesh.setDepth(source[1])
                mesh.setFont(QFont())
                mesh.setText(source[3])

            currMod['e'].addComponent(mesh)
            currMod['m'] = mesh

        trans = currMod.get('trans', None)
        rot = currMod.get('rot', None)
        scale = currMod.get('scale', None)
        if trans or rot or scale:
            transform = QTransform()

            if trans and isinstance(trans, list) and len(trans) == 3:
                transform.setTranslation(QVector3D(*trans))

            if rot and isinstance(rot, list) and len(rot) == 3:
                transform.setRotationX(rot[0])
                transform.setRotationY(rot[1])
                transform.setRotationZ(rot[2])

            if scale and isinstance(scale, list) and len(scale) == 3:
                transform.setScale3D(QVector3D(*scale))

            currMod['e'].addComponent(transform)
            currMod['t'] = transform

        mat = currMod.get('mat', None)
        if mat:
            currMod['mat'] = mat
            currMod['e'].addComponent(mat)

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

        self.model = {
            'ref': {
                'parent': None,
                'source': None,
                'trans': None,
                'rot': [-90, 90, 0],
                'scale': [0.001, 0.001, 0.001],
                'mat': None,
            },
            'domeColumn': {
                'parent': 'ref',
                'source': 'dome-column.stl',
                'scale': [1, 1, 1],
                'mat': Materials().aluminiumS,
            },
            'domeCompassRose': {
                'parent': 'ref',
                'source': 'dome-rose.stl',
                'scale': [1, 1, 1],
                'mat': Materials().aluminiumR,
            },
            'domeCompassRoseChar': {
                'parent': 'ref',
                'source': 'dome-rose-char.stl',
                'scale': [1, 1, 1],
                'mat': Materials().white,
            },
            'mountBase': {
                'parent': 'ref',
                'source': 'mont-base.stl',
                'trans': [0, 0, 1000],
                'mat': Materials().aluminiumS,
            },
            'pointer': {
                'parent': 'ref',
                'source': [QSphereMesh(), 50, 30, 30],
                'scale': [1, 1, 1],
                'mat': Materials().aluminiumB,
            },
            'mountKnobs': {
                'parent': 'mountBase',
                'source': 'mont-base-knobs.stl',
                'mat': Materials().aluminium,
            },
            'lat': {
                'parent': 'mountBase',
                'trans': [0, 0, 70],
                'rot': [0, -90 + 48, 0],
            },
            'montRa': {
                'parent': 'lat',
                'source': 'mont-ra.stl',
                'trans': [0, 0, -70],
                'mat': Materials().aluminiumS,
            },
            'ra': {
                'parent': 'montRa',
                'trans': [0, 0, 190],
            },
            'montDec': {
                'parent': 'ra',
                'source': 'mont-dec.stl',
                'trans': [0, 0, -190],
                'mat': Materials().aluminiumS,
            },
            'montDecKnobs': {
                'parent': 'ra',
                'source': 'mont-dec-knobs.stl',
                'trans': [0, 0, -190],
                'mat': Materials().aluminium,
            },
            'montDecWeights': {
                'parent': 'ra',
                'source': 'mont-dec-weights.stl',
                'trans': [0, 0, -190],
                'mat': Materials().stainless,
            },
            'dec': {
                'parent': 'montDec',
                'trans': [159, 0, 190],
            },
            'montHead': {
                'parent': 'dec',
                'source': 'mont-head.stl',
                'trans': [-159, 0, -190],
                'mat': Materials().aluminiumS,
            },
            'montHeadKnobs': {
                'parent': 'dec',
                'source': 'mont-head-knobs.stl',
                'trans': [-159, 0, -190],
                'mat': Materials().aluminium,
            },
            'gem': {
                'parent': 'montHead',
                'source': [QCuboidMesh(), 100, 60, 10],
                'trans': [159, 0, 338.5],
                'mat': Materials().aluminiumB,
            },
            'gemCorr': {
                'parent': 'gem',
                'scale': [1, 1, 1],
            },
            'otaPlate': {
                'parent': 'gemCorr',
                'source': 'ota-plate.stl',
                'mat': Materials().aluminiumS,
            },
            'otaRing': {
                'parent': 'otaPlate',
                'source': 'ota-ring-s.stl',
                'scale': [1, 1, 1],
                'mat': Materials().aluminiumS,
            },
            'otaTube': {
                'parent': 'otaPlate',
                'source': 'ota-tube-s.stl',
                'scale': [1, 1, 1],
                'mat': Materials().white,
            },
            'otaImagetrain': {
                'parent': 'gemCorr',
                'source': 'ota-imagetrain.stl',
                'scale': [1, 1, 1],
                'mat': Materials().aluminiumS,
            },
            'otaCCD': {
                'parent': 'otaImagetrain',
                'source': 'ota-ccd.stl',
                'mat': Materials().aluminiumB,
            },
            'otaFocus': {
                'parent': 'otaImagetrain',
                'source': 'ota-focus.stl',
                'mat': Materials().aluminiumR,
            },
            'otaFocusTop': {
                'parent': 'otaImagetrain',
                'source': 'ota-focus-top.stl',
                'mat': Materials().white,
            },
        }

        for name in self.model:
            self.linkModel(self.model, name, rootEntity)

    def createWorld(self, rootEntity):
        """

        :param rootEntity:
        :return:
        """

        self.world = {
            'ref': {
                'parent': None,
                'source': None,
                'trans': None,
                'rot': [-90, 90, 0],
                'scale': [0.001, 0.001, 0.001],
                'mat': None,
            },
            'ref1000': {
                'parent': None,
                'source': None,
                'trans': None,
                'rot': [-90, 90, 0],
                'mat': None,
            },
            'environ': {
                'parent': 'ref',
                'source': 'dome-environ.stl',
                'mat': Materials().aluminiumG,
            },
            'domeFloor': {
                'parent': 'ref',
                'source': 'dome-floor.stl',
                'scale': [1, 1, 1],
                'mat': Materials().aluminiumGrey,
            },
            'domeWall': {
                'parent': 'ref',
                'source': 'dome-wall.stl',
                'scale': [1, 1, 1],
                'mat': Materials().dome1,
            },
            'domeSphere': {
                'parent': 'ref',
                'source': 'dome-sphere.stl',
                'scale': [1, 1, 1],
                'mat': Materials().dome1,
            },
            'domeSlit1': {
                'parent': 'domeSphere',
                'source': 'dome-slit1.stl',
                'scale': [1, 1, 1],
                'mat': Materials().dome2,
            },
            'domeSlit2': {
                'parent': 'domeSphere',
                'source': 'dome-slit2.stl',
                'scale': [1, 1, 1],
                'mat': Materials().dome2,
            },
            'domeDoor1': {
                'parent': 'domeSphere',
                'source': 'dome-door1.stl',
                'scale': [1, 1, 1],
                'mat': Materials().dome2,
            },
            'domeDoor2': {
                'parent': 'domeSphere',
                'source': 'dome-door2.stl',
                'scale': [1, 1, 1],
                'mat': Materials().dome2,
            },
            'test': {
                'parent': 'ref1000',
                'source': [QExtrudedTextMesh(), 0.1, 'Arial', 'Testtext'],
                'scale': [.1, .1, .1],
                'mat': Materials().aluminiumB,
            },
        }

        for name in self.world:
            self.linkModel(self.world, name, rootEntity)

        self.world['test']['t'].setTranslation(QVector3D(2, 2, 3))

    @staticmethod
    def createPoint(rEntity, alt, az):
        """

        :param rEntity:
        :param alt:
        :param az:
        :return: entity, x, y, z coordinates
        """

        radius = 5
        entity = QEntity(rEntity)
        mesh = QSphereMesh()
        mesh.setRadius(0.03)
        mesh.setRings(30)
        mesh.setSlices(30)
        trans = QTransform()
        x, y, z = transform.sphericalToCartesian(alt, az, radius)
        trans.setTranslation(QVector3D(x, y, 1 + z))
        entity.addComponent(mesh)
        entity.addComponent(trans)
        entity.addComponent(Materials().points)

        return entity, x, y, z

    def createBuildPoints(self, points):
        """
        createBuildPoints show the point in the sky if checked, in addition if selected the
        slew path between the points and in addition if checked the point numbers

        :return: success
        """

        if not self.world:
            return False

        if self.points:
            self.pointRoot.setParent(None)

        self.points.clear()

        if not points:
            return False

        self.pointRoot = QEntity(self.world['ref1000']['e'])

        for point in points:
            e, x, y, z = self.createPoint(self.pointRoot,
                                          np.radians(point[0]),
                                          np.radians(point[1]))

            element = {'e': e, 'x': x, 'y': y, 'z': z}
            self.points.append(element)

        return True

    def createScene(self, rootEntity):
        """

        :param rootEntity:
        :return:
        """

        self.createWorld(rootEntity)
        self.setDomeTransparency()
        self.updateDome()
        self.createOTA(rootEntity)

    def setDomeTransparency(self):
        """

        :return: True for test purpose
        """

        domeEntities = {
            'domeWall': {
                'trans': Materials().transparent,
                'solid': Materials().dome1
            },
            'domeSphere': {
                'trans': Materials().transparent,
                'solid': Materials().dome1
            },
            'domeSlit1': {
                'trans': Materials().transparent,
                'solid': Materials().dome2
            },
            'domeSlit2': {
                'trans': Materials().transparent,
                'solid': Materials().dome2
            },
            'domeDoor1': {
                'trans': Materials().transparent,
                'solid': Materials().dome2
            },
            'domeDoor2': {
                'trans': Materials().transparent,
                'solid': Materials().dome2
            },
        }

        transparent = self.ui.checkDomeTransparent.isChecked()

        for entity in domeEntities:
            if transparent:
                self.world[entity]['e'].addComponent(domeEntities[entity]['trans'])
            else:
                self.world[entity]['e'].addComponent(domeEntities[entity]['solid'])

        return True

    def updateSettings(self):
        """
        updateSettings resize parts depending on the setting made in the dome tab. likewise
        some transformations have to be reverted as they are propagated through entity linking.

        :return:
        """

        if self.app.mount.obsSite.location:
            latitude = self.app.mount.obsSite.location.latitude.degrees
            self.model['lat']['t'].setRotationY(- abs(latitude))

        if self.app.mount.geometry.offGemPlate:
            offPlateOTA = self.app.mount.geometry.offPlateOTA * 1000
            lat = - self.app.mainW.ui.offLAT.value() * 1000

            self.model['gem']['m'].setYExtent(abs(lat) + 80)
            self.model['gem']['t'].setTranslation(QVector3D(159.0, lat / 2, 338.5))
            self.model['gemCorr']['t'].setTranslation(QVector3D(0.0, lat / 2, 0.0))

            scaleRad = (offPlateOTA - 25) / 55
            scaleRad = max(scaleRad, 1)

            self.model['otaRing']['t'].setScale3D(QVector3D(1.0, scaleRad, scaleRad))
            self.model['otaRing']['t'].setTranslation(QVector3D(0.0, 0.0, - 10 * scaleRad + 10))
            self.model['otaTube']['t'].setScale3D(QVector3D(1.0, scaleRad, scaleRad))
            self.model['otaTube']['t'].setTranslation(QVector3D(0.0, 0.0, - 10 * scaleRad + 10))
            self.model['otaImagetrain']['t'].setTranslation(QVector3D(0, 0, 65 * (scaleRad - 1)))

        if 't' not in self.world['domeFloor']:
            return False

        north = self.app.mainW.ui.domeNorthOffset.value() * 1000
        east = self.app.mainW.ui.domeEastOffset.value() * 1000
        vertical = self.app.mainW.ui.domeVerticalOffset.value() * 1000
        scale = (960 + vertical) / 960
        self.model['domeColumn']['t'].setTranslation(QVector3D(north, -east, 0))
        self.model['domeColumn']['t'].setScale3D(QVector3D(1, 1, scale))
        self.model['mountBase']['t'].setTranslation(QVector3D(north, -east, 1000 + vertical))
        self.model['domeCompassRose']['t'].setTranslation(QVector3D(north, -east, 0))
        self.model['domeCompassRoseChar']['t'].setTranslation(QVector3D(north, -east, 0))

        radius = self.app.mainW.ui.domeRadius.value() * 1000
        scale = 1 + (radius - 1250) / 1250
        corrZ = - (scale - 1) * 800
        self.world['domeFloor']['t'].setScale3D(QVector3D(scale, scale, 1))
        self.world['domeWall']['t'].setScale3D(QVector3D(scale, scale, 1))
        self.world['domeSphere']['t'].setScale3D(QVector3D(scale, scale, scale))
        self.world['domeSphere']['t'].setTranslation(QVector3D(0, 0, corrZ))

        self.setDomeTransparency()

        return True

    def updateMount(self):
        """
        updateMount moves ra and dec axis according to the values in the mount.

        :return:
        """

        if ('t' not in self.model['ra'] and 't' not in self.model['dec']):
            return False

        angRA = self.app.mount.obsSite.angularPosRA
        angDEC = self.app.mount.obsSite.angularPosDEC

        if not (angRA and angDEC):
            return False

        self.model['ra']['t'].setRotationX(- angRA.degrees + 90)
        self.model['dec']['t'].setRotationZ(- angDEC.degrees)

        lat = self.app.mount.obsSite.location.latitude
        ha = self.app.mount.obsSite.haJNow
        dec = self.app.mount.obsSite.decJNow
        pierside = self.app.mount.obsSite.pierside

        if not self.ui.checkShowPointer.isChecked():
            self.model['pointer']['e'].setEnabled(False)
            return False

        self.model['pointer']['e'].setEnabled(True)
        geometry = self.app.mount.geometry
        _, _, x, y, z = geometry.calcTransformationMatrices(ha=ha,
                                                            dec=dec,
                                                            lat=lat,
                                                            pierside=pierside)

        x = x * 1000
        y = y * 1000
        z = z * 1000 + 1000

        self.model['pointer']['t'].setTranslation(QVector3D(x, y, z))

        return True

    def updateDome(self):
        """
        updateDome moves dome components
        you normally have to revert your transformation in linked entities if they have
        fixed sizes because they propagate transformations.
        for the shutter i would like to keep the width setting unscaled with increasing dome
        radius

        :return:
        """

        domeEntities = ['domeWall', 'domeSphere', 'domeSlit1',
                        'domeSlit2', 'domeDoor1', 'domeDoor2']

        if self.app.mainW is None:
            devicePresent = False
        else:
            devicePresent = self.app.mainW.deviceStat.get('dome', False)
            if devicePresent is None:
                devicePresent = False

        viewDisabled = self.ui.checkDomeDisable.isChecked()

        visible = devicePresent and not viewDisabled

        for entity in domeEntities:
            self.world[entity]['e'].setEnabled(visible)

        if 'ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION' in self.app.dome.data:
            az = self.app.dome.data['ABS_DOME_POSITION.DOME_ABSOLUTE_POSITION']
            self.world['domeSphere']['t'].setRotationZ(az)

        if 'DOME_SHUTTER.SHUTTER_OPEN' in self.app.dome.data:
            radius = self.app.mainW.ui.domeRadius.value() * 1000
            scale = 1 + (radius - 1250) / 1250

            self.world['domeDoor1']['t'].setScale3D(QVector3D(1, scale, 1))
            self.world['domeDoor2']['t'].setScale3D(QVector3D(1, scale, 1))

            stat = self.app.dome.data['DOME_SHUTTER.SHUTTER_OPEN']
            width = self.app.mainW.ui.domeShutterWidth.value() * 1000 / 2 / scale
            if stat:
                self.world['domeDoor1']['t'].setTranslation(QVector3D(0, width, 0))
                self.world['domeDoor2']['t'].setTranslation(QVector3D(0, -width, 0))
            else:
                self.world['domeDoor1']['t'].setTranslation(QVector3D(0, 0, 0))
                self.world['domeDoor2']['t'].setTranslation(QVector3D(0, 0, 0))

        return True
