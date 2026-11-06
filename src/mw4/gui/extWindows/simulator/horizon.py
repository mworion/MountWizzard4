# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import numpy as np
from mw4.base.appProtocol import HasBuildPoints
from mw4.gui.extWindows.simulator.materials import Materials
from PySide6.Qt3DCore import Qt3DCore
from PySide6.Qt3DExtras import Qt3DExtras
from PySide6.QtCore import QObject, Slot
from PySide6.QtGui import QVector3D
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mw4.gui.extWindows.simulator.simulatorW import SimulatorWindow


class SimulatorHorizon(QObject):
    WALL_RADIUS = 4
    WALL_SPACE = 5

    def __init__(self, parent: "SimulatorWindow", app: HasBuildPoints) -> None:
        super().__init__(parent)
        self.parentWindow = parent
        self.app = app
        self.parentWindow.ui.showHorizon.checkStateChanged.connect(self.showEnable)

    @Slot()
    def showEnable(self) -> None:
        isVisible = self.parentWindow.ui.showHorizon.isChecked()
        node = self.parentWindow.entityModel.get("horizonRoot")
        if node:
            node["entity"].setEnabled(isVisible)

    def clear(self) -> None:
        node = self.parentWindow.entityModel.get("horizonRoot")
        if not node:
            return

        node["entity"].setParent(None)
        del self.parentWindow.entityModel["horizonRoot"]["entity"]
        del self.parentWindow.entityModel["horizonRoot"]

    def createWall(self, parentEntity, alt, az) -> Qt3DCore.QEntity:
        e1 = Qt3DCore.QEntity()
        e1.setParent(parentEntity)
        trans1 = Qt3DCore.QTransform()
        trans1.setRotationZ(-az)
        e1.addComponent(trans1)

        e2 = Qt3DCore.QEntity()
        e2.setParent(e1)
        trans2 = Qt3DCore.QTransform()
        trans2.setTranslation(QVector3D(self.WALL_RADIUS, 0, 0))
        e2.addComponent(trans2)

        e3 = Qt3DCore.QEntity()
        e3.setParent(e2)
        height = self.WALL_RADIUS * np.tan(np.radians(alt)) + 1.35
        mesh = Qt3DExtras.QCuboidMesh()
        mesh.setXExtent(0.01)
        mesh.setYExtent(self.WALL_RADIUS * np.tan(np.radians(self.WALL_SPACE)))
        mesh.setZExtent(height)
        e3.addComponent(mesh)
        trans3 = Qt3DCore.QTransform()
        trans3.setTranslation(QVector3D(0, 0, height / 2))
        e3.addComponent(trans3)
        e3.addComponent(Materials().horizon)
        return e3

    def create(self) -> None:
        if not self.app.buildPoint.horizonP:
            return

        horizonAz = np.linspace(0, 360 - self.WALL_SPACE, int(360 / self.WALL_SPACE))
        alt = [x[0] for x in self.app.buildPoint.horizonP]
        az = [x[1] for x in self.app.buildPoint.horizonP]
        horizonAlt = np.interp(horizonAz, az, alt)

        self.clear()
        horizonEntity = Qt3DCore.QEntity()
        parent = self.parentWindow.entityModel["ref_fusion"]["entity"]
        horizonEntity.setParent(parent)
        self.parentWindow.entityModel["horizonRoot"] = {"entity": horizonEntity}

        for alt, az in zip(horizonAlt, horizonAz, strict=True):
            self.createWall(horizonEntity, alt, az)
        self.showEnable()
