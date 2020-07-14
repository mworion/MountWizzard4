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
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QVector3D
from PyQt5.QtWidgets import QWidget
from PyQt5.Qt3DExtras import Qt3DWindow
from PyQt5.Qt3DExtras import QOrbitCameraController
from PyQt5.Qt3DRender import QPointLight
from PyQt5.Qt3DCore import QEntity, QTransform

# local import
from mw4.gui import widget
from mw4.gui.widgets import simulator_ui
from mw4.gui.simulator.materials import Materials
from mw4.gui.simulator import tools
from mw4.gui.simulator.dome import SimulatorDome
from mw4.gui.simulator.telescope import SimulatorTelescope
from mw4.gui.simulator.horizon import SimulatorHorizon
from mw4.gui.simulator.buildPoints import SimulatorBuildPoints


class SimulatorWindow(widget.MWidget):

    __all__ = ['SimulatorWindow',
               ]

    def __init__(self, app):
        super().__init__()

        self.app = app

        self.ui = simulator_ui.Ui_SimulatorDialog()
        self.ui.setupUi(self)
        self.initUI()

        self.view = Qt3DWindow()
        self.container = QWidget.createWindowContainer(self.view)
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

        self.dome = SimulatorDome(self.app)
        self.telescope = SimulatorTelescope(self.app)
        self.horizon = SimulatorHorizon(self.app)
        self.buildPoints = SimulatorBuildPoints(self.app)
        self.world = None

        self.initConfig()
        self.showWindow()

        # connect to gui

        self.ui.checkDomeTransparent.clicked.connect(
            lambda: self.dome.setTransparency(self.ui.checkDomeTransparent.isChecked()))
        self.ui.checkDomeEnable.clicked.connect(
            lambda: self.dome.create(self.world['ref']['e'],
                                     self.ui.checkDomeEnable.isChecked()))
        self.ui.checkShowBuildPoints.clicked.connect(
            lambda: self.buildPoints.create(self.world['ref1000']['e'],
                                            self.ui.checkShowBuildPoints.isChecked(),
                                            self.ui.checkShowNumbers.isChecked(),
                                            self.ui.checkShowSlewPath.isChecked()))
        self.ui.checkShowNumbers.clicked.connect(
            lambda: self.buildPoints.create(self.world['ref1000']['e'],
                                            self.ui.checkShowBuildPoints.isChecked(),
                                            self.ui.checkShowNumbers.isChecked(),
                                            self.ui.checkShowSlewPath.isChecked()))
        self.ui.checkShowSlewPath.clicked.connect(
            lambda: self.buildPoints.create(self.world['ref1000']['e'],
                                            self.ui.checkShowBuildPoints.isChecked(),
                                            self.ui.checkShowNumbers.isChecked(),
                                            self.ui.checkShowSlewPath.isChecked()))
        self.ui.checkShowHorizon.clicked.connect(
            lambda: self.horizon.create(self.world['ref1000']['e'],
                                        self.ui.checkShowHorizon.isChecked()))

        self.ui.topView.clicked.connect(self.topView)
        self.ui.topEastView.clicked.connect(self.topEastView)
        self.ui.topWestView.clicked.connect(self.topWestView)
        self.ui.eastView.clicked.connect(self.eastView)
        self.ui.westView.clicked.connect(self.westView)
        self.ui.checkPL.clicked.connect(self.setPL)

        # connect functional signals
        self.app.update1s.connect(self.dome.updatePositions)
        self.app.mount.signals.pointDone.connect(self.telescope.updatePositions)
        self.app.drawDome.connect(
            lambda: self.dome.create(self.world['ref']['e'],
                                     self.ui.checkDomeEnable.isChecked()))
        self.app.drawBuildPoints.connect(
            lambda: self.buildPoints.create(self.world['ref1000']['e'],
                                            self.ui.checkShowBuildPoints.isChecked(),
                                            self.ui.checkShowNumbers.isChecked(),
                                            self.ui.checkShowSlewPath.isChecked()))
        self.app.drawHorizonPoints.connect(
            lambda: self.horizon.create(self.world['ref1000']['e'],
                                        self.ui.checkShowHorizon.isChecked()))

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
        self.ui.checkDomeEnable.setChecked(config.get('checkDomeEnable', False))
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
        config['checkDomeEnable'] = self.ui.checkDomeEnable.isChecked()
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
        self.show()

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
        }

        for name in self.world:
            tools.linkModel(self.world, name, rootEntity)

    def createScene(self, rEntity):
        """

        :param rEntity:
        :return:
        """

        numbers = self.ui.checkShowNumbers.isChecked()
        path = self.ui.checkShowSlewPath.isChecked()

        self.createWorld(rEntity)
        self.dome.create(self.world['ref']['e'], False)
        self.telescope.create(self.world['ref']['e'], True)
        self.buildPoints.create(self.world['ref1000']['e'], False, numbers, path)
        self.horizon.create(self.world['ref1000']['e'], False)
