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
from PyQt5.QtCore import QMutex
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QVector3D
from PyQt5.QtWidgets import QWidget
from PyQt5.Qt3DExtras import Qt3DWindow
from PyQt5.Qt3DExtras import QOrbitCameraController
from PyQt5.Qt3DRender import QPointLight
from PyQt5.Qt3DCore import QEntity, QTransform

# local import
from gui.utilities import toolsQtWidget
from gui.widgets import simulator_ui
from gui.extWindows.simulator.materials import Materials
from gui.extWindows.simulator import tools
from gui.extWindows.simulator.dome import SimulatorDome
from gui.extWindows.simulator.telescope import SimulatorTelescope
from gui.extWindows.simulator.horizon import SimulatorHorizon
from gui.extWindows.simulator.points import SimulatorBuildPoints
from gui.extWindows.simulator.pointer import SimulatorPointer
from gui.extWindows.simulator.laser import SimulatorLaser


class SimulatorWindow(toolsQtWidget.MWidget):

    __all__ = ['SimulatorWindow',
               ]

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.ui = simulator_ui.Ui_SimulatorDialog()
        self.ui.setupUi(self)
        self.createMutex = QMutex()

        self.view = Qt3DWindow()
        container = QWidget.createWindowContainer(self.view)
        self.ui.simulator.addWidget(container)

        self.rootEntity = QEntity()
        self.camera = self.view.camera()
        self.camera.lens().setPerspectiveProjection(60.0, 16.0 / 9.0, 0.1, 1000.0)
        self.camera.setViewCenter(QVector3D(0.0, 1.5, 0.0))
        self.camera.setPosition(QVector3D(5.0, 15.0, 3.0))
        self.camera.setUpVector(QVector3D(0.0, 1.0, 0.0))
        self.camController = QOrbitCameraController(self.rootEntity)
        self.camController.setCamera(self.camera)
        self.camController.setLinearSpeed(5.0)
        self.camController.setLookSpeed(90)
        self.view.setRootEntity(self.rootEntity)
        self.view.defaultFrameGraph().setClearColor(QColor(24, 24, 24))

        self.pL0E = QEntity(self.rootEntity)
        self.pL0 = QPointLight(self.pL0E)
        self.pL0.setIntensity(1.5)
        self.pL0ETransform = QTransform()
        self.pL0ETransform.setTranslation(QVector3D(5, 20, 5))
        self.pL0E.addComponent(self.pL0)
        self.pL0E.addComponent(self.pL0ETransform)

        self.dome = SimulatorDome(self.app)
        self.telescope = SimulatorTelescope(self.app)
        self.horizon = SimulatorHorizon(self.app)
        self.buildPoints = SimulatorBuildPoints(self.app)
        self.pointer = SimulatorPointer(self.app)
        self.laser = SimulatorLaser(self.app)
        self.world = None

    def initConfig(self):
        """
        :return: True for test purpose
        """
        if 'simulatorW' not in self.app.config:
            self.app.config['simulatorW'] = {}
        config = self.app.config['simulatorW']
        height = config.get('height', 600)
        width = config.get('width', 800)
        self.resize(width, height)
        x = config.get('winPosX', 0)
        y = config.get('winPosY', 0)
        if x > self.screenSizeX - width:
            x = 0
        if y > self.screenSizeY - height:
            y = 0
        if x != 0 and y != 0:
            self.move(x, y)

        if 'cameraPositionX' in config:
            x = config['cameraPositionX']
            y = config['cameraPositionY']
            z = config['cameraPositionZ']
            self.camera.setPosition(QVector3D(x, y, z))
            self.camera.setUpVector(QVector3D(0.0, 1.0, 0.0))

        self.ui.checkDomeTransparent.setChecked(config.get('checkDomeTransparent', False))
        self.ui.checkShowPointer.setChecked(config.get('checkShowPointer', False))
        self.ui.checkShowLaser.setChecked(config.get('checkShowLaser', False))
        self.ui.checkShowBuildPoints.setChecked(config.get('checkShowBuildPoints', False))
        self.ui.checkShowNumbers.setChecked(config.get('checkShowNumbers', False))
        self.ui.checkShowSlewPath.setChecked(config.get('checkShowSlewPath', False))
        self.ui.checkShowHorizon.setChecked(config.get('checkShowHorizon', False))

        return True

    def storeConfig(self):
        """
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
        config['checkShowPointer'] = self.ui.checkShowPointer.isChecked()
        config['checkShowLaser'] = self.ui.checkShowLaser.isChecked()
        config['checkShowBuildPoints'] = self.ui.checkShowBuildPoints.isChecked()
        config['checkShowNumbers'] = self.ui.checkShowNumbers.isChecked()
        config['checkShowSlewPath'] = self.ui.checkShowSlewPath.isChecked()
        config['checkShowHorizon'] = self.ui.checkShowHorizon.isChecked()
        return True

    def closeEvent(self, closeEvent):
        """
        :param closeEvent:
        :return:
        """
        self.storeConfig()

        self.app.update1s.disconnect(self.dome.updatePositions)
        self.ui.checkDomeTransparent.clicked.disconnect(self.setDomeTransparency)
        self.ui.checkShowBuildPoints.clicked.disconnect(self.buildPointsCreate)
        self.ui.checkShowNumbers.clicked.disconnect(self.buildPointsCreate)
        self.ui.checkShowSlewPath.clicked.disconnect(self.buildPointsCreate)
        self.app.updatePointMarker.disconnect(self.buildPointsCreate)
        self.ui.checkShowHorizon.clicked.disconnect(self.horizonCreate)
        self.ui.checkShowPointer.clicked.disconnect(self.pointerCreate)
        self.ui.checkShowLaser.clicked.disconnect(self.laserCreate)
        self.ui.topView.clicked.disconnect(self.topView)
        self.ui.topEastView.clicked.disconnect(self.topEastView)
        self.ui.topWestView.clicked.disconnect(self.topWestView)
        self.ui.eastView.clicked.disconnect(self.eastView)
        self.ui.westView.clicked.disconnect(self.westView)
        self.app.updateDomeSettings.disconnect(self.updateSettings)
        self.app.updateDomeSettings.disconnect(self.telescope.updateSettings)
        self.app.updateDomeSettings.disconnect(self.dome.updateSettings)
        self.app.mount.signals.pointDone.disconnect(self.telescope.updatePositions)
        self.app.mount.signals.pointDone.disconnect(self.pointer.updatePositions)
        self.app.mount.signals.pointDone.disconnect(self.laser.updatePositions)
        self.app.mount.signals.pointDone.disconnect(self.buildPoints.updatePositions)
        self.app.drawBuildPoints.disconnect(self.buildPointsCreate)
        self.app.drawHorizonPoints.disconnect(self.horizonCreate)
        self.camera.positionChanged.disconnect(self.limitPositionZ)
        super().closeEvent(closeEvent)

    def showWindow(self):
        """
        :return: True for test purpose
        """
        self.createScene(self.rootEntity)
        self.ui.checkDomeTransparent.clicked.connect(self.setDomeTransparency)
        self.ui.checkShowBuildPoints.clicked.connect(self.buildPointsCreate)
        self.ui.checkShowNumbers.clicked.connect(self.buildPointsCreate)
        self.ui.checkShowSlewPath.clicked.connect(self.buildPointsCreate)
        self.app.updatePointMarker.connect(self.buildPointsCreate)
        self.ui.checkShowHorizon.clicked.connect(self.horizonCreate)
        self.ui.checkShowPointer.clicked.connect(self.pointerCreate)
        self.ui.checkShowLaser.clicked.connect(self.laserCreate)
        self.ui.topView.clicked.connect(self.topView)
        self.ui.topEastView.clicked.connect(self.topEastView)
        self.ui.topWestView.clicked.connect(self.topWestView)
        self.ui.eastView.clicked.connect(self.eastView)
        self.ui.westView.clicked.connect(self.westView)
        self.app.update1s.connect(self.dome.updatePositions)
        self.app.updateDomeSettings.connect(self.updateSettings)
        self.app.updateDomeSettings.connect(self.telescope.updateSettings)
        self.app.updateDomeSettings.connect(self.dome.updateSettings)
        self.app.mount.signals.pointDone.connect(self.telescope.updatePositions)
        self.app.mount.signals.pointDone.connect(self.pointer.updatePositions)
        self.app.mount.signals.pointDone.connect(self.laser.updatePositions)
        self.app.mount.signals.pointDone.connect(self.buildPoints.updatePositions)
        self.app.drawBuildPoints.connect(self.buildPointsCreate)
        self.app.drawHorizonPoints.connect(self.horizonCreate)
        self.camera.positionChanged.connect(self.limitPositionZ)
        self.show()
        return True

    def limitPositionZ(self):
        """
        :return:
        """
        pos = self.camera.position()
        if pos[1] < 0:
            z = 0
        else:
            z = pos[1]
        posNew = QVector3D(pos[0], z, pos[2])
        self.camera.setPosition(posNew)
        return True

    def buildPointsCreate(self):
        """
        :return: True for test purpose
        """
        self.buildPoints.create(self.world['ref1000']['e'],
                                self.ui.checkShowBuildPoints.isChecked(),
                                self.ui.checkShowNumbers.isChecked(),
                                self.ui.checkShowSlewPath.isChecked())
        return True

    def horizonCreate(self):
        """
        :return: True for test purpose
        """
        self.horizon.create(self.world['ref1000']['e'],
                            self.ui.checkShowHorizon.isChecked())
        return True

    def pointerCreate(self):
        """
        :return: True for test purpose
        """
        self.pointer.create(self.world['ref']['e'],
                            self.ui.checkShowPointer.isChecked())
        return True

    def laserCreate(self):
        """
        :return: True for test purpose
        """
        self.laser.create(self.world['ref']['e'],
                          self.ui.checkShowLaser.isChecked())
        return True

    def setDomeTransparency(self):
        """
        :return: True for test purpose
        """
        self.dome.setTransparency(self.ui.checkDomeTransparent.isChecked())
        return True

    def topView(self):
        """
        move the camera to top view position

        :return: True for test purpose
        """
        self.changeStyleDynamic(self.ui.telescopeView, 'running', False)
        self.camera.setViewCenter(QVector3D(0.0, 1.5, 0.0))
        self.camera.setPosition(QVector3D(0.0, 5.0, 0.0))
        self.camera.setUpVector(QVector3D(0.0, 1.0, 0.0))
        return True

    def topEastView(self):
        """
        moves the camera to top east position

        :return: True for test purpose
        """
        self.changeStyleDynamic(self.ui.telescopeView, 'running', False)
        self.camera.setViewCenter(QVector3D(0.1, 1.5, 0.1))
        self.camera.setPosition(QVector3D(5.0, 5.0, 0.0))
        self.camera.setUpVector(QVector3D(0.0, 1.0, 0.0))
        return True

    def topWestView(self):
        """
        moves the camera to top west position

        :return: True for test purpose
        """
        self.changeStyleDynamic(self.ui.telescopeView, 'running', False)
        self.camera.setViewCenter(QVector3D(0.0, 1.5, 0.0))
        self.camera.setPosition(QVector3D(-5.0, 5.0, 0.0))
        self.camera.setUpVector(QVector3D(0.0, 1.0, 0.0))
        return True

    def eastView(self):
        """
        moves the camera to east position

        :return: True for test purpose
        """
        self.changeStyleDynamic(self.ui.telescopeView, 'running', False)
        self.camera.setViewCenter(QVector3D(0.0, 1.5, 0.0))
        self.camera.setPosition(QVector3D(5.0, 1.5, 0.0))
        self.camera.setUpVector(QVector3D(0.0, 1.0, 0.0))
        return True

    def westView(self):
        """
        moves the camera to west position

        :return: True for test purpose
        """
        self.changeStyleDynamic(self.ui.telescopeView, 'running', False)
        self.camera.setViewCenter(QVector3D(0.0, 1.5, 0.0))
        self.camera.setPosition(QVector3D(-5.0, 1.5, 0.0))
        self.camera.setUpVector(QVector3D(0.0, 1.0, 0.0))
        return True

    def createWorld(self, rEntity):
        """
        first transformation is from fusion360 to qt3d fusion360 (x is north,
        y is west, z is up), scale in mm Qt3D (-z is north, x is east, y is up)
        scale is m and set as reference. from there on we are in the fusion
        coordinate system

        'ref' is the fusion360 coordinate system, please be aware that rotations
        around the z axis for azimuth is clockwise and not counterclockwise as a
        right handed coordinate system would propose.

        for the sake of simplifying there is another reference, which only has
        the corrections in coordinates and not for scaling, this is called 'ref1000'

        beside defining the references, createWorld build the foundation for the
        positioning of a raw telescope column and a compass rose.

        :param rEntity:
        :return:
        """
        self.world = {
            'ref1000': {
                'parent': None,
                'rot': [-90, 90, 0],
            },
            'ref': {
                'parent': 'ref1000',
                'scale': [0.001, 0.001, 0.001],
            },
            'environ': {
                'parent': 'ref',
                'source': 'dome-environ.stl',
                'scale': [2, 2, 1],
                'mat': Materials().environ1,
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
        }

        for name in self.world:
            tools.linkModel(self.world, name, rEntity)

    def createScene(self, rEntity):
        """
        createScene initially builds all 3d models and collects them to a scene. please look
        closely which references are used-

        :param rEntity:
        :return:
        """
        if not self.createMutex.tryLock():
            return False

        numbers = self.ui.checkShowNumbers.isChecked()
        path = self.ui.checkShowSlewPath.isChecked()
        pointer = self.ui.checkShowPointer.isChecked()
        laser = self.ui.checkShowLaser.isChecked()
        dome = self.app.deviceStat.get('dome', False)
        horizon = self.ui.checkShowHorizon.isChecked()
        points = self.ui.checkShowBuildPoints.isChecked()
        isDomeTransparent = self.ui.checkDomeTransparent.isChecked()

        if dome:
            self.ui.checkDomeTransparent.setEnabled(True)
            self.ui.checkShowPointer.setEnabled(True)
        else:
            self.ui.checkDomeTransparent.setEnabled(False)
            self.ui.checkDomeTransparent.setChecked(False)
            self.ui.checkShowPointer.setEnabled(False)
            self.ui.checkShowPointer.setChecked(False)

        self.createWorld(rEntity)
        self.telescope.create(self.world['ref']['e'], True)
        self.dome.create(self.world['ref']['e'], dome)
        self.pointer.create(self.world['ref']['e'], pointer)
        self.laser.create(self.world['ref']['e'], laser)
        self.buildPoints.create(self.world['ref1000']['e'], points, numbers, path)
        self.horizon.create(self.world['ref1000']['e'], horizon)

        self.updateSettings()
        self.dome.updateSettings()
        self.dome.updatePositions()
        self.dome.setTransparency(isDomeTransparent)
        self.telescope.updateSettings()
        self.telescope.updatePositions()
        self.createMutex.unlock()
        return True

    def updateSettings(self):
        """
        updateSettings resize parts depending on the setting made in the dome tab. likewise
        some transformations have to be reverted as they are propagated through entity linking.

        :return:
        """
        if not self.world:
            return False

        north = self.app.mount.geometry.offNorth * 1000
        east = self.app.mount.geometry.offEast * 1000
        vertical = self.app.mount.geometry.offVert * 1000
        scale = (960 + vertical) / 960

        self.world['domeColumn']['t'].setTranslation(QVector3D(north, -east, 0))
        self.world['domeColumn']['t'].setScale3D(QVector3D(1, 1, scale))
        self.world['domeCompassRose']['t'].setTranslation(QVector3D(north, -east, 0))
        self.world['domeCompassRoseChar']['t'].setTranslation(QVector3D(north, -east, 0))
        return True
