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
# Licence APL2.0
#
###########################################################
from pathlib import Path
import numpy as np
import os
import pytest
import shutil
import unittest.mock as mock
from astropy.io import fits
from mw4.gui.mainWaddon.tabTools_Rename import Rename
from mw4.gui.utilities.toolsQtWidget import MWidget
from mw4.gui.widgets.main_ui import Ui_MainWindow
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    mainW = MWidget()
    mainW.app = App()
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)
    window = Rename(mainW)
    yield window
    mainW.app.threadPool.waitForDone(1000)


def test_initConfig_1(function):
    function.app.config["mainW"] = {}
    function.initConfig()


def test_storeConfig_1(function):
    function.storeConfig()


def test_setupIcons_1(function):
    function.setupIcons()


def test_setupGuiTools(function):
    function.setupGuiTools()
    for _, ui in function.selectorsDropDowns.items():
        assert ui.count() == 7


def test_getNumberFiles_1(function):
    function.renameDir = Path("tests/testData")
    number = function.getNumberFiles("**/*.fit*")
    assert number > 0


def test_getNumberFiles_2(function):
    function.renameDir = Path("tests/testData")
    number = function.getNumberFiles("**/star*.fit*")
    assert number == 3


def test_getNumberFiles_3(function):
    function.renameDir = Path("tests/testData")
    number = function.getNumberFiles("star*.fit*")
    assert number == 3


def test_convertHeaderEntry_1(function):
    chunk = function.convertHeaderEntry(entry="", fitsKey="1")
    assert not chunk


def test_convertHeaderEntry_2(function):
    chunk = function.convertHeaderEntry(entry="1", fitsKey="")
    assert not chunk


def test_convertHeaderEntry_3(function):
    chunk = function.convertHeaderEntry(entry="2019-05-26T17:02:18.843", fitsKey="DATE-OBS")
    assert chunk == "2019-05-26_17-02-18"


def test_convertHeaderEntry_4(function):
    chunk = function.convertHeaderEntry(entry="2019-05-26T17:02:18", fitsKey="DATE-OBS")
    assert chunk == "2019-05-26_17-02-18"


def test_convertHeaderEntry_5(function):
    chunk = function.convertHeaderEntry(entry=1, fitsKey="XBINNING")
    assert chunk == "Bin1"


def test_convertHeaderEntry_6(function):
    chunk = function.convertHeaderEntry(entry=25, fitsKey="CCD-TEMP")
    assert chunk == "Temp025"


def test_convertHeaderEntry_7(function):
    chunk = function.convertHeaderEntry(entry="Light", fitsKey="FRAME")
    assert chunk == "Light"


def test_convertHeaderEntry_8(function):
    chunk = function.convertHeaderEntry(entry="red", fitsKey="FILTER")
    assert chunk == "red"


def test_convertHeaderEntry_9(function):
    chunk = function.convertHeaderEntry(entry=14, fitsKey="EXPTIME")
    assert chunk == "Exp14s"


def test_convertHeaderEntry_11(function):
    chunk = function.convertHeaderEntry(entry="12354", fitsKey="XXX")
    assert not chunk


def test_processSelectors_1(function):
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header.set("DATE-OBS", "2019-05-26T17:02:18.843")
    name = function.processSelectors(header, "Frame")
    assert not name


def test_processSelectors_2(function):
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header.set("DATE-OBS", "2019-05-26T17:02:18.843")
    name = function.processSelectors(header, "Datetime")
    assert name == "2019-05-26_17-02-18"


def test_renameFile_1(function):
    hdu = fits.PrimaryHDU(np.arange(100.0))
    hduList = fits.HDUList([hdu])
    hduList.writeto(Path("tests/work/image/m01.fit"), overwrite=True)
    with mock.patch.object(Path, "rename"):
        function.renameFile(Path("tests/work/image/m01.fit"))


def test_renameFile_2(function):
    hdu = fits.PrimaryHDU(np.arange(100.0))
    hduList = fits.HDUList([hdu])
    hduList.writeto(Path("tests/work/image/m02.fit"), overwrite=True)

    with mock.patch.object(Path, "rename"):
        function.renameFile(Path("tests/work/image/m02.fit"))


def test_renameFile_3(function):
    hdu = fits.PrimaryHDU(np.arange(100.0))
    hduList = fits.HDUList([hdu])
    function.ui.newObjectName.setText("test")
    hduList.writeto(Path("tests/work/image/m03.fit"), overwrite=True)

    with mock.patch.object(Path, "rename"):
        function.renameFile(Path("tests/work/image/m03.fit"))


def test_renameFile_4(function):
    hdu = fits.PrimaryHDU(np.arange(100.0))
    hdu.header["FILTER"] = "test"
    hduList = fits.HDUList([hdu])
    hduList.writeto(Path("tests/work/image/m04.fit"), overwrite=True)
    function.ui.rename1.clear()
    function.ui.rename1.addItem("Filter")

    with mock.patch.object(os, "rename"):
        function.renameFile(Path("tests/work/image/m04.fit"))


def test_renameRunGUI_1(function):
    function.renameDir = Path("tests/work/xxx")
    function.ui.includeSubdirs.setChecked(False)
    function.renameRunGUI()


def test_renameRunGUI_2(function):
    function.ui.includeSubdirs.setChecked(True)
    function.renameDir = Path("tests/work/image")
    with mock.patch.object(function, "getNumberFiles", return_value=0):
        function.renameRunGUI()


def test_renameRunGUI_3(function):
    shutil.copy("tests/testData/m51.fit", "tests/work/image/m51.fit")
    function.renameDir = Path("tests/work/image")
    function.ui.includeSubdirs.setChecked(False)
    with mock.patch.object(function, "renameFile"):
        function.renameRunGUI()


def test_renameRunGUI_4(function):
    shutil.copy("tests/testData/m51.fit", "tests/work/image/m51.fit")
    function.renameDir = Path("tests/work/image")
    with mock.patch.object(function, "renameFile"):
        function.renameRunGUI()


def test_chooseDir_1(function):
    with mock.patch.object(MWidget, "openDir", return_value=("", "", "")):
        function.chooseDir()


def test_chooseDir_2(function):
    with mock.patch.object(MWidget, "openDir", return_value=("test", "", "")):
        function.chooseDir()
