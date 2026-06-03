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
import gc
import pyqtgraph as pg
import pytest
import shutil
import unittest.mock as mock
from mw4.gui.extWindows.hemisphere.hemisphereDraw import HemisphereDraw
from mw4.gui.extWindows.hemisphere.hemisphereW import HemisphereWindow
from PySide6.QtCore import QPointF
from PySide6.QtWidgets import QApplication
from skyfield.api import Angle, wgs84
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    shutil.copy("tests/testData/terrain.jpg", "tests/work/config/terrain.jpg")
    func = HemisphereDraw(parent=HemisphereWindow(app=App(), title="Hemisphere"))
    yield func
    QApplication.processEvents()
    gc.collect()
    QApplication.processEvents()


def test_initConfig_1(function):
    function.initConfig()


def test_closeTab_1(function):
    function.closeTab()


def test_setPointerVisibility(function):
    function.setupPointer()
    function.setPointerVisibility()


def test_mouseMoved_1(function):
    with mock.patch.object(function.parent, "mouseMoved"):
        function.mouseMovedHemisphere(pos=QPointF(1, 1))


def test_enableOperationModeChange_1(function):
    function.enableOperationModeChange(1)


def test_enableOperationModeChange_2(function):
    function.enableOperationModeChange(0)


def test_setOperationMode_1(function):
    function.ui.editModeHem.setChecked(True)
    with mock.patch.object(function, "drawModelPoints"):
        function.setOperationMode()


def test_setOperationMode_2(function):
    function.ui.alignmentModeHem.setChecked(True)
    function.setOperationMode()


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


def test_setupAlignmentStars(function):
    function.setupAlignmentStars()


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
    function.alignmentStarsText = []
    function.alignmentStarsText.append(pg.TextItem())
    function.ui.showAlignStar.setChecked(True)
    function.ui.alignmentModeHem.setChecked(False)
    function.alignmentStars = pg.ScatterPlotItem()
    function.drawAlignmentStars()


def test_drawAlignmentStars_3(function):
    function.alignmentStarsText = []
    function.alignmentStarsText.append(pg.TextItem())
    function.ui.showAlignStar.setChecked(True)
    function.ui.alignmentModeHem.setChecked(True)
    function.alignmentStars = pg.ScatterPlotItem()
    function.drawAlignmentStars()


def test_setModelPointsAppearanceInPlot_1(function):
    statusList = [0, 1]
    item = pg.PlotDataItem(x=[1, 2], y=[1, 2], symbol="o")
    function.setModelPointsAppearanceInPlot(item, statusList)


def test_drawModelPoints_1(function):
    function.app.data.buildP = []
    function.drawModelPoints()


def test_drawModelPoints_2(function):
    function.modelPoints = pg.PlotDataItem(x=[1, 2], y=[1, 2], symbol="o")
    function.app.data.buildP = [(1, 1, 0), (2, 2, 0)]
    with mock.patch.object(function, "setModelPointsAppearanceInPlot"):
        function.drawModelPoints()


def test_drawModelText_1(function):
    function.app.data.buildP = []
    function.drawModelText()


def test_drawModelText_2(function):
    function.modelPoints = pg.PlotDataItem(x=[1, 2], y=[1, 2], symbol="o")
    function.app.data.buildP = [(1, 1, 1), (2, 2, 0)]
    function.ui.editModeHem.setChecked(True)
    function.modelPointsText.append(pg.TextItem())
    function.drawModelText()


def test_drawModelText_3(function):
    function.modelPoints = pg.PlotDataItem(x=[1, 2], y=[1, 2], symbol="o")
    function.app.data.buildP = [(1, 1, 1), (2, 2, 0)]
    function.ui.normalModeHem.setChecked(True)
    function.drawModelText()


def test_updateDataModel(function):
    with (
        mock.patch.object(function, "drawModelPoints"),
        mock.patch.object(function, "drawModelText"),
    ):
        function.updateDataModel([1, 2], [1, 2])


def test_setupModel_1(function):
    with (
        mock.patch.object(function, "drawModelPoints"),
        mock.patch.object(function, "drawModelText"),
    ):
        function.ui.editModeHem.setChecked(True)
        function.ui.showSlewPath.setChecked(True)
        function.setupModel()


def test_setupModel_2(function):
    with (
        mock.patch.object(function, "drawModelPoints"),
        mock.patch.object(function, "drawModelText"),
    ):
        function.ui.normalModeHem.setChecked(True)
        function.ui.showSlewPath.setChecked(False)
        function.setupModel()


def test_setupPointer(function):
    function.setupPointer()


def test_drawPointer(function):
    function.app.mount.obsSite.Az = Angle(degrees=10)
    function.app.mount.obsSite.Alt = Angle(degrees=10)
    function.setupPointer()
    function.drawPointer()


def test_setupDome(function):
    function.setupDome()


def test_setDomeAzimuth(function):
    function.pointerDome = pg.QtWidgets.QGraphicsRectItem(165, 1, 30, 88)
    function.setDomeAzimuth(100)


def test_drawDome_1(function):
    function.pointerDome = pg.QtWidgets.QGraphicsRectItem(165, 1, 30, 88)
    function.app.dReg.drivers["dome"]["stat"] = False
    function.drawDome()


def test_drawDome_2(function):
    function.pointerDome = pg.QtWidgets.QGraphicsRectItem(165, 1, 30, 88)
    function.app.dReg.drivers["dome"]["stat"] = True
    function.drawDome()


def test_drawModelIsoCurve_1(function):
    function.app.mount.model.starList = []
    function.drawModelIsoCurve()


def test_drawModelIsoCurve_2(function):
    class Star:
        alt = Angle(degrees=10)
        az = Angle(degrees=20)
        errorRMS = 5

    function.app.mount.model.starList = [Star()]
    with mock.patch.object(function.ui.hemisphere, "addIsoItemHorizon", return_value=True):
        function.drawModelIsoCurve()


def test_slewDirect_1(function):
    with mock.patch.object(function, "messageDialog", return_value=False):
        function.slewDirect(QPointF(1, 1))


def test_slewDirect_2(function):
    with (
        mock.patch.object(function, "messageDialog", return_value=True),
        mock.patch.object(function.slewInterface, "slewTargetAltAz", return_value=False),
    ):
        function.slewDirect(QPointF(1, 1))


def test_slewStar_1(function):
    function.alignmentStars = pg.ScatterPlotItem()
    with mock.patch.object(function.alignmentStars, "pointsAt", return_value=[]):
        function.slewStar(QPointF(1, 1))


def test_slewStar_2(function):
    class Spot:
        @staticmethod
        def index():
            return 0

    function.app.hipparcos.name = ["test"]
    function.app.mount.setting.statusDualAxisTracking = True
    function.alignmentStars = pg.ScatterPlotItem(x=[0, 1, 2], y=[0, 1, 2])
    with (
        mock.patch.object(function.alignmentStars, "pointsAt", return_value=[Spot()]),
        mock.patch.object(function, "messageDialog", return_value=0),
        mock.patch.object(
            function.app.hipparcos, "getAlignStarRaDecFromName", return_value=(0, 0)
        ),
    ):
        function.slewStar(QPointF(1, 1))


def test_slewStar_3(function):
    class Spot:
        @staticmethod
        def index():
            return 0

    function.app.hipparcos.name = ["test"]
    function.app.mount.setting.statusDualAxisTracking = False
    function.app.mount.model.numberStars = 5
    function.alignmentStars = pg.ScatterPlotItem(x=[0, 1, 2], y=[0, 1, 2])
    with (
        mock.patch.object(function.alignmentStars, "pointsAt", return_value=[Spot()]),
        mock.patch.object(function, "messageDialog", return_value=0),
        mock.patch.object(
            function.app.hipparcos, "getAlignStarRaDecFromName", return_value=(0, 0)
        ),
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
    with (
        mock.patch.object(function.alignmentStars, "pointsAt", return_value=[Spot()]),
        mock.patch.object(function, "messageDialog", return_value=1),
        mock.patch.object(
            function.app.hipparcos, "getAlignStarRaDecFromName", return_value=(0, 0)
        ),
        mock.patch.object(function.slewInterface, "slewTargetRaDec", return_value=False),
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
    with (
        mock.patch.object(function.alignmentStars, "pointsAt", return_value=[Spot()]),
        mock.patch.object(function, "messageDialog", return_value=2),
        mock.patch.object(
            function.app.hipparcos, "getAlignStarRaDecFromName", return_value=(0, 0)
        ),
        mock.patch.object(function.slewInterface, "slewTargetRaDec", return_value=True),
    ):
        function.slewStar(QPointF(1, 1))


def test_mouseDoubleClick_1(function):
    function.ui.alignmentModeHem.setChecked(True)
    function.ui.normalModeHem.setChecked(False)
    with mock.patch.object(function, "slewStar"):
        function.mouseDoubleClick(1, QPointF(1, 1))


def test_mouseDoubleClick_2(function):
    function.ui.alignmentModeHem.setChecked(False)
    function.ui.normalModeHem.setChecked(True)
    with mock.patch.object(function, "slewDirect"):
        function.mouseDoubleClick(1, QPointF(1, 1))


def test_mouseDoubleClick_3(function):
    function.ui.editModeHem.setChecked(True)
    with (
        mock.patch.object(function, "slewStar") as mock_star,
        mock.patch.object(function, "slewDirect") as mock_direct,
    ):
        function.mouseDoubleClick(1, QPointF(1, 1))
        mock_star.assert_not_called()
        mock_direct.assert_not_called()


def test_drawTab_1(function):
    function.ui.showIsoModel.setChecked(True)
    function.ui.showCelestial.setChecked(True)
    function.ui.showTerrain.setChecked(True)
    function.ui.showMountLimits.setChecked(True)
    function.ui.showHorizon.setChecked(True)
    function.app.dReg.drivers["mount"]["stat"] = True
    function.app.mount.model.numberStars = 5
    with (
        mock.patch.object(function, "drawCelestialEquator"),
        mock.patch.object(function.parent, "drawTerrainImage"),
        mock.patch.object(function.parent, "drawMeridianLimits"),
        mock.patch.object(function.parent, "drawHorizonLimits"),
        mock.patch.object(function, "drawModelIsoCurve"),
        mock.patch.object(function, "drawHorizon"),
    ):
        function.drawTab()


def test_drawTab_2(function):
    function.ui.showIsoModel.setChecked(False)
    function.ui.showCelestial.setChecked(False)
    function.ui.showTerrain.setChecked(False)
    function.ui.showMountLimits.setChecked(False)
    function.ui.showHorizon.setChecked(False)
    function.app.dReg.drivers["mount"]["stat"] = False
    function.app.mount.model.numberStars = 0
    function.drawTab()


def test_drawCelestialEquator_empty(function):
    with mock.patch.object(
        function.app.buildPoint, "generateCelestialEquator", return_value=None
    ):
        function.drawCelestialEquator()


def test_drawModelPoints_no_items(function):
    function.app.buildPoint.buildP = []
    function.drawModelPoints()


def test_drawModelText_empty(function):
    function.app.buildPoint.buildP = []
    function.drawModelText()


def test_drawModelPoints_with_findItem_returning_none(function):
    function.app.buildPoint.buildP = [(10, 20, 1), (30, 40, 2)]
    with mock.patch.object(
        function.ui.hemisphere, "findItemByName", return_value=None
    ):
        function.drawModelPoints()


def test_drawModelText_with_existing_text_items(function):
    function.app.buildPoint.buildP = [(10, 20, 1)]
    fakeTextItem = mock.MagicMock()
    function.modelPointsText = [fakeTextItem]
    with mock.patch.object(function.ui.hemisphere.p[0], "removeItem"):
        function.drawModelText()


