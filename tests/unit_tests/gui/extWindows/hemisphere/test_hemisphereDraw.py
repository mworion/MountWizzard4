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
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import os
import shutil
import unittest.mock as mock

import numpy as np
import pyqtgraph as pg
import pytest

# external packages
from PySide6.QtCore import QPointF
from skyfield.api import Angle, wgs84

from mw4.gui.extWindows.hemisphere.hemisphereDraw import HemisphereDraw
from mw4.gui.extWindows.hemisphere.hemisphereW import HemisphereWindow
from mw4.gui.utilities.slewInterface import SlewInterface
from mw4.mountcontrol.setting import Setting

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    shutil.copy("tests/testData/terrain.jpg", "tests/work/config/terrain.jpg")
    func = HemisphereDraw(parent=HemisphereWindow(app=App()))
    yield func
    func.app.threadPool.waitForDone(10000)


def test_initConfig_1(function):
    with mock.patch.object(os.path, "isfile", return_value=False):
        function.initConfig()


def test_initConfig_2(function):
    function.app.config["hemisphereW"] = {"winPosX": 10000}
    function.app.config["hemisphereW"] = {"winPosY": 10000}
    with mock.patch.object(os.path, "isfile", return_value=False):
        function.initConfig()


def test_initConfig_3(function):
    function.app.config["hemisphereW"] = {}
    function.app.config["hemisphereW"] = {"winPosX": 100}
    function.app.config["hemisphereW"] = {"winPosY": 100}
    with mock.patch.object(os.path, "isfile", return_value=False):
        function.initConfig()


def test_initConfig_4(function):
    shutil.copy("tests/testData/terrain.jpg", "tests/work/config/terrain.jpg")
    function.app.config["hemisphereW"] = {}
    function.app.config["hemisphereW"] = {"winPosX": 100}
    function.app.config["hemisphereW"] = {"winPosY": 100}
    function.initConfig()


def test_close_1(function):
    function.close()


def test_mouseMoved_1(function):
    with mock.patch.object(function.parent, "mouseMoved"):
        function.mouseMovedHemisphere(pos=QPointF(1, 1))


def test_enableOperationModeChange_1(function):
    function.enableOperationModeChange(True)


def test_setOperationMode_1(function):
    function.ui.editModeHem.setChecked(True)
    with mock.patch.object(function, "drawModelPoints"):
        with mock.patch.object(function, "drawTab"):
            function.setOperationMode()


def test_setOperationMode_2(function):
    function.ui.alignmentModeHem.setChecked(True)
    with mock.patch.object(function, "drawModelPoints"):
        with mock.patch.object(function, "drawTab"):
            function.setOperationMode()


def test_updateOnChangedParams_0(function):
    class Parent:
        host = None
    sett = Setting(parent=Parent())
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
    class Parent:
        host = None
    sett = Setting(parent=Parent())
    sett.meridianLimitSlew = 0
    sett.meridianLimitTrack = 0
    sett.horizonLimitHigh = 0
    sett.horizonLimitLow = 1

    function.meridianSlew = 0
    function.meridianTrack = 0
    function.horizonLimitHigh = 0
    function.horizonLimitLow = 0
    with mock.patch.object(function, "drawTab"):
        suc = function.updateOnChangedParams(sett)
        assert suc


def test_updateOnChangedParams_2(function):
    class Parent:
        host = None
    sett = Setting(parent=Parent())
    sett.meridianLimitSlew = 0
    sett.meridianLimitTrack = 0
    sett.horizonLimitHigh = 1
    sett.horizonLimitLow = 0

    function.meridianSlew = 0
    function.meridianTrack = 0
    function.horizonLimitHigh = 0
    function.horizonLimitLow = 0

    with mock.patch.object(function, "drawTab"):
        suc = function.updateOnChangedParams(sett)
        assert suc


def test_updateOnChangedParams_3(function):
    class Parent:
        host = None
    sett = Setting(parent=Parent())
    sett.meridianLimitSlew = 0
    sett.meridianLimitTrack = 1
    sett.horizonLimitHigh = 0
    sett.horizonLimitLow = 0

    function.meridianSlew = 0
    function.meridianTrack = 0
    function.horizonLimitHigh = 0
    function.horizonLimitLow = 0

    with mock.patch.object(function, "drawTab"):
        suc = function.updateOnChangedParams(sett)
        assert suc


def test_updateOnChangedParams_4(function):
    class Parent:
        host = None
    sett = Setting(parent=Parent())
    sett.meridianLimitSlew = 1
    sett.meridianLimitTrack = 0
    sett.horizonLimitHigh = 0
    sett.horizonLimitLow = 0

    function.meridianSlew = 0
    function.meridianTrack = 0
    function.horizonLimitHigh = 0
    function.horizonLimitLow = 0

    with mock.patch.object(function, "drawTab"):
        suc = function.updateOnChangedParams(sett)
        assert suc


def test_prepareView(function):
    function.prepareView()


def test_drawCelestialEquator_1(function):
    with mock.patch.object(function.app.data, "generateCelestialEquator", return_value=None):
        function.drawCelestialEquator()


def test_drawCelestialEquator_2(function):
    with mock.patch.object(
        function.app.data, "generateCelestialEquator", return_value=[(1, 1)]
    ):
        function.drawCelestialEquator()


def test_drawHorizon(function):
    function.drawHorizon()


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


def test_setupPointer(function):
    function.setupPointer()


def test_drawPointer_1(function):
    function.app.mount.obsSite.Az = None
    function.app.mount.obsSite.Alt = None
    function.setupPointer()
    function.drawPointer()


def test_drawPointer_2(function):
    function.app.mount.obsSite.Az = Angle(degrees=10)
    function.app.mount.obsSite.Alt = Angle(degrees=10)
    function.setupPointer()
    function.drawPointer()


def test_setupDome(function):
    function.setupDome()


def test_drawDome_1(function):
    function.pointerDome = pg.QtWidgets.QGraphicsRectItem(165, 1, 30, 88)
    function.drawDome("test")


def test_drawDome_2(function):
    function.pointerDome = pg.QtWidgets.QGraphicsRectItem(165, 1, 30, 88)
    function.drawDome(azimuth=100)


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
    with mock.patch.object(function, "getMountModelData", return_value=(None, None, None)):
        function.drawModelIsoCurve()


def test_drawModelIsoCurve_2(function):
    val = np.array([1])
    data = (val, val, val)
    with mock.patch.object(function, "getMountModelData", return_value=data):
        with mock.patch.object(function.ui.hemisphere, "addIsoItem", return_value=True):
            function.drawModelIsoCurve()


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
                with mock.patch.object(SlewInterface, "slewTargetRaDec", return_value=False):
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
                with mock.patch.object(SlewInterface, "slewTargetRaDec", return_value=True):
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


def test_drawTab_1(function):
    function.ui.showIsoModel.setChecked(True)
    function.ui.showCelestial.setChecked(True)
    function.ui.showTerrain.setChecked(True)
    function.ui.showMountLimits.setChecked(True)
    function.ui.showHorizon.setChecked(True)
    function.app.deviceStat["mount"] = True
    with mock.patch.object(function, "drawCelestialEquator"):
        with mock.patch.object(function.parent.horizonDraw, "drawTerrainImage"):
            with mock.patch.object(function, "drawMeridianLimits"):
                with mock.patch.object(function, "drawHorizonLimits"):
                    with mock.patch.object(function, "drawModelIsoCurve"):
                        with mock.patch.object(function, "drawHorizon"):
                            function.drawTab()
