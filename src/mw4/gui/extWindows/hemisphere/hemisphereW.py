############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages
import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QCursor, QGuiApplication

from mw4.gui.extWindows.hemisphere.hemisphereDraw import HemisphereDraw
from mw4.gui.extWindows.hemisphere.horizonDraw import HorizonDraw

# local import
from mw4.gui.utilities.toolsQtWidget import MWidget
from mw4.gui.widgets import hemisphere_ui


class HemisphereWindow(MWidget):
    """
    the hemisphere window class handles all interaction with model points
    show / edit etc. the z orders is aligned as follows:

    on the static plane we have (and set to the z order)
        - terrain image         -10
        - horizon               0
        - horizon limits        0
        - celestial path        0
        - meridian limit track  10
        - meridian limit slew   20
        - alignment stars       30
        - build points          40
        - checked build points  50
    """

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.msg = app.msg
        self.ui = hemisphere_ui.Ui_HemisphereDialog()
        self.ui.setupUi(self)
        self.horizonDraw = HorizonDraw(self)
        self.hemisphereDraw = HemisphereDraw(self)

    def initConfig(self) -> None:
        """ """
        config = self.app.config.get("hemisphereW", {})
        self.positionWindow(config)
        self.setTabAndIndex(self.ui.tabWidget, config, "orderMain")
        self.ui.showSlewPath.setChecked(config.get("showSlewPath", False))
        self.ui.showMountLimits.setChecked(config.get("showMountLimits", False))
        self.ui.showCelestial.setChecked(config.get("showCelestial", False))
        self.ui.showAlignStar.setChecked(config.get("showAlignStar", False))
        self.ui.showHorizon.setChecked(config.get("showHorizon", True))
        self.ui.showPolar.setChecked(config.get("showPolar", False))
        self.ui.showTerrain.setChecked(config.get("showTerrain", False))
        self.ui.showIsoModel.setChecked(config.get("showIsoModel", False))
        self.ui.tabWidget.setCurrentIndex(config.get("tabWidget", 0))
        self.ui.terrainAlpha.setValue(config.get("terrainAlpha", 0.35))
        self.ui.azimuthShift.setValue(config.get("azimuthShift", 0))
        self.ui.altitudeShift.setValue(config.get("altitudeShift", 0))
        self.app.tabsMovable.connect(self.enableTabsMovable)
        self.enableTabsMovable(self.app.config["mainW"].get("tabsMovable", False))

        self.horizonDraw.initConfig()
        self.hemisphereDraw.initConfig()

    def storeConfig(self) -> None:
        """ """
        configMain = self.app.config
        configMain["hemisphereW"] = {}
        config = configMain["hemisphereW"]

        config["winPosX"] = max(self.pos().x(), 0)
        config["winPosY"] = max(self.pos().y(), 0)
        config["height"] = self.height()
        config["width"] = self.width()
        self.getTabAndIndex(self.ui.tabWidget, config, "orderMain")
        config["showSlewPath"] = self.ui.showSlewPath.isChecked()
        config["showMountLimits"] = self.ui.showMountLimits.isChecked()
        config["showCelestial"] = self.ui.showCelestial.isChecked()
        config["showAlignStar"] = self.ui.showAlignStar.isChecked()
        config["showHorizon"] = self.ui.showHorizon.isChecked()
        config["showPolar"] = self.ui.showPolar.isChecked()
        config["showTerrain"] = self.ui.showTerrain.isChecked()
        config["showIsoModel"] = self.ui.showIsoModel.isChecked()
        config["tabWidget"] = self.ui.tabWidget.currentIndex()
        config["horizonMaskFileName"] = self.ui.horizonMaskFileName.text()
        config["terrainFileName"] = self.ui.terrainFileName.text()
        config["terrainAlpha"] = self.ui.terrainAlpha.value()
        config["azimuthShift"] = self.ui.azimuthShift.value()
        config["altitudeShift"] = self.ui.altitudeShift.value()

    def enableTabsMovable(self, isMovable: bool) -> None:
        """ """
        self.ui.tabWidget.setMovable(isMovable)

    def closeEvent(self, closeEvent) -> None:
        """ """
        self.ui.normalModeHem.setChecked(True)
        self.ui.normalModeHor.setChecked(True)
        self.storeConfig()
        self.hemisphereDraw.close()
        super().closeEvent(closeEvent)

    def showWindow(self) -> None:
        """ """
        self.app.colorChange.connect(self.colorChange)
        self.app.tabsMovable.connect(self.enableTabsMovable)
        self.hemisphereDraw.drawTab()
        self.horizonDraw.drawTab()
        self.setIcons()
        self.show()

    def setIcons(self) -> None:
        """ """
        self.wIcon(self.ui.loadTerrainFile, "load")
        self.wIcon(self.ui.clearTerrainFile, "trash")
        self.wIcon(self.ui.loadHorizonMask, "load")
        self.wIcon(self.ui.saveHorizonMask, "save")
        self.wIcon(self.ui.saveHorizonMaskAs, "save")
        self.wIcon(self.ui.clearHorizonMask, "trash")

    def mouseMoved(self, pos: QPointF) -> None:
        """ """
        viewBox = self.ui.hemisphere.p[0].getViewBox()
        mousePoint = viewBox.mapSceneToView(pos)

        if viewBox.posInViewRange(pos):
            self.ui.azimuth.setText(f"{mousePoint.x():3.1f}")
            self.ui.altitude.setText(f"{mousePoint.y():3.1f}")
            QGuiApplication.setOverrideCursor(QCursor(Qt.CursorShape.CrossCursor))
        else:
            self.ui.azimuth.setText("")
            self.ui.altitude.setText("")
            QGuiApplication.setOverrideCursor(QCursor(Qt.CursorShape.ArrowCursor))

    def colorChange(self) -> None:
        """ """
        self.setStyleSheet(self.mw4Style)
        self.ui.hemisphere.colorChange()
        self.ui.horizon.colorChange()
        self.hemisphereDraw.drawTab()
        self.horizonDraw.drawTab()
        self.setIcons()

    @staticmethod
    def preparePlotItem(plotItem) -> None:
        """ """
        plotItem.clear()
        plotItem.showAxes(True, showValues=True)
        plotItem.getViewBox().setMouseMode(pg.ViewBox().PanMode)
        xTicks = [(x, f"{x:0.0f}") for x in np.arange(30, 331, 30)]
        plotItem.getAxis("bottom").setTicks([xTicks])
        plotItem.getAxis("top").setTicks([xTicks])
        yTicks = [(x, f"{x:0.0f}") for x in np.arange(10, 90, 10)]
        plotItem.getAxis("left").setTicks([yTicks])
        plotItem.getAxis("right").setTicks([yTicks])
        plotItem.setLabel("bottom", "Azimuth [deg]")
        plotItem.setLabel("left", "Altitude [deg]")
        plotItem.setLimits(
            xMin=0,
            xMax=360,
            yMin=0,
            yMax=90,
            minXRange=120,
            maxXRange=360,
            minYRange=30,
            maxYRange=90,
        )
        plotItem.setXRange(0, 360)
        plotItem.setYRange(0, 90)
        plotItem.disableAutoRange()

    def preparePolarItem(self, plotItem) -> None:
        """ """
        plotItem.clear()
        showPolar = self.ui.showPolar.isChecked()
        if not showPolar:
            self.ui.hemisphere.ci.layout.setColumnStretchFactor(0, 17)
            self.ui.hemisphere.ci.layout.setColumnStretchFactor(1, 0)
            plotItem.setVisible(False)
            return

        plotItem.setVisible(True)
        self.ui.hemisphere.ci.layout.setColumnStretchFactor(0, 17)
        self.ui.hemisphere.ci.layout.setColumnStretchFactor(1, 10)
        plotItem.showAxes(False, showValues=False)
        plotItem.setMouseEnabled(x=False, y=False)
        plotItem.getViewBox().setMouseMode(pg.ViewBox().PanMode)
        plotItem.setXRange(-90, 90)
        plotItem.setYRange(-90, 90)
        plotItem.disableAutoRange()
        self.ui.hemisphere.setGrid(plotItem=plotItem, reverse=True)
        lat = self.app.mount.obsSite.location.latitude.degrees
        self.ui.hemisphere.plotLoc(lat, plotItem=plotItem)

    def redrawAll(self) -> None:
        """ """
        self.hemisphereDraw.drawTab()
        self.horizonDraw.drawTab()
