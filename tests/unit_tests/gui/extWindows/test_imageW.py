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
import shutil
from pathlib import Path

# external packages
from PySide6.QtGui import QCloseEvent
from PySide6.QtCore import QPointF
from astropy.io import fits
from astropy import wcs
from skyfield.api import Angle
import numpy as np

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.utilities.toolsQtWidget import MWidget
from gui.utilities.slewInterface import SlewInterface
from gui.extWindows.imageW import ImageWindow
from logic.photometry.photometry import Photometry
from logic.file.fileHandler import FileHandler
from base.loggerMW import setupLogging

setupLogging()


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    func = ImageWindow(app=App())
    yield func


def test_initConfig_1(function):
    function.initConfig()


def test_storeConfig_1(function):
    if "imageW" in function.app.config:
        del function.app.config["imageW"]

    function.storeConfig()


def test_storeConfig_2(function):
    function.app.config["imageW"] = {}

    function.storeConfig()


def test_enableTabsMovable(function):
    function.enableTabsMovable(True)


def test_closeEvent_1(function):
    with mock.patch.object(function, "show"):
        with mock.patch.object(MWidget, "closeEvent"):
            function.showWindow()
            function.closeEvent(QCloseEvent)


def test_colorChange(function):
    with mock.patch.object(function, "showCurrent"):
        function.colorChange()


def test_clearGui(function):
    function.clearGui()


def test_operationMode_1(function):
    function.operationMode(0)


def test_operationMode_2(function):
    function.operationMode(1)


def test_updateWindowsStats_1(function):
    function.imagingDeviceStat["expose"] = True
    function.imagingDeviceStat["exposeN"] = True
    function.imagingDeviceStat["solve"] = True
    function.app.deviceStat["camera"] = False
    function.app.deviceStat["plateSolve"] = True
    function.imagingDeviceStat["imaging"] = True
    function.imagingDeviceStat["plateSolve"] = True

    function.updateWindowsStats()


def test_updateWindowsStats_2(function):
    function.imagingDeviceStat["expose"] = False
    function.imagingDeviceStat["exposeN"] = True
    function.imagingDeviceStat["solve"] = False
    function.app.deviceStat["camera"] = True
    function.app.deviceStat["plateSolve"] = False
    function.imagingDeviceStat["imaging"] = False
    function.imagingDeviceStat["plateSolve"] = False

    function.updateWindowsStats()


def test_updateWindowsStats_3(function):
    function.imagingDeviceStat["expose"] = False
    function.imagingDeviceStat["exposeN"] = False
    function.imagingDeviceStat["solve"] = False
    function.app.deviceStat["camera"] = True
    function.app.deviceStat["plateSolve"] = False
    function.imagingDeviceStat["imaging"] = False
    function.imagingDeviceStat["plateSolve"] = False

    function.updateWindowsStats()


def test_selectImage_1(function):
    with mock.patch.object(MWidget, "openFile", return_value=Path("test.fits")):
        function.selectImage()


def test_selectImage_2(function):
    function.ui.autoSolve.setChecked(False)
    with mock.patch.object(MWidget, "openFile", return_value=Path("c:/test/test.fits")):
        with mock.patch.object(Path, "is_file", return_value=True):
            function.selectImage()
            assert function.folder == Path("c:/test")


def test_selectImage_3(function):
    function.ui.autoSolve.setChecked(True)
    with mock.patch.object(MWidget, "openFile", return_value=Path("c:/test/test.fits")):
        with mock.patch.object(Path, "is_file", return_value=True):
            function.selectImage()
            assert function.folder == Path("c:/test")


def test_setBarColor_1(function):
    function.ui.color.setCurrentIndex(0)
    with mock.patch.object(function.ui.image, "setColorMap"):
        function.setBarColor()


def test_copyLevels(function):
    function.copyLevels()


def test_setCrosshair_1(function):
    function.ui.color.setCurrentIndex(0)
    with mock.patch.object(function.ui.image, "showCrosshair"):
        function.setCrosshair()


def test_setAspectLocked(function):
    function.setAspectLocked()


def test_getImageSourceRange(function):
    function.getImageSourceRange()


def test_clearImageTab(function):
    function.clearImageTab(function.ui.image)


def test_writeHeaderDataToGUI_1(function):
    function.header = fits.PrimaryHDU().header
    function.writeHeaderDataToGUI(function.header)


def test_writeHeaderDataToGUI_2(function):
    function.header = fits.PrimaryHDU().header
    function.header["naxis"] = 2
    function.writeHeaderDataToGUI(function.header)


def test_writeHeaderDataToGUI_3(function):
    function.header = fits.PrimaryHDU().header
    function.header["naxis"] = 2
    function.header["OBJCTRA"] = "+08 00 00"
    function.header["OBJCTDEC"] = "90 00 00"
    function.writeHeaderDataToGUI(function.header)


def test_writeHeaderDataToGUI_4(function):
    function.header = fits.PrimaryHDU().header
    function.header["naxis"] = 2
    function.header["RA"] = 12.0
    function.header["DEC"] = 80.0
    function.writeHeaderDataToGUI(function.header)


def test_resultPhotometry_1(function):
    function.photometry = Photometry(function)
    function.photometry.objs = None
    function.resultPhotometry()


def test_resultPhotometry_2(function):
    function.photometry = Photometry(function)
    function.photometry.objs = 1
    function.resultPhotometry()


def test_processPhotometry_1(function):
    class App:
        threadPool = None

    function.fileHandler = FileHandler(App())
    function.ui.photometryGroup.setChecked(True)
    function.fileHandler.image = 1
    with mock.patch.object(function.photometry, "processPhotometry"):
        function.processPhotometry()


def test_processPhotometry_2(function):
    class App:
        threadPool = None

    function.fileHandler = FileHandler(App())
    function.fileHandler.image = None
    with mock.patch.object(function, "clearGui"):
        function.processPhotometry()


def test_showImage_1(function):
    function.imagingDeviceStat["expose"] = True
    with mock.patch.object(function, "clearGui"):
        function.showImage(Path(""))


def test_showImage_2(function):
    function.imagingDeviceStat["expose"] = False
    function.showImage(Path("c:/test/test.fits"))


def test_showImage_3(function):
    function.imagingDeviceStat["expose"] = False
    with mock.patch.object(Path, "is_file", return_value=True):
        with mock.patch.object(function.fileHandler, "loadImage"):
            function.showImage(Path("c:/test/test.fits"))


def test_showCurrent_1(function):
    function.showCurrent()


def test_exposeRaw_1(function):
    function.app.camera.subFrame = 100
    function.ui.timeTagImage.setChecked(True)
    with mock.patch.object(function.app.camera, "expose", return_value=True):
        function.exposeRaw(exposureTime=1, binning=1)


def test_exposeRaw_2(function):
    function.app.camera.subFrame = 100
    function.ui.timeTagImage.setChecked(False)
    with mock.patch.object(function.app.camera, "expose", return_value=True):
        function.exposeRaw(exposureTime=1, binning=1)


def test_exposeRaw_3(function):
    function.app.camera.subFrame = 100
    with mock.patch.object(function.app.camera, "expose", return_value=False):
        function.exposeRaw(exposureTime=1, binning=1)


def test_exposeImageDone_1(function):
    function.ui.autoSolve.setChecked(False)
    function.app.camera.signals.saved.connect(function.exposeImageDone)
    function.exposeImageDone(Path("test"))


def test_exposeImageDone_2(function):
    function.ui.autoSolve.setChecked(True)
    function.app.camera.signals.saved.connect(function.exposeImageDone)
    function.exposeImageDone(Path("test"))


def test_exposeImage_1(function):
    function.app.camera.data = {}
    function.exposeImage()


def test_exposeImageNDone_1(function):
    function.ui.autoSolve.setChecked(False)
    function.app.camera.signals.saved.connect(function.exposeImageDone)
    function.exposeImageNDone(Path("test"))


def test_exposeImageNDone_2(function):
    function.ui.autoSolve.setChecked(True)
    function.app.camera.signals.saved.connect(function.exposeImageDone)
    function.exposeImageNDone(Path("test"))


def test_exposeImageN_1(function):
    function.app.camera.data = {}
    function.exposeImageN()


def test_abortExpose_1(function):
    with mock.patch.object(function.app.camera, "abort"):
        function.abortExpose()


def test_abortExpose_2(function):
    function.app.camera.signals.saved.connect(function.showImage)
    function.ui.exposeN.setEnabled(True)
    function.ui.expose.setEnabled(False)
    function.app.camera.signals.saved.connect(function.exposeRaw)
    with mock.patch.object(function.app.camera, "abort"):
        function.abortExpose()


def test_abortExpose_3(function):
    function.imagingDeviceStat["expose"] = True
    function.imagingDeviceStat["exposeN"] = False
    function.app.camera.signals.saved.connect(function.showImage)
    function.ui.exposeN.setEnabled(False)
    function.ui.expose.setEnabled(True)
    function.app.camera.signals.saved.connect(function.exposeImageDone)
    with mock.patch.object(function.app.camera, "abort"):
        function.abortExpose()


def test_abortExpose_4(function):
    function.imagingDeviceStat["expose"] = False
    function.imagingDeviceStat["exposeN"] = True
    function.app.camera.signals.saved.connect(function.showImage)
    function.ui.exposeN.setEnabled(False)
    function.ui.expose.setEnabled(True)
    function.app.camera.signals.saved.connect(function.exposeImageNDone)
    with mock.patch.object(function.app.camera, "abort"):
        function.abortExpose()


def test_solveDone_1(function):
    function.app.plateSolve.signals.result.connect(function.solveDone)
    function.solveDone([])


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

    function.app.plateSolve.signals.result.connect(function.solveDone)
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

    function.app.plateSolve.signals.result.connect(function.solveDone)
    function.solveDone(result=result)


def test_solveImage_1(function):
    function.solveImage(Path(""))


def test_solveImage_2(function):
    function.solveImage(imagePath=Path("testFile"))


def test_solveImage_3(function):
    shutil.copy("tests/testData/m51.fit", "tests/workDir/image/m51.fit")
    file = Path("tests/workDir/image/m51.fit")
    with mock.patch.object(function.app.plateSolve, "solve"):
        function.solveImage(imagePath=file)


def test_solveCurrent(function):
    function.solveCurrent()


def test_abortSolve_1(function):
    function.abortSolve()


def test_mouseToWorld_0(function):
    function.fileHandler = FileHandler(App())
    function.fileHandler.wcs = None
    function.fileHandler.flipH = True
    function.fileHandler.flipV = False
    ra, dec = function.mouseToWorld(QPointF(1, 1))


def test_mouseToWorld_1(function):
    function.fileHandler = FileHandler(App())
    function.fileHandler.wcs = wcs.WCS({})
    function.fileHandler.flipH = True
    function.fileHandler.flipV = False

    with mock.patch.object(function.fileHandler.wcs, "wcs_pix2world", return_value=(0, 0)):
        ra, dec = function.mouseToWorld(QPointF(1, 1))


def test_slewDirect_1(function):
    function.app.deviceStat["mount"] = False
    function.slewDirect(Angle(hours=0), Angle(degrees=0))


def test_slewDirect_2(function):
    function.app.deviceStat["mount"] = True
    with mock.patch.object(function, "messageDialog", return_value=False):
        function.slewDirect(Angle(hours=0), Angle(degrees=0))


def test_slewDirect_3(function):
    function.app.deviceStat["mount"] = True
    with mock.patch.object(function, "messageDialog", return_value=True):
        with mock.patch.object(SlewInterface, "slewTargetRaDec", return_value=True):
            function.slewDirect(Angle(hours=0), Angle(degrees=0))


def test_mouseMoved_1(function):
    function.fileHandler = FileHandler(App())
    function.fileHandler.wcs = wcs.WCS({})
    function.fileHandler.image = np.random.rand(100, 100) + 1
    with mock.patch.object(
        function.ui.image.p[0].getViewBox(), "posInViewRange", return_value=True
    ):
        function.mouseMoved(pos=QPointF(50, 14))


def test_mouseMoved_2(function):
    function.fileHandler = FileHandler(App())
    function.fileHandler.wcs = wcs.WCS({})
    function.ui.image.setImage(imageDisp=np.random.rand(100, 100) + 1)
    with mock.patch.object(
        function.ui.image.p[0].getViewBox(), "posInViewRange", return_value=False
    ):
        function.mouseMoved(pos=QPointF(50, 25))


def test_mouseDoubleClick_1(function):
    function.fileHandler = FileHandler(App())
    function.mouseDoubleClick(1, QPointF(50, 25))


def test_mouseDoubleClick_2(function):
    function.fileHandler = FileHandler(App())
    function.fileHandler.hasCelestial = True
    with mock.patch.object(function, "slewDirect"):
        with mock.patch.object(function, "mouseToWorld", return_value=(0, 0)):
            function.mouseDoubleClick(1, QPointF(50, 25))


def test_slewCenter_1(function):
    function.fileHandler = FileHandler(App())
    function.slewCenter()


def test_slewCenter_2(function):
    function.fileHandler = FileHandler(App())
    function.fileHandler.header = {
        "RA": 10,
        "DEC": 10,
    }
    function.fileHandler.hasCelestial = True
    with mock.patch.object(function, "slewDirect"):
        function.slewCenter()


def test_syncMountToImage_1(function):
    with mock.patch.object(function.app.mount.obsSite, "syncPositionToTarget", return_value=False):
        function.syncMountToImage()


def test_syncMountToImage_2(function):
    with mock.patch.object(function.app.mount.obsSite, "syncPositionToTarget", return_value=True):
        function.syncMountToImage()
