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
from PyQt6.QtGui import QColor
from PyQt6.QtGui import QVector3D
from PyQt6.QtWidgets import QWidget
from PyQt6.Qt3DExtras import Qt3DWindow
from PyQt6.Qt3DExtras import QOrbitCameraController
from PyQt6.Qt3DCore import QEntity
from PyQt6.Qt3DRender import QObjectPicker
import PyQt6

# local import
from gui.utilities.toolsQtWidget import MWidget
from gui.widgets import simulator_ui
from gui.extWindows.simulator.materials import Materials
from gui.extWindows.simulator.dome import SimulatorDome
from gui.extWindows.simulator.telescope import SimulatorTelescope
from gui.extWindows.simulator.horizon import SimulatorHorizon
from gui.extWindows.simulator.buildPoints import SimulatorBuildPoints
from gui.extWindows.simulator.pointer import SimulatorPointer
from gui.extWindows.simulator.laser import SimulatorLaser
from gui.extWindows.simulator.world import SimulatorWorld
from gui.extWindows.simulator.light import SimulatorLight
from gui.extWindows.simulator.tools import linkModel
from gui.extWindows.materialW import MaterialWindow


class SimulatorWindow(MWidget):
    """
    """
    __all__ = ['SimulatorWindow']

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.ui = simulator_ui.Ui_SimulatorDialog()
        self.ui.setupUi(self)
        self.entityModel = {'root_qt3d': QEntity()}

        self.world = SimulatorWorld(self, self.app)
        self.light = SimulatorLight(self, self.app)
        self.dome = SimulatorDome(self, self.app)
        self.telescope = SimulatorTelescope(self, self.app)
        self.laser = SimulatorLaser(self, self.app)
        self.pointer = SimulatorPointer(self, self.app)
        self.horizon = SimulatorHorizon(self, self.app)
        self.buildPoints = SimulatorBuildPoints(self, self.app)
        self.materials = Materials()
        self.materialWindow = MaterialWindow(self.app)
        self.materialWindow.initConfig()
        self.materialWindow.showWindow()

        self.camera = None
        self.cameraController = None

        self.view = Qt3DWindow()
        self.view.defaultFrameGraph().setClearColor(QColor(self.M_BACK))
        container = QWidget.createWindowContainer(self.view)
        self.ui.simulator.addWidget(container)
        self.view.setRootEntity(self.entityModel['root_qt3d'])

        self.picker = QObjectPicker()
        self.entityModel['root_qt3d'].addComponent(self.picker)
        self.view.renderSettings().pickingSettings().setPickMethod(
            PyQt6.Qt3DRender.QPickingSettings.PickMethod.TrianglePicking)
        self.view.renderSettings().pickingSettings().setPickResultMode(
            PyQt6.Qt3DRender.QPickingSettings.PickResultMode.NearestPick)
        self.view.renderSettings().pickingSettings().setFaceOrientationPickingMode(
            PyQt6.Qt3DRender.QPickingSettings.FaceOrientationPickingMode.FrontAndBackFace)
        self.view.renderSettings().pickingSettings().setWorldSpaceTolerance(0.0001)
        self.picker.clicked.connect(self.clicked)

        self.setupCamera(self.entityModel['root_qt3d'])
        self.createScene()

    def clicked(self, pickEntity):
        """
        """
        for key, value in self.entityModel.items():
            if value == pickEntity.entity():
                self.app.material.emit(pickEntity.entity(), key)

    def initConfig(self):
        """
        """
        if 'simulatorW' not in self.app.config:
            self.app.config['simulatorW'] = {}
        config = self.app.config['simulatorW']

        self.positionWindow(config)
        self.ui.domeTransparent.setChecked(config.get('domeTransparent', False))
        self.ui.showPointer.setChecked(config.get('showPointer', False))
        self.ui.showLaser.setChecked(config.get('showLaser', False))
        self.ui.showBuildPoints.setChecked(config.get('showBuildPoints', False))
        self.ui.showNumbers.setChecked(config.get('showNumbers', False))
        self.ui.showSlewPath.setChecked(config.get('showSlewPath', False))
        self.ui.showHorizon.setChecked(config.get('showHorizon', False))

    def storeConfig(self):
        """
        """
        config = self.app.config
        if 'simulatorW' not in config:
            config['simulatorW'] = {}
        else:
            config['simulatorW'].clear()
        config = config['simulatorW']

        config['winPosX'] = max(self.pos().x(), 0)
        config['winPosY'] = max(self.pos().y(), 0)
        config['height'] = self.height()
        config['width'] = self.width()
        pos = self.camera.position()
        config['cameraPositionX'] = pos.x()
        config['cameraPositionY'] = pos.y()
        config['cameraPositionZ'] = pos.z()
        config['domeTransparent'] = self.ui.domeTransparent.isChecked()
        config['showPointer'] = self.ui.showPointer.isChecked()
        config['showLaser'] = self.ui.showLaser.isChecked()
        config['showBuildPoints'] = self.ui.showBuildPoints.isChecked()
        config['showNumbers'] = self.ui.showNumbers.isChecked()
        config['showSlewPath'] = self.ui.showSlewPath.isChecked()
        config['showHorizon'] = self.ui.showHorizon.isChecked()

    def closeEvent(self, closeEvent):
        """
        :param closeEvent:
        :return:
        """
        self.entityModel.clear()
        self.materialWindow.storeConfig()
        self.materialWindow.close()
        self.storeConfig()
        super().closeEvent(closeEvent)

    def showWindow(self):
        """
        """
        self.ui.topView.clicked.connect(self.topView)
        self.ui.topEastView.clicked.connect(self.topEastView)
        self.ui.topWestView.clicked.connect(self.topWestView)
        self.ui.eastView.clicked.connect(self.eastView)
        self.ui.westView.clicked.connect(self.westView)
        self.camera.positionChanged.connect(self.limitPositionZ)
        self.app.colorChange.connect(self.colorChange)
        self.show()

    def setupCamera(self, parentEntity):
        """
        :param parentEntity:
        :return:
        """
        self.camera = self.view.camera()
        self.camera.lens().setPerspectiveProjection(60.0, 16.0 / 9.0, 0.1, 10000.0)
        self.camera.setViewCenter(QVector3D(0.0, 1.5, 0.0))
        self.camera.setPosition(QVector3D(5.0, 15.0, 3.0))
        self.camera.setUpVector(QVector3D(0.0, 1.0, 0.0))
        self.cameraController = QOrbitCameraController(parentEntity)
        self.cameraController.setCamera(self.camera)
        self.cameraController.setLinearSpeed(5.0)
        self.cameraController.setLookSpeed(90)

    def colorChange(self):
        """
        We change the color of the background and the style of the window but
        not for the 3D scene itself during runtime.
        """
        self.setStyleSheet(self.mw4Style)
        self.view.defaultFrameGraph().setClearColor(QColor(self.M_BACK))

    def limitPositionZ(self):
        """
        Here we limit the position of the camera to the z=0 plane. This helps
        to keep the camera from going below the horizon and looking up into the
        sky.
        """
        pos = self.camera.position()
        if pos[1] < 0:
            z = 0
        else:
            z = pos[1]
        posNew = QVector3D(pos[0], z, pos[2])
        self.camera.setPosition(posNew)

    def topView(self):
        """
        The position vector in not 0,0,0 as the precision leads to a black
        screen.
        """
        self.changeStyleDynamic(self.ui.telescopeView, 'running', False)
        self.camera.setViewCenter(QVector3D(0.0, 1.5, 0.0))
        self.camera.setPosition(QVector3D(0.001, 5.0, 0.001))
        self.camera.setUpVector(QVector3D(0.0, 1.0, 0.0))

    def topEastView(self):
        """
        """
        self.changeStyleDynamic(self.ui.telescopeView, 'running', False)
        self.camera.setViewCenter(QVector3D(0.1, 1.5, 0.1))
        self.camera.setPosition(QVector3D(5.0, 5.0, 0.0))
        self.camera.setUpVector(QVector3D(0.0, 1.0, 0.0))

    def topWestView(self):
        """
        """
        self.changeStyleDynamic(self.ui.telescopeView, 'running', False)
        self.camera.setViewCenter(QVector3D(0.0, 1.5, 0.0))
        self.camera.setPosition(QVector3D(-5.0, 5.0, 0.0))
        self.camera.setUpVector(QVector3D(0.0, 1.0, 0.0))

    def eastView(self):
        """
        """
        self.changeStyleDynamic(self.ui.telescopeView, 'running', False)
        self.camera.setViewCenter(QVector3D(0.0, 1.5, 0.0))
        self.camera.setPosition(QVector3D(5.0, 1.5, 0.0))
        self.camera.setUpVector(QVector3D(0.0, 1.0, 0.0))

    def westView(self):
        """
        """
        self.changeStyleDynamic(self.ui.telescopeView, 'running', False)
        self.camera.setViewCenter(QVector3D(0.0, 1.5, 0.0))
        self.camera.setPosition(QVector3D(-5.0, 1.5, 0.0))
        self.camera.setUpVector(QVector3D(0.0, 1.0, 0.0))

    def setupReference(self):
        """
        Coordinate Systems:
        - fusion360 (x is north, y is west, z is up), scale in mm
        - Qt3D (x is east, y is up, -z is north), scale in m

        First transformation is from fusion360 to Qt3D.
        From there on we are in the Qt3D coordinate system.

        'ref_fusion_m' is the fusion360 coordinate system, please be aware that
        rotations around the z axis for azimuth is clockwise and not
        counterclockwise as a right-handed coordinate system would propose.

        for the sake of simplifying there is another reference, which only has
        the corrections in coordinates and not for scaling, this is called
        'ref_fusion'
        """
        model = {
            'ref_fusion': {
                'parent': 'root_qt3d',
                'rot': [-90, 90, 0],
            },
            'ref_fusion_m': {
                'parent': 'ref_fusion',
                'scale': [0.001, 0.001, 0.001],
            },
        }
        linkModel(model, self.entityModel)

    def createScene(self):
        """
        SetupScene initially builds all 3d models and collects them to Qt3D
        scene graph. The scene graph is stored parallel in the dict
        'entityModel'. The dict is used to link the models please look
        closely which references are used.
        """
        self.setupReference()
        self.light.create()
        self.telescope.create()
        self.laser.create()
        self.pointer.create()
        self.world.create()
        self.horizon.create()
        self.dome.create()
        self.buildPoints.create()
