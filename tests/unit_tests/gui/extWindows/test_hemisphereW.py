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
# GUI with PySide for python
#
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import pytest
import os
import shutil
from pathlib import Path

# external packages
from PySide6.QtCore import QPointF
from PySide6.QtGui import QCloseEvent
from skyfield.api import Angle, wgs84
import numpy as np
import pyqtgraph as pg

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.utilities.toolsQtWidget import MWidget
from gui.utilities.slewInterface import SlewInterface
from gui.extWindows.hemisphereW import HemisphereWindow
from mountcontrol.setting import Setting
from gui.utilities.gCustomViewBox import CustomViewBox


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    shutil.copy("tests/testData/terrain.jpg", "tests/workDir/config/terrain.jpg")
    func = HemisphereWindow(app=App())
    yield func
    func.app.threadPool.waitForDone(1000)


def test_initConfig_1(function):
    with mock.patch.object(os.path, "isfile", return_value=False):
        function.initConfig()


def test_initConfig_2(function):
    function.app.config["hemisphereW"]["winPosX"] = 10000
    function.app.config["hemisphereW"]["winPosY"] = 10000
    with mock.patch.object(os.path, "isfile", return_value=False):
        function.initConfig()


def test_initConfig_3(function):
    function.app.config["hemisphereW"] = {}
    function.app.config["hemisphereW"]["winPosX"] = 100
    function.app.config["hemisphereW"]["winPosY"] = 100
    with mock.patch.object(os.path, "isfile", return_value=False):
        function.initConfig()


def test_initConfig_4(function):
    shutil.copy("tests/testData/terrain.jpg", "tests/workDir/config/terrain.jpg")
    function.app.config["hemisphereW"] = {}
    function.app.config["hemisphereW"]["winPosX"] = 100
    function.app.config["hemisphereW"]["winPosY"] = 100
    function.initConfig()


def test_storeConfig_1(function):
    function.app.config = {}
    function.storeConfig()


def test_setIcons(function):
    function.setIcons()


def test_enableTabsMovable(function):
    function.enableTabsMovable(True)


def test_closeEvent_1(function):
    with mock.patch.object(function, "drawHemisphereTab"):
        with mock.patch.object(function, "show"):
            with mock.patch.object(MWidget, "closeEvent"):
                function.showWindow()
                function.closeEvent(QCloseEvent)


def test_showWindow_1(function):
    with mock.patch.object(function, "drawHemisphereTab"):
        with mock.patch.object(function, "show"):
            function.showWindow()


def test_mouseMoved_1(function):
    with mock.patch.object(
        function.ui.hemisphere.p[0].getViewBox(), "posInViewRange", return_value=False
    ):
        function.mouseMoved(pos=QPointF(1, 1))


def test_mouseMoved_2(function):
    with mock.patch.object(
        function.ui.hemisphere.p[0].getViewBox(), "posInViewRange", return_value=True
    ):
        function.mouseMoved(pos=QPointF(0.5, 0.5))


def test_colorChange(function):
    with mock.patch.object(function, "drawHemisphereTab"):
        function.colorChange()


def test_enableOperationModeChange_1(function):
    function.enableOperationModeChange(True)


def test_setOperationModeHem_1(function):
    function.ui.editModeHem.setChecked(True)
    with mock.patch.object(function, "drawModelPoints"):
        with mock.patch.object(function, "drawHemisphereTab"):
            function.setOperationModeHem()


def test_setOperationModeHem_2(function):
    function.ui.alignmentModeHem.setChecked(True)
    with mock.patch.object(function, "drawModelPoints"):
        with mock.patch.object(function, "drawHemisphereTab"):
            function.setOperationModeHem()


def test_calculateRelevance_0(function):
    function.app.mount.obsSite.location = None
    val = function.calculateRelevance(40, 180)
    assert round(val, 3) == 0.845


def test_calculateRelevance_1(function):
    function.app.mount.obsSite.location = wgs84.latlon(
        longitude_degrees=0, latitude_degrees=45
    )
    val = function.calculateRelevance(40, 180)
    assert round(val, 3) == 0.845


def test_calculateRelevance_2(function):
    function.app.mount.obsSite.location = wgs84.latlon(
        longitude_degrees=0, latitude_degrees=45
    )
    val = function.calculateRelevance(0, 0)
    assert val == 0


def test_calculateRelevance_3(function):
    function.app.mount.obsSite.location = wgs84.latlon(
        longitude_degrees=0, latitude_degrees=45
    )
    val = function.calculateRelevance(30, 180)
    assert val > 0


def test_calculateRelevance_4(function):
    function.app.mount.obsSite.location = wgs84.latlon(
        longitude_degrees=0, latitude_degrees=45
    )
    val = function.calculateRelevance(40, 10)
    assert val == 0


def test_calculateRelevance_5(function):
    function.app.mount.obsSite.location = wgs84.latlon(
        longitude_degrees=0, latitude_degrees=-45
    )
    val = function.calculateRelevance(40, 10)
    assert val > 0


def test_selectFontParam_1(function):
    function.colorSet = 0
    col, size = function.selectFontParam(0)
    assert size == 8


def test_selectFontParam_2(function):
    function.colorSet = 0
    col, size = function.selectFontParam(1)
    assert size == 13


def test_updateOnChangedParams_0(function):
    sett = Setting()
    sett.meridianLimitSlew = 0
    sett.meridianLimitTrack = 0
    sett.horizonLimitHigh = 0
    sett.horizonLimitLow = 0

    function.meridianSlew = 0
    function.meridianTrack = 0
    function.horizonLimitHigh = 0
    function.horizonLimitLow = 0
    suc = function.updateOnChangedParams(sett)
    assert not suc


def test_updateOnChangedParams_1(function):
    sett = Setting()
    sett.meridianLimitSlew = 0
    sett.meridianLimitTrack = 0
    sett.horizonLimitHigh = 0
    sett.horizonLimitLow = 1

    function.meridianSlew = 0
    function.meridianTrack = 0
    function.horizonLimitHigh = 0
    function.horizonLimitLow = 0
    with mock.patch.object(function, "drawHemisphereTab"):
        suc = function.updateOnChangedParams(sett)
        assert suc


def test_updateOnChangedParams_2(function):
    sett = Setting()
    sett.meridianLimitSlew = 0
    sett.meridianLimitTrack = 0
    sett.horizonLimitHigh = 1
    sett.horizonLimitLow = 0

    function.meridianSlew = 0
    function.meridianTrack = 0
    function.horizonLimitHigh = 0
    function.horizonLimitLow = 0

    with mock.patch.object(function, "drawHemisphereTab"):
        suc = function.updateOnChangedParams(sett)
        assert suc


def test_updateOnChangedParams_3(function):
    sett = Setting()
    sett.meridianLimitSlew = 0
    sett.meridianLimitTrack = 1
    sett.horizonLimitHigh = 0
    sett.horizonLimitLow = 0

    function.meridianSlew = 0
    function.meridianTrack = 0
    function.horizonLimitHigh = 0
    function.horizonLimitLow = 0

    with mock.patch.object(function, "drawHemisphereTab"):
        suc = function.updateOnChangedParams(sett)
        assert suc


def test_updateOnChangedParams_4(function):
    sett = Setting()
    sett.meridianLimitSlew = 1
    sett.meridianLimitTrack = 0
    sett.horizonLimitHigh = 0
    sett.horizonLimitLow = 0

    function.meridianSlew = 0
    function.meridianTrack = 0
    function.horizonLimitHigh = 0
    function.horizonLimitLow = 0

    with mock.patch.object(function, "drawHemisphereTab"):
        suc = function.updateOnChangedParams(sett)
        assert suc


def test_preparePlotItem(function):
    pd = pg.PlotItem()
    function.preparePlotItem(pd)


def test_preparePolarItem_1(function):
    pd = pg.PlotItem()
    function.ui.showPolar.setChecked(False)
    suc = function.preparePolarItem(pd)
    assert not suc


def test_preparePolarItem_2(function):
    pd = pg.PlotItem()
    function.ui.showPolar.setChecked(True)
    suc = function.preparePolarItem(pd)
    assert suc


def test_prepareHemisphere(function):
    function.prepareHemisphere()


def test_drawCelestialEquator_1(function):
    with mock.patch.object(
        function.app.data, "generateCelestialEquator", return_value=None
    ):
        suc = function.drawCelestialEquator()
        assert not suc


def test_drawCelestialEquator_2(function):
    with mock.patch.object(
        function.app.data, "generateCelestialEquator", return_value=[(1, 1)]
    ):
        suc = function.drawCelestialEquator()
        assert suc


def test_drawHorizonOnHem(function):
    function.drawHorizonOnHem()


def test_drawTerrainMask_1(function):
    pd = pg.PlotItem()
    function.imageTerrain = None
    suc = function.drawTerrainMask(pd)
    assert not suc


def test_drawTerrainMask_2(function):
    pd = pg.PlotItem()
    function.imageTerrain = np.ones((100, 100), dtype=np.uint8)
    function.drawTerrainMask(pd)


def test_drawMeridianLimits_1(function):
    function.app.mount.setting.meridianLimitSlew = None
    function.app.mount.setting.meridianLimitTrack = None
    function.drawMeridianLimits()


def test_drawMeridianLimits2(function):
    function.app.mount.setting.meridianLimitSlew = 10
    function.app.mount.setting.meridianLimitTrack = 10
    function.drawMeridianLimits()


def test_staticHorizonLimits_1(function):
    function.app.mount.setting.horizonLimitHigh = None
    function.app.mount.setting.horizonLimitLow = None
    function.drawHorizonLimits()


def test_staticHorizonLimits_2(function):
    function.app.mount.setting.horizonLimitHigh = 90
    function.app.mount.setting.horizonLimitLow = 10
    function.drawHorizonLimits()


def test_setupAlignmentStars(function):
    function.app.data.hip = ["test"]
    function.setupAlignmentStars()


def test_drawAlignmentStars_1(function):
    function.ui.showAlignStar.setChecked(False)
    function.drawAlignmentStars()


def test_drawAlignmentStars_2(function):
    function.ui.showAlignStar.setChecked(True)
    function.alignmentStars = None
    function.drawAlignmentStars()


def test_drawAlignmentStars_3(function):
    function.alignmentStarsText = []
    function.alignmentStarsText.append(pg.TextItem())
    function.ui.showAlignStar.setChecked(True)
    function.alignmentStars = pg.ScatterPlotItem()
    function.drawAlignmentStars()


def test_drawAlignmentStars_4(function):
    function.alignmentStarsText = []
    function.alignmentStarsText.append(pg.TextItem())
    function.ui.showAlignStar.setChecked(True)
    function.ui.alignmentModeHem.setChecked(True)
    function.alignmentStars = pg.ScatterPlotItem()
    function.drawAlignmentStars()


def test_drawModelPoints_1(function):
    function.app.data.buildP = None
    function.drawModelPoints()


def test_drawModelPoints_2(function):
    function.modelPoints = pg.PlotDataItem(x=[1, 2], y=[1, 2], symbol="o")
    function.app.data.buildP = [(1, 1, True), (2, 2, False)]
    function.drawModelPoints()


def test_drawModelText_1(function):
    function.app.data.buildP = None
    function.drawModelText()


def test_drawModelText_2(function):
    function.modelPoints = pg.PlotDataItem(x=[1, 2], y=[1, 2], symbol="o")
    function.app.data.buildP = [(1, 1, True), (2, 2, False)]
    function.ui.editModeHem.setChecked(True)
    function.modelPointsText.append(pg.TextItem())
    function.drawModelText()


def test_drawModelText_3(function):
    function.modelPoints = pg.PlotDataItem(x=[1, 2], y=[1, 2], symbol="o")
    function.app.data.buildP = [(1, 1, True), (2, 2, False)]
    function.ui.normalModeHem.setChecked(True)
    function.drawModelText()


def test_updateDataModel(function):
    with mock.patch.object(function, "drawModelPoints"):
        with mock.patch.object(function, "drawModelText"):
            function.updateDataModel([1, 2], [1, 2])


def test_setupModel_1(function):
    with mock.patch.object(function, "drawModelPoints"):
        with mock.patch.object(function, "drawModelText"):
            function.ui.editModeHem.setChecked(True)
            function.ui.showSlewPath.setChecked(True)
            function.setupModel()


def test_setupModel_2(function):
    with mock.patch.object(function, "drawModelPoints"):
        with mock.patch.object(function, "drawModelText"):
            function.ui.normalModeHem.setChecked(True)
            function.ui.showSlewPath.setChecked(False)
            function.setupModel()


def test_setupPointerHem(function):
    function.setupPointerHem()


def test_drawPointerHem_1(function):
    function.app.mount.obsSite.Az = None
    function.app.mount.obsSite.Alt = None
    function.setupPointerHem()
    suc = function.drawPointerHem()
    assert not suc


def test_drawPointerHem_2(function):
    function.app.mount.obsSite.Az = Angle(degrees=10)
    function.app.mount.obsSite.Alt = Angle(degrees=10)
    function.setupPointerHem()
    suc = function.drawPointerHem()
    assert suc


def test_setupDome(function):
    function.setupDome()


def test_drawDome_1(function):
    function.pointerDome = pg.QtWidgets.QGraphicsRectItem(165, 1, 30, 88)
    suc = function.drawDome("test")
    assert not suc


def test_drawDome_2(function):
    function.pointerDome = pg.QtWidgets.QGraphicsRectItem(165, 1, 30, 88)
    suc = function.drawDome(azimuth=100)
    assert suc


def test_getMountModelData_1(function):
    val = function.getMountModelData()
    assert val[0] is None
    assert val[1] is None
    assert val[2] is None


def test_getMountModelData_2(function):
    class Star:
        alt = Angle(degrees=10)
        az = Angle(degrees=20)
        errorRMS = 5

    function.app.mount.model.starList = [Star()]
    val = function.getMountModelData()
    assert val[0][0] == 20
    assert val[1][0] == 10
    assert val[2][0] == 5


def test_drawModelIsoCurve_1(function):
    with mock.patch.object(
        function, "getMountModelData", return_value=(None, None, None)
    ):
        suc = function.drawModelIsoCurve()
        assert not suc


def test_drawModelIsoCurve_2(function):
    val = np.array([1])
    data = (val, val, val)
    with mock.patch.object(function, "getMountModelData", return_value=data):
        with mock.patch.object(function.ui.hemisphere, "addIsoItem", return_value=True):
            function.drawModelIsoCurve()


def test_drawHemisphereTab_1(function):
    function.ui.showIsoModel.setChecked(True)
    function.ui.showCelestial.setChecked(True)
    function.ui.showTerrain.setChecked(True)
    function.ui.showMountLimits.setChecked(True)
    function.ui.showHorizon.setChecked(True)
    function.app.deviceStat["mount"] = True
    with mock.patch.object(function, "drawCelestialEquator"):
        with mock.patch.object(function, "drawTerrainMask"):
            with mock.patch.object(function, "drawMeridianLimits"):
                with mock.patch.object(function, "drawHorizonLimits"):
                    with mock.patch.object(function, "drawModelIsoCurve"):
                        with mock.patch.object(function, "drawHorizonOnHem"):
                            function.drawHemisphereTab()


def test_slewDirect_1(function):
    with mock.patch.object(function, "messageDialog", return_value=False):
        function.slewDirect(QPointF(1, 1))


def test_slewDirect_2(function):
    with mock.patch.object(function, "messageDialog", return_value=True):
        with mock.patch.object(SlewInterface, "slewTargetAltAz", return_value=False):
            function.slewDirect(QPointF(1, 1))


def test_slewDirect_3(function):
    with mock.patch.object(function, "messageDialog", return_value=True):
        with mock.patch.object(SlewInterface, "slewTargetAltAz", return_value=True):
            function.slewDirect(QPointF(1, 1))


def test_slewStar_1(function):
    function.alignmentStars = pg.ScatterPlotItem()
    with mock.patch.object(function.alignmentStars, "pointsAt", return_value=[]):
        function.slewStar(QPointF(1, 1))


def test_slewStar_3(function):
    class Spot:
        @staticmethod
        def index():
            return 0

    function.app.hipparcos.name = ["test"]
    function.app.mount.model.numberStars = 5
    function.alignmentStars = pg.ScatterPlotItem(x=[0, 1, 2], y=[0, 1, 2])
    with mock.patch.object(function.alignmentStars, "pointsAt", return_value=[Spot()]):
        with mock.patch.object(function, "messageDialog", return_value=0):
            with mock.patch.object(
                function.app.hipparcos, "getAlignStarRaDecFromName", return_value=(0, 0)
            ):
                function.slewStar(QPointF(1, 1))


def test_slewStar_4(function):
    class Spot:
        @staticmethod
        def index():
            return 0

    function.app.hipparcos.name = ["test"]
    function.app.mount.model.numberStars = 5
    function.alignmentStars = pg.ScatterPlotItem(x=[0, 1, 2], y=[0, 1, 2])
    with mock.patch.object(function.alignmentStars, "pointsAt", return_value=[Spot()]):
        with mock.patch.object(function, "messageDialog", return_value=1):
            with mock.patch.object(
                function.app.hipparcos, "getAlignStarRaDecFromName", return_value=(0, 0)
            ):
                with mock.patch.object(
                    SlewInterface, "slewTargetRaDec", return_value=False
                ):
                    function.slewStar(QPointF(1, 1))


def test_slewStar_5(function):
    class Spot:
        @staticmethod
        def index():
            return 0

    function.app.hipparcos.name = ["test"]
    function.app.mount.model.numberStars = 5
    function.alignmentStars = pg.ScatterPlotItem(x=[0, 1, 2], y=[0, 1, 2])
    with mock.patch.object(function.alignmentStars, "pointsAt", return_value=[Spot()]):
        with mock.patch.object(function, "messageDialog", return_value=2):
            with mock.patch.object(
                function.app.hipparcos, "getAlignStarRaDecFromName", return_value=(0, 0)
            ):
                with mock.patch.object(
                    SlewInterface, "slewTargetRaDec", return_value=True
                ):
                    function.slewStar(QPointF(1, 1))


def test_mouseDoubleClick_1(function):
    function.ui.alignmentModeHem.setChecked(True)
    function.ui.normalModeHem.setChecked(False)
    with mock.patch.object(function, "slewStar"):
        function.mouseDoubleClick(1, 2)


def test_mouseDoubleClick_2(function):
    function.ui.alignmentModeHem.setChecked(False)
    function.ui.normalModeHem.setChecked(True)
    with mock.patch.object(function, "slewDirect"):
        function.mouseDoubleClick(1, 2)


def test_mouseMovedHorizon_1(function):
    with mock.patch.object(function, "mouseMoved"):
        function.mouseMovedHorizon("test")


def test_setTerrainFile_1(function):
    function.setTerrainFile("test")
    assert function.imageTerrain is None


def test_setTerrainFile_2(function):
    function.setTerrainFile("terrain.jpg")
    assert function.imageTerrain is not None


def test_loadTerrainFile_1(function):
    class Test:
        @staticmethod
        def drawHemisphere():
            return

    function.app.uiWindows = {"showHemisphereW": {"classObj": Test()}}
    with mock.patch.object(function, "openFile", return_value=Path("terrain.jpg")):
        with mock.patch.object(function, "setTerrainFile", return_value=True):
            with mock.patch.object(Path, "is_file", return_value=True):
                with mock.patch.object(function, "drawHorizonTab"):
                    suc = function.loadTerrainFile()
                    assert suc


def test_loadTerrainFile_2(function):
    with mock.patch.object(function, "openFile", return_value=(Path(""))):
        with mock.patch.object(Path, "is_file", return_value=False):
            suc = function.loadTerrainFile()
            assert not suc


def test_loadTerrainFile_3(function):
    with mock.patch.object(function, "openFile", return_value=Path("terrain.jpg")):
        with mock.patch.object(function, "setTerrainFile", return_value=False):
            with mock.patch.object(Path, "is_file", return_value=True):
                with mock.patch.object(function, "drawHorizonTab"):
                    suc = function.loadTerrainFile()
                    assert suc


def test_clearTerrainFile(function):
    with mock.patch.object(function, "setTerrainFile"):
        with mock.patch.object(function, "drawHorizonTab"):
            function.clearTerrainFile()


def test_loadHorizonMask_1(function):
    with mock.patch.object(function, "openFile", return_value=Path("test.test")):
        with mock.patch.object(Path, "is_file", return_value=False):
            suc = function.loadHorizonMask()
            assert not suc


def test_loadHorizonMask_2(function):
    with mock.patch.object(function, "openFile", return_value=Path("test.bpts")):
        with mock.patch.object(function.app.data, "loadHorizonP", return_value=False):
            with mock.patch.object(Path, "is_file", return_value=True):
                with mock.patch.object(function, "drawHorizonTab"):
                    suc = function.loadHorizonMask()
                    assert suc


def test_loadHorizonMask_3(function):
    with mock.patch.object(function, "openFile", return_value=Path("test.bpts")):
        with mock.patch.object(function.app.data, "loadHorizonP", return_value=True):
            with mock.patch.object(Path, "is_file", return_value=True):
                with mock.patch.object(function, "drawHorizonTab"):
                    suc = function.loadHorizonMask()
                    assert suc


def test_saveHorizonMask_1(function):
    function.ui.horizonMaskFileName.setText("test")
    with mock.patch.object(function, "openFile", return_value=Path("test.bpts")):
        with mock.patch.object(function.app.data, "saveHorizonP", return_value=True):
            suc = function.saveHorizonMask()
            assert suc


def test_saveHorizonMaskFile_2(function):
    function.ui.horizonMaskFileName.setText("")
    suc = function.saveHorizonMask()
    assert not suc


def test_saveHorizonMaskFile_3(function):
    function.ui.horizonMaskFileName.setText("test")
    with mock.patch.object(
        function, "saveFile", return_value=("build", "test", "bpts")
    ):
        with mock.patch.object(function.app.data, "saveHorizonP", return_value=False):
            suc = function.saveHorizonMask()
            assert suc


def test_saveHorizonMaskFileAs_1(function):
    with mock.patch.object(
        function, "saveFile", return_value=("build", "test", "bpts")
    ):
        with mock.patch.object(function.app.data, "saveHorizonP", return_value=True):
            suc = function.saveHorizonMaskAs()
            assert suc


def test_saveHorizonMaskFileAs_2(function):
    with mock.patch.object(function, "saveFile", return_value=("", "", "")):
        suc = function.saveHorizonMaskAs()
        assert not suc


def test_saveHorizonMaskFileAs_3(function):
    with mock.patch.object(
        function, "saveFile", return_value=("build", "test", "bpts")
    ):
        with mock.patch.object(function.app.data, "saveHorizonP", return_value=False):
            suc = function.saveHorizonMaskAs()
            assert suc


def test_setOperationModeHor_1(function):
    function.ui.editModeHor.setChecked(True)
    function.setOperationModeHor()


def test_setOperationModeHor_2(function):
    function.ui.normalModeHor.setChecked(True)
    function.setOperationModeHor()


def test_updateDataHorizon(function):
    function.horizonPlot = pg.PlotDataItem()
    function.updateDataHorizon([1, 2], [1, 2])


def test_clearHorizonMask(function):
    function.clearHorizonMask()


def test_addActualPosition_1(function):
    function.app.mount.obsSite.Alt = None
    function.app.mount.obsSite.Az = None
    suc = function.addActualPosition()
    assert not suc


def test_addActualPosition_2(function):
    function.app.mount.obsSite.Alt = Angle(degrees=10)
    function.app.mount.obsSite.Az = Angle(degrees=20)
    with mock.patch.object(CustomViewBox, "getNearestPointIndex", return_value=1):
        with mock.patch.object(CustomViewBox, "addUpdate"):
            suc = function.addActualPosition()
            assert suc


def test_prepareHorizonView(function):
    with mock.patch.object(function, "preparePlotItem"):
        function.prepareHorizonView()


def test_drawHorizonView_1(function):
    function.horizonPlot = pg.PlotDataItem()
    suc = function.drawHorizonView()
    assert not suc


def test_drawHorizonView_2(function):
    function.app.data.horizonP = [(1, 1), (2, 2)]
    function.horizonPlot = pg.PlotDataItem(x=[1], y=[1])
    suc = function.drawHorizonView()
    assert suc


def test_setupPointerHor(function):
    function.prepareHorizonView()


def test_drawPointerHor_1(function):
    function.pointerHor = None
    suc = function.drawPointerHor()
    assert not suc


def test_drawPointerHor_2(function):
    function.pointerHor = pg.ScatterPlotItem()
    function.app.mount.obsSite.Alt = None
    suc = function.drawPointerHor()
    assert not suc


def test_drawPointerHor_3(function):
    function.pointerHor = pg.ScatterPlotItem()
    function.app.mount.obsSite.Alt = Angle(degrees=10)
    function.app.mount.obsSite.Az = Angle(degrees=20)
    suc = function.drawPointerHor()
    assert suc


def test_setupHorizonView_1(function):
    function.ui.editModeHor.setChecked(True)
    function.setupHorizonView()


def test_setupHorizonView_2(function):
    function.ui.editModeHor.setChecked(False)
    function.setupHorizonView()


def test_drawHorizonTab_1(function):
    function.ui.showTerrain.setChecked(True)
    function.ui.editModeHor.setChecked(True)
    function.drawHorizonTab()


def test_drawHorizonTab_2(function):
    function.ui.showTerrain.setChecked(False)
    function.ui.editModeHor.setChecked(False)
    function.drawHorizonTab()
