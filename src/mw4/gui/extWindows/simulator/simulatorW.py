############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# License APL2.0
#
###########################################################
import logging
from mw4.gui.extWindows.simulator.buildPoints import SimulatorBuildPoints
from mw4.gui.extWindows.simulator.dome import SimulatorDome
from mw4.gui.extWindows.simulator.horizon import SimulatorHorizon
from mw4.gui.extWindows.simulator.laser import SimulatorLaser
from mw4.gui.extWindows.simulator.light import SimulatorLight
from mw4.gui.extWindows.simulator.pointer import SimulatorPointer
from mw4.gui.extWindows.simulator.telescope import SimulatorTelescope
from mw4.gui.extWindows.simulator.tools import linkModel
from mw4.gui.extWindows.simulator.world import SimulatorWorld
from mw4.gui.utilities.qtHelpers import changeStyleDynamic
from mw4.gui.utilities.qtMain import MWidget
from mw4.gui.widgets import simulator_ui
from PySide6.Qt3DCore import Qt3DCore
from PySide6.Qt3DExtras import Qt3DExtras
from PySide6.QtGui import QColor, QVector3D
from PySide6.QtWidgets import QWidget
from typing import Any


class SimulatorWindow(MWidget):
    log = logging.getLogger("MW4")

    def __init__(self, app: Any, title: str) -> None:
        super().__init__()
        self.app = app
        self.ui = simulator_ui.Ui_SimulatorDialog()
        self.ui.setupUi(self.ws)
        self.setMinimumSize(self.FULL_WIDTH, self.FULL_HEIGHT)
        self.setWindowTitle("Simulation")
        self.world = SimulatorWorld(self, self.app)
        self.light = SimulatorLight(self, self.app)
        self.dome = SimulatorDome(self, self.app)
        self.telescope = SimulatorTelescope(self, self.app)
        self.laser = SimulatorLaser(self, self.app)
        self.pointer = SimulatorPointer(self, self.app)
        self.horizon = SimulatorHorizon(self, self.app)
        self.buildPoints = SimulatorBuildPoints(self, self.app)
        self.window3D = Qt3DExtras.Qt3DWindow()
        self.entityModel = {"root": {"entity": Qt3DCore.QEntity()}}
        self.window3D.setRootEntity(self.entityModel["root"]["entity"])
        self.entityModel["root"]["entity"].setObjectName("root")
        self.window3D.defaultFrameGraph().setClearColor(QColor(self.M_BACK))
        self.container = QWidget.createWindowContainer(self.window3D)
        self.ui.simulator.addWidget(self.container)
        self.camera = None
        self.cameraController = None
        self.setupCamera(self.entityModel["root"]["entity"])
        self.createScene()

    def initConfig(self) -> None:
        config = self.app.config.get("WindowSimulator", {})
        self.positionWindow(config)
        self.ui.domeTransparent.setChecked(config.get("domeTransparent", False))
        self.ui.showPointer.setChecked(config.get("showPointer", False))
        self.ui.showLaser.setChecked(config.get("showLaser", False))
        self.ui.showBuildPoints.setChecked(config.get("showBuildPoints", False))
        self.ui.showNumbers.setChecked(config.get("showNumbers", False))
        self.ui.showSlewPath.setChecked(config.get("showSlewPath", False))
        self.ui.showHorizon.setChecked(config.get("showHorizon", False))

    def storeConfig(self) -> None:
        configMain = self.app.config
        configMain["WindowSimulator"] = {}
        config = configMain["WindowSimulator"]

        config["winPosX"] = max(self.pos().x(), 0)
        config["winPosY"] = max(self.pos().y(), 0)
        config["height"] = self.height()
        config["width"] = self.width()
        pos = self.camera.position()
        config["cameraPositionX"] = pos.x()
        config["cameraPositionY"] = pos.y()
        config["cameraPositionZ"] = pos.z()
        config["domeTransparent"] = self.ui.domeTransparent.isChecked()
        config["showPointer"] = self.ui.showPointer.isChecked()
        config["showLaser"] = self.ui.showLaser.isChecked()
        config["showBuildPoints"] = self.ui.showBuildPoints.isChecked()
        config["showNumbers"] = self.ui.showNumbers.isChecked()
        config["showSlewPath"] = self.ui.showSlewPath.isChecked()
        config["showHorizon"] = self.ui.showHorizon.isChecked()

    def closeEvent(self, closeEvent) -> None:
        self.app.dReg.drivers["mount"]["class"].signals.pointDone.disconnect(
            self.buildPoints.updatePositions
        )
        self.app.dReg.drivers["mount"]["class"].signals.pointDone.disconnect(
            self.laser.updatePositions
        )
        self.app.dReg.drivers["mount"]["class"].signals.pointDone.disconnect(
            self.pointer.updatePositions
        )
        self.app.dReg.drivers["mount"]["class"].signals.pointDone.disconnect(
            self.telescope.updateRotation
        )
        self.entityModel.clear()
        self.storeConfig()
        super().closeEvent(closeEvent)

    def showWindow(self) -> None:
        self.ui.topView.clicked.connect(self.topView)
        self.ui.topEastView.clicked.connect(self.topEastView)
        self.ui.topWestView.clicked.connect(self.topWestView)
        self.ui.eastView.clicked.connect(self.eastView)
        self.ui.westView.clicked.connect(self.westView)
        self.app.colorChange.connect(self.colorChange)
        self.camera.positionChanged.connect(self.limitPositionZ)
        self.app.dReg.drivers["mount"]["class"].signals.pointDone.connect(
            self.buildPoints.updatePositions
        )
        self.app.dReg.drivers["mount"]["class"].signals.pointDone.connect(
            self.laser.updatePositions
        )
        self.app.dReg.drivers["mount"]["class"].signals.pointDone.connect(
            self.pointer.updatePositions
        )
        self.app.dReg.drivers["mount"]["class"].signals.pointDone.connect(
            self.telescope.updateRotation
        )
        self.show()

    def setupCamera(self, parentEntity) -> None:
        self.camera = self.window3D.camera()
        self.camera.lens().setPerspectiveProjection(60, 16 / 9, 0.1, 10000)
        self.camera.setViewCenter(QVector3D(0, 1, 0))
        self.camera.setPosition(QVector3D(3, 10, 3))
        self.camera.setUpVector(QVector3D(0, 1, 0))
        self.cameraController = Qt3DExtras.QOrbitCameraController(parentEntity)
        self.cameraController.setCamera(self.camera)
        self.cameraController.setLinearSpeed(5.0)
        self.cameraController.setLookSpeed(90)

    def colorChange(self) -> None:
        self.setStyleSheet(self.mw4Style)
        self.window3D.defaultFrameGraph().setClearColor(QColor(self.M_BACK))

    def limitPositionZ(self) -> None:
        """
        Here we limit the position of the camera to the z=0 plane. This helps
        to keep the camera from going below the horizon and looking up into the
        sky.
        """
        pos = self.camera.position()
        y = 0 if pos.y() < 0 else pos.y()
        posNew = QVector3D(pos.x(), y, pos.z())
        self.camera.setPosition(posNew)

    def topView(self) -> None:
        changeStyleDynamic(self.ui.telescopeView, "run", False)
        self.camera.setViewCenter(QVector3D(0.0, 1.5, 0.0))
        self.camera.setPosition(QVector3D(0.001, 5.0, 0.001))
        self.camera.setUpVector(QVector3D(0.0, 1.0, 0.0))

    def topEastView(self) -> None:
        changeStyleDynamic(self.ui.telescopeView, "run", False)
        self.camera.setViewCenter(QVector3D(0.1, 1.5, 0.1))
        self.camera.setPosition(QVector3D(5.0, 5.0, 0.0))
        self.camera.setUpVector(QVector3D(0.0, 1.0, 0.0))

    def topWestView(self) -> None:
        changeStyleDynamic(self.ui.telescopeView, "run", False)
        self.camera.setViewCenter(QVector3D(0.0, 1.5, 0.0))
        self.camera.setPosition(QVector3D(-5.0, 5.0, 0.0))
        self.camera.setUpVector(QVector3D(0.0, 1.0, 0.0))

    def eastView(self) -> None:
        changeStyleDynamic(self.ui.telescopeView, "run", False)
        self.camera.setViewCenter(QVector3D(0.0, 1.5, 0.0))
        self.camera.setPosition(QVector3D(5.0, 1.5, 0.0))
        self.camera.setUpVector(QVector3D(0.0, 1.0, 0.0))

    def westView(self) -> None:
        changeStyleDynamic(self.ui.telescopeView, "run", False)
        self.camera.setViewCenter(QVector3D(0.0, 1.5, 0.0))
        self.camera.setPosition(QVector3D(-5.0, 1.5, 0.0))
        self.camera.setUpVector(QVector3D(0.0, 1.0, 0.0))

    def createReference(self) -> None:
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
            "ref_fusion": {
                "parent": "root",
                "rot": [-90, 90, 0],
            },
            "ref_fusion_m": {
                "parent": "ref_fusion",
                "scale": [0.001, 0.001, 0.001],
            },
        }
        linkModel(model, self.entityModel)

    def createScene(self) -> None:
        self.createReference()
        self.horizon.create()
        self.dome.create()
        self.telescope.create()
        self.laser.create()
        self.pointer.create()
        self.buildPoints.create()
        self.light.create()
        self.world.create()
