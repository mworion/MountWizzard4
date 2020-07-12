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
from PyQt5.Qt3DExtras import QOrbitCameraController, QExtrudedTextMesh, QCylinderMesh
from PyQt5.Qt3DRender import QMesh, QPointLight
from PyQt5.Qt3DCore import QEntity, QTransform

# local import
from mw4.base import transform
from mw4.gui import widget
from mw4.gui.widgets import simulator_ui
from mw4.gui.simulatorMaterials import Materials


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
        self.buildPoints = None
        self.points = []
        self.pointRoot = None

        self.initConfig()
        self.showWindow()

        # connect to gui
        self.ui.checkDomeTransparent.clicked.connect(self.updateSettings)
        self.ui.checkShowBuildPoints.clicked.connect(self.createBuildPoints)
        self.ui.checkShowNumbers.clicked.connect(self.createBuildPoints)
        self.ui.checkShowSlewPath.clicked.connect(self.createBuildPoints)
        self.ui.topView.clicked.connect(self.topView)
        self.ui.topEastView.clicked.connect(self.topEastView)
        self.ui.topWestView.clicked.connect(self.topWestView)
        self.ui.eastView.clicked.connect(self.eastView)
        self.ui.westView.clicked.connect(self.westView)
        self.ui.checkPL.clicked.connect(self.setPL)
        self.ui.telescopeView.clicked.connect(self.setTelescopeView)

        # connect functional signals
        self.app.update1s.connect(self.updateDome)
        self.app.redrawSimulator.connect(self.updateSettings)
        self.app.sendBuildPoints.connect(self.storeBuildPoints)
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
        self.ui.checkShowBuildPoints.setChecked(config.get('checkShowBuildPoints', False))
        self.ui.checkShowNumbers.setChecked(config.get('checkShowNumbers', False))
        self.ui.checkShowSlewPath.setChecked(config.get('checkShowSlewPath', False))
        self.ui.checkShowHorizon.setChecked(config.get('checkShowHorizon', False))

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
        config['checkShowBuildPoints'] = self.ui.checkShowBuildPoints.isChecked()
        config['checkShowNumbers'] = self.ui.checkShowNumbers.isChecked()
        config['checkShowSlewPath'] = self.ui.checkShowSlewPath.isChecked()
        config['checkShowHorizon'] = self.ui.checkShowHorizon.isChecked()

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

    def storeBuildPoints(self, points):
        """

        :param points:
        :return: True for test purpose
        """

        self.buildPoints = points
        self.createBuildPoints()

        return True

    def setTelescopeView(self):
        """

        :return: True for test purpose
        """

        if self.ui.telescopeView.property('running'):
            self.changeStyleDynamic(self.ui.telescopeView, 'running', False)
        else:
            self.changeStyleDynamic(self.ui.telescopeView, 'running', True)
            self.camera.setViewCenter(QVector3D(0.0, 3.0, -3.0))
            self.camera.setUpVector(QVector3D(0.0, 1.0, 0.0))
            self.camera.setPosition(QVector3D(0, 2, 0))

        self.createBuildPoints()
        return True

    def setPL(self):
        """
        setPL enables point light and therefore changes the light conditions

        :return: True for test purpose
        """

        self.pL0E.setEnabled(self.ui.checkPL.isChecked())
        self.pL1E.setEnabled(not self.ui.checkPL.isChecked())

        return True

    def topView(self):
        """

        :return: True for test purpose
        """

        self.changeStyleDynamic(self.ui.telescopeView, 'running', False)
        self.createBuildPoints()
        self.camera.setViewCenter(QVector3D(0.0, 1.5, 0.0))
        self.camera.setPosition(QVector3D(0.0, 10.0, 0.0))

        return True

    def topEastView(self):
        """

        :return: True for test purpose
        """

        self.changeStyleDynamic(self.ui.telescopeView, 'running', False)
        self.createBuildPoints()
        self.camera.setViewCenter(QVector3D(0.0, 1.5, 0.0))
        self.camera.setPosition(QVector3D(5.0, 5.0, 0.0))
        self.camera.setUpVector(QVector3D(0.0, 1.0, 0.0))

        return True

    def topWestView(self):
        """

        :return: True for test purpose
        """

        self.changeStyleDynamic(self.ui.telescopeView, 'running', False)
        self.createBuildPoints()
        self.camera.setViewCenter(QVector3D(0.0, 1.5, 0.0))
        self.camera.setPosition(QVector3D(-5.0, 5.0, 0.0))
        self.camera.setUpVector(QVector3D(0.0, 1.0, 0.0))

        return True

    def eastView(self):
        """

        :return: True for test purpose
        """

        self.changeStyleDynamic(self.ui.telescopeView, 'running', False)
        self.createBuildPoints()
        self.camera.setViewCenter(QVector3D(0.0, 1.5, 0.0))
        self.camera.setPosition(QVector3D(5.0, 1.5, 0.0))
        self.camera.setUpVector(QVector3D(0.0, 1.0, 0.0))

        return True

    def westView(self):
        """

        :return: True for test purpose
        """

        self.changeStyleDynamic(self.ui.telescopeView, 'running', False)
        self.createBuildPoints()
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
            elif isinstance(source[0], QCylinderMesh):
                mesh = source[0]
                mesh.setLength(source[1])
                mesh.setRadius(source[2])
                mesh.setRings(source[3])
                mesh.setSlices(source[4])
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
                'mat': Materials().environ1,
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
        }

        for name in self.world:
            self.linkModel(self.world, name, rootEntity)

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

        alt, az, radius = transform.cartesianToSpherical(dx, dy, dz)
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
        x, y, z = transform.sphericalToCartesian(alt, az, radius)
        trans.setTranslation(QVector3D(x, y, z + 1.35))
        entity.addComponent(mesh)
        entity.addComponent(trans)
        entity.addComponent(Materials().points)

        return entity, x, y, z

    @staticmethod
    def createAnnotation(rEntity, alt, az, text, faceIn):
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

    def createBuildPoints(self):
        """
        createBuildPoints show the point in the sky if checked, in addition if selected the
        slew path between the points and in addition if checked the point numbers
        as the azimuth (second element in tuple) is turning clockwise, it's opposite to the
        right turning coordinate system (z is upwards), which means angle around z
        (which is azimuth) turns counterclockwise. so we have to set - azimuth for coordinate
        calculation

        :return: success
        """

        if not self.world:
            return False

        if self.points:
            self.pointRoot.setParent(None)

        self.points.clear()

        if not self.ui.checkShowBuildPoints.isChecked():
            return False

        if not self.buildPoints:
            return False

        faceIn = self.ui.telescopeView.property('running')

        self.pointRoot = QEntity(self.world['ref1000']['e'])

        for index, point in enumerate(self.buildPoints):
            e, x, y, z = self.createPoint(self.pointRoot,
                                          np.radians(point[0]),
                                          np.radians(-point[1]))

            if self.ui.checkShowNumbers.isChecked():
                a = self.createAnnotation(e, point[0], -point[1], f'{index:02d}', faceIn)
            else:
                a = None

            if index and self.ui.checkShowSlewPath.isChecked():
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
                'trans': Materials().dome1t,
                'solid': Materials().dome1
            },
            'domeSphere': {
                'trans': Materials().dome1t,
                'solid': Materials().dome1
            },
            'domeSlit1': {
                'trans': Materials().dome2t,
                'solid': Materials().dome2
            },
            'domeSlit2': {
                'trans': Materials().dome2t,
                'solid': Materials().dome2
            },
            'domeDoor1': {
                'trans': Materials().dome2t,
                'solid': Materials().dome2
            },
            'domeDoor2': {
                'trans': Materials().dome2t,
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
        when telescope view is enable as well, the camera position and view target is
        adjusted, too.

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

        geometry = self.app.mount.geometry
        _, _, x, y, z = geometry.calcTransformationMatrices(ha=ha,
                                                            dec=dec,
                                                            lat=lat,
                                                            pierside=pierside)
        x = x * 1000
        y = y * 1000
        z = z * 1000 + 1000

        if not self.ui.checkShowPointer.isChecked():
            self.model['pointer']['e'].setEnabled(False)

        else:
            self.model['pointer']['e'].setEnabled(True)
            self.model['pointer']['t'].setTranslation(QVector3D(x, y, z))

        if self.ui.telescopeView.property('running'):
            self.camera.setViewCenter(QVector3D(- y / 500, z / 500, - x / 500))
            self.camera.setPosition(QVector3D(0.0, 1.7, 0.0))
            self.camera.setUpVector(QVector3D(0.0, 1.0, 0.0))

        return True

    def updateDome(self):
        """
        updateDome moves dome components
        you normally have to revert your transformation in linked entities if they have
        fixed sizes because they propagate transformations.
        for the shutter i would like to keep the width setting unscaled with increasing dome
        radius

        :return: success
        """

        if not self.app.mainW:
            return False

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
