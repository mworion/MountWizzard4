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
import mw4.gui.extWindows.image.imageW
import numpy as np
import pyqtgraph as pg
import pytest
import shutil
from mw4.gui.extWindows.image.imageTabs import ImageTabs
from mw4.gui.extWindows.image.imageW import ImageWindow
from mw4.gui.utilities.nativeQt.qtFileDialog import MWFileDialog
from mw4.gui.utilities.qtMain import MWidget
from pathlib import Path
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QApplication
from skyfield.api import Angle
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    with (
        mock.patch.object(ImageTabs, "setCrosshair"),
        mock.patch.object(ImageTabs, "colorChange"),
    ):
        func = ImageWindow(App(), title="Image")
        yield func
        QApplication.processEvents()


def test_classVars_tabLists(function):
    assert ImageWindow.TAB_ASPECT == [
        "image",
        "imageSource",
        "tiltSquare",
        "tiltTriangle",
        "background",
        "backgroundRMS",
        "hfr",
        "roundness",
    ]
    assert ImageWindow.TAB_LEVEL == [
        "imageSource",
        "tiltSquare",
        "tiltTriangle",
        "aberration",
    ]
    assert function.TAB_ASPECT == ImageWindow.TAB_ASPECT
    assert function.TAB_LEVEL == ImageWindow.TAB_LEVEL


def test_initConfig_1(function):
    with (
        mock.patch.object(function, "setPositionWindow"),
        mock.patch.object(function.tabs, "setCrosshair"),
    ):
        function.initConfig()


def test_storeConfig_1(function):
    if "WindowImage" in function.app.config:
        del function.app.config["WindowImage"]
    function.storeConfig()


def test_storeConfig_2(function):
    function.app.config["WindowImage"] = {}
    function.storeConfig()


def test_showWindow_1(function):
    with (
        mock.patch.object(function, "setAspectLocked"),
        mock.patch.object(function, "clearGui"),
        mock.patch.object(function, "setupIcons"),
        mock.patch.object(function, "colorChange"),
        mock.patch.object(function, "show"),
    ):
        function.showWindow()


def test_closeEvent_1(function):
    with mock.patch.object(MWidget, "closeEvent"), mock.patch.object(function, "storeConfig"):
        function.closeEvent(QCloseEvent)


def test_setupIcons_1(function):
    function.setupIcons()


def test_colorChange(function):
    with (
        mock.patch.object(function, "showCurrent"),
        mock.patch.object(function.tabs, "colorChange"),
        mock.patch.object(function, "setupIcons"),
    ):
        function.colorChange()


def test_clearGui(function):
    function.clearGui()


def test_operationMode_1(function):
    function.operationMode(0)


def test_operationMode_2(function):
    function.operationMode(1)


def test_updateWindowsStats_1(function):
    function.isExposing = True
    function.isSolving = False
    function.updateWindowsStats()


def test_updateWindowsStats_2(function):
    function.isExposing = False
    function.isSolving = True
    function.updateWindowsStats()


def test_updateWindowsStats_3(function):
    function.isExposing = False
    function.isSolving = False
    function.updateWindowsStats()


def test_updateWindowsStats_noCameraDevice(function):
    function.isExposing = False
    function.isSolving = False
    function.app.dReg["camera"].stat = False
    function.updateWindowsStats()
    function.app.dReg["camera"].stat = True


def test_selectImage_1(function):
    function.ui.autoSolve.setChecked(False)
    with mock.patch.object(MWFileDialog, "getOpenFileName", return_value=Path("xyz.fits")):
        function.selectImage()


def test_selectImage_2(function):
    function.ui.autoSolve.setChecked(False)
    with (
        mock.patch.object(
            MWFileDialog, "getOpenFileName", return_value=Path("c:/test/test.fits")
        ),
        mock.patch.object(Path, "is_file", return_value=True),
    ):
        function.selectImage()
        assert function.folder == Path("c:/test")


def test_selectImage_3(function):
    function.ui.autoSolve.setChecked(True)
    with (
        mock.patch.object(
            MWFileDialog, "getOpenFileName", return_value=Path("c:/test/test.fits")
        ),
        mock.patch.object(Path, "is_file", return_value=True),
    ):
        function.selectImage()
        assert function.folder == Path("c:/test")


def test_copyLevels(function):
    with mock.patch.object(pg.ImageItem, "setLevels"):
        function.copyLevels()


def test_setAspectLocked(function):
    with mock.patch.object(pg.PlotItem, "setAspectLocked"):
        function.setAspectLocked()


def test_resultPhotometry_1(function):
    function.photometry.hfr = np.zeros(0)
    function.resultPhotometry()


def test_resultPhotometry_2(function):
    function.photometry.hfr = np.ones(20)
    function.resultPhotometry()


def test_processPhotometry_1(function):
    function.ui.photometryGroup.setChecked(True)
    function.fileHandler.image = 1
    with (
        mock.patch.object(function.photometry, "processPhotometry"),
        mock.patch.object(function, "clearGui"),
    ):
        function.processPhotometry()


def test_processPhotometry_2(function):
    function.fileHandler.image = None
    with mock.patch.object(function, "clearGui"):
        function.processPhotometry()


def test_showImage_1(function):
    with mock.patch.object(function, "clearGui"):
        function.showImage(Path(""))


def test_showImage_2(function):
    function.showImage(Path("c:/test/test.fits"))


def test_showImage_3(function):
    with (
        mock.patch.object(Path, "is_file", return_value=True),
        mock.patch.object(function.fileHandler, "loadImage"),
    ):
        function.showImage(Path("c:/test/test.fits"))


def test_showCurrent_1(function):
    function.showCurrent()


def test_exposeRaw_1(function):
    function.app.dReg["camera"].instance.subFrame = 100
    function.ui.timeTagImage.setChecked(True)
    with mock.patch.object(function.app.dReg["camera"].instance, "expose", return_value=True):
        function.exposeRaw(exposureTime=1, binning=1)


def test_exposeRaw_2(function):
    function.app.dReg["camera"].instance.subFrame = 100
    function.ui.timeTagImage.setChecked(False)
    with mock.patch.object(function.app.dReg["camera"].instance, "expose", return_value=True):
        function.exposeRaw(exposureTime=1, binning=1)


def test_exposeRaw_3(function):
    function.app.dReg["camera"].instance.subFrame = 100
    with (
        mock.patch.object(function.app.dReg["camera"].instance, "expose", return_value=False),
        mock.patch.object(function.app.dReg["camera"].instance, "abort", return_value=True),
    ):
        function.exposeRaw(exposureTime=1, binning=1)


def test_exposeImageDone_1(function):
    function.ui.autoSolve.setChecked(False)
    function.app.dReg["camera"].instance.signals.saved.connect(function.exposeImageDone)
    function.exposeImageDone(Path("test"))


def test_exposeImageDone_2(function):
    function.ui.autoSolve.setChecked(True)
    function.app.dReg["camera"].instance.signals.saved.connect(function.exposeImageDone)
    function.exposeImageDone(Path("test"))


def test_exposeImage_1(function):
    function.app.dReg["camera"].stat = True
    function.app.dReg["camera"].instance.data = {}
    with mock.patch.object(function.app.dReg["camera"].instance, "expose", return_value=True):
        function.exposeImage()


def test_exposeImage_noCameraConnected(function):
    function.app.dReg["camera"].stat = False
    mock_msg = mock.MagicMock()
    original_msg = function.msg
    function.msg = mock_msg
    try:
        function.exposeImage()
        mock_msg.emit.assert_called_once_with(2, "Image", "Error", "No camera connected")
    finally:
        function.msg = original_msg


def test_exposeImageDone_continuous(function):
    function.ui.autoSolve.setChecked(False)
    function.ui.continous.setChecked(True)
    function.app.dReg["camera"].signals.saved.connect(function.exposeImageDone)
    function.exposeImageDone(Path("test"))


def test_exposeImageDone_continuousAutoSolve(function):
    function.ui.autoSolve.setChecked(True)
    function.ui.continous.setChecked(True)
    function.app.dReg["camera"].signals.saved.connect(function.exposeImageDone)
    function.exposeImageDone(Path("test"))


def test_exposeImageDone_noContinuous(function):
    function.ui.continous.setChecked(False)
    function.app.dReg["camera"].signals.saved.connect(function.exposeImageDone)
    function.exposeImageDone(Path("test"))


def test_abortExpose_1(function):
    function.app.dReg["camera"].signals.saved.connect(function.exposeImageDone)
    with mock.patch.object(function.app.dReg["camera"].instance, "abort"):
        function.abortExpose()


def test_abortExpose_2(function):
    function.isExposing = True
    function.imageFileNameOld = Path("old.fits")
    function.imageFileName = Path("new.fits")
    function.app.dReg["camera"].signals.saved.connect(function.exposeImageDone)
    function.app.dReg["camera"].signals.saved.connect(function.showImage)
    with mock.patch.object(function.app.dReg["camera"].instance, "abort"):
        function.abortExpose()


def test_abortExpose_3(function):
    function.isExposing = False
    function.imageFileNameOld = Path("old.fits")
    function.imageFileName = Path("new.fits")
    function.app.dReg["camera"].signals.saved.connect(function.exposeImageDone)
    function.app.dReg["camera"].signals.saved.connect(function.showImage)
    with mock.patch.object(function.app.dReg["camera"].instance, "abort"):
        function.abortExpose()


def test_abortExpose_4(function):
    function.isExposing = True
    function.ui.continous.setChecked(True)
    function.imageFileNameOld = Path("old.fits")
    function.imageFileName = Path("new.fits")
    function.app.dReg["camera"].signals.saved.connect(function.exposeImageDone)
    with mock.patch.object(function.app.dReg["camera"].instance, "abort"):
        function.abortExpose()


def test_solveDone_1(function):
    function.app.dReg["plateSolve"].signals.result.connect(function.solveDone)
    function.solveDone({"success": False})


def test_solveDone_2(function):
    result = {
        "success": False,
        "raJ2000S": Angle(hours=10),
        "decJ2000S": Angle(degrees=20),
        "angleS": 30,
        "scaleS": 1,
        "errorRMS_S": 3,
        "flippedS": False,
        "imagePath": "test",
        "message": "test",
    }
    function.app.dReg["plateSolve"].signals.result.connect(function.solveDone)
    function.solveDone(result=result)


def test_solveDone_3(function):
    function.ui.embedData.setChecked(True)
    result = {
        "success": True,
        "raJ2000S": Angle(hours=10),
        "decJ2000S": Angle(degrees=20),
        "angleS": Angle(degrees=30),
        "scaleS": 1,
        "errorRMS_S": 3,
        "flippedS": False,
        "imagePath": "test",
        "message": "test",
    }

    function.app.dReg["plateSolve"].signals.result.connect(function.solveDone)
    function.solveDone(result=result)


def test_solveImage_1(function):
    function.solveImage(Path(""))


def test_solveImage_2(function):
    function.solveImage(imagePath=Path("testFile"))


def test_solveImage_3(function):
    shutil.copy("tests/testData/m51.fit", "tests/work/image/m51.fit")
    file = Path("tests/work/image/m51.fit")
    with mock.patch.object(function.app.dReg["plateSolve"].instance, "solve"):
        function.solveImage(imagePath=file)


def test_solveCurrent(function):
    function.solveCurrent()


def test_abortSolve_1(function):
    function.abortSolve()


def test_slewDirect_1(function):
    function.app.dReg.d["mount"].stat = False
    function.slewDirect(Angle(hours=0), Angle(degrees=0))


def test_slewDirect_2(function):
    function.app.dReg.d["mount"].stat = True
    with mock.patch(
        "mw4.gui.extWindows.image.imageW.MWMessageDialog.question",
        return_value=False,
    ):
        function.slewDirect(Angle(hours=0), Angle(degrees=0))


def test_slewDirect_3(function):
    function.app.dReg.d["mount"].stat = True
    with (
        mock.patch(
            "mw4.gui.extWindows.image.imageW.MWMessageDialog.question",
            return_value=True,
        ),
        mock.patch.object(function.slewInterface, "slewTargetRaDec", return_value=True),
    ):
        function.slewDirect(Angle(hours=0), Angle(degrees=0))


def test_slewCenter_1(function):
    function.fileHandler.header = {
        "RA": 10,
        "DEC": 10,
    }
    with mock.patch.object(function, "slewDirect"):
        function.slewCenter()


def test_syncModelToImage_1(function):
    function.app.dReg.d["mount"].stat = False
    function.imageFileName = Path("tests")
    function.syncModelToImage()


def test_syncModelToImage_2(function):
    function.app.dReg.d["mount"].stat = True
    function.imageFileName = Path("tests")
    function.syncModelToImage()


def test_syncModelToImage_3(function):
    function.app.dReg.d["mount"].stat = True
    function.imageFileName = Path("tests/testData/m51.fit")
    with (
        mock.patch.object(
            mw4.gui.extWindows.image.imageW,
            "getCoordinatesFromHeader",
            return_value=(Angle(hours=10), Angle(degrees=10)),
        ),
        mock.patch.object(
            mw4.gui.extWindows.image.imageW,
            "J2000ToJNow",
            return_value=(Angle(hours=10), Angle(degrees=10)),
        ),
        mock.patch.object(
            function.app.mount.obsSite, "syncPositionToTarget", return_value=False
        ),
    ):
        function.syncModelToImage()


def test_syncModelToImage_4(function):
    function.app.dReg.d["mount"].stat = True
    function.imageFileName = Path("tests/testData/m51.fit")
    with (
        mock.patch.object(
            mw4.gui.extWindows.image.imageW,
            "getCoordinatesFromHeader",
            return_value=(Angle(hours=10), Angle(degrees=10)),
        ),
        mock.patch.object(
            function.app.mount.obsSite, "syncPositionToTarget", return_value=False
        ),
    ):
        function.syncModelToImage()


def test_syncModelToImage_5(function):
    function.app.dReg.d["mount"].stat = True
    function.imageFileName = Path("tests/testData/m51.fit")
    with (
        mock.patch.object(
            mw4.gui.extWindows.image.imageW,
            "getCoordinatesFromHeader",
            return_value=(Angle(hours=10), Angle(degrees=10)),
        ),
        mock.patch.object(
            function.app.mount.obsSite, "syncPositionToTarget", return_value=True
        ),
    ):
        function.syncModelToImage()


def test_abortExpose_fail(function):
    function.app.dReg["camera"].signals.saved.connect(function.exposeImageDone)
    with mock.patch.object(function.app.dReg["camera"].instance, "abort", return_value=False):
        function.abortExpose()


def test_setButtonExposingStatusEnabled_noCamera(function):
    saved = function.app.dReg.d["camera"]
    function.app.dReg.d["camera"] = None
    try:
        function.setButtonExposingStatusEnabled()
        assert not function.ui.expose.isEnabled()
        assert not function.ui.abortExpose.isEnabled()
    finally:
        function.app.dReg.d["camera"] = saved


def test_setButtonExposingStatusEnabled_isExposing(function):
    function.isExposing = True
    function.setButtonExposingStatusEnabled()
    assert not function.ui.load.isEnabled()
    assert function.ui.abortExpose.isEnabled()


def test_setButtonExposingStatusEnabled_notExposing(function):
    function.isExposing = False
    function.setButtonExposingStatusEnabled()
    assert function.ui.expose.isEnabled()
    assert function.ui.load.isEnabled()
    assert not function.ui.abortExpose.isEnabled()
