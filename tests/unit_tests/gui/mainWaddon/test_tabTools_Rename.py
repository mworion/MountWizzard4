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

# external packages
from astropy.io import fits
import numpy as np
from PySide6.QtWidgets import QWidget

# local import
from gui.utilities.toolsQtWidget import MWidget
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.widgets.main_ui import Ui_MainWindow
from gui.mainWaddon.tabTools_Rename import Rename


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    mainW = QWidget()
    mainW.app = App()
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)
    window = Rename(mainW)
    yield window
    mainW.app.threadPool.waitForDone(1000)


def test_initConfig_1(function):
    function.app.config["mainW"] = {}
    suc = function.initConfig()
    assert suc


def test_storeConfig_1(function):
    suc = function.storeConfig()
    assert suc


def test_setupGuiTools(function):
    suc = function.setupGuiTools()
    assert suc
    for _, ui in function.selectorsDropDowns.items():
        assert ui.count() == 7


def test_getNumberFiles_1(function):
    number = function.getNumberFiles()
    assert number == 0


def test_getNumberFiles_2(function):
    number = function.getNumberFiles(pathDir="/Users")
    assert number == 0


def test_getNumberFiles_3(function):
    number = function.getNumberFiles(pathDir="tests/testData", search="**/*.fit*")
    assert number > 0


def test_getNumberFiles_4(function):
    number = function.getNumberFiles(pathDir="/xxx", search="**/*.fit*")
    assert number == 0


def test_getNumberFiles_5(function):
    number = function.getNumberFiles(pathDir="tests/testData", search="**/star*.fit*")
    assert number == 3


def test_getNumberFiles_6(function):
    number = function.getNumberFiles(pathDir="tests/testData", search="star*.fit*")
    assert number == 3


def test_getNumberFiles_7(function):
    number = function.getNumberFiles(pathDir="tests/testData")
    assert number == 0


def test_convertHeaderEntry_1(function):
    chunk = function.convertHeaderEntry(entry="", fitsKey="1")
    assert not chunk


def test_convertHeaderEntry_2(function):
    chunk = function.convertHeaderEntry(entry="1", fitsKey="")
    assert not chunk


def test_convertHeaderEntry_3(function):
    chunk = function.convertHeaderEntry(
        entry="2019-05-26T17:02:18.843", fitsKey="DATE-OBS"
    )
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
    name = function.processSelectors(fitsHeader=header)
    assert not name


def test_processSelectors_2(function):
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header.set("DATE-OBS", "2019-05-26T17:02:18.843")
    name = function.processSelectors(fitsHeader=header, selection="Frame")
    assert not name


def test_processSelectors_3(function):
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header.set("DATE-OBS", "2019-05-26T17:02:18.843")
    name = function.processSelectors(fitsHeader=header, selection="Datetime")
    assert name == "2019-05-26_17-02-18"


def test_processSelectors_4(function):
    hdu = fits.HDUList()
    hdu.append(fits.PrimaryHDU())
    header = hdu[0].header
    header.set("DATE-OBS", "2019-05-26T17:02:18.843")
    name = function.processSelectors(selection="Datetime")
    assert not name


def test_renameFile_1(function):
    suc = function.renameFile()
    assert not suc


def test_renameFile_2(function):
    if os.path.isfile("tests/workDir/image/m51.fit"):
        os.remove("tests/workDir/image/m51.fit")
    suc = function.renameFile("tests/workDir/image/m51.fit")
    assert not suc


def test_renameFile_3(function):
    shutil.copy("tests/testData/m51.fit", "tests/workDir/image/m51.fit")

    with mock.patch.object(os, "rename"):
        suc = function.renameFile("tests/workDir/image/m51.fit")
        assert suc


def test_renameFile_4(function):
    shutil.copy("tests/testData/m51.fit", "tests/workDir/image/m51.fit")
    function.ui.newObjectName.setText("test")

    with mock.patch.object(os, "rename"):
        suc = function.renameFile("tests/workDir/image/m51.fit")
        assert suc


def test_renameFile_5(function):
    hdu = fits.PrimaryHDU(np.arange(100.0))
    hduList = fits.HDUList([hdu])
    function.ui.newObjectName.setText("")
    hduList.writeto("tests/workDir/image/m51.fit", overwrite=True)

    with mock.patch.object(os, "rename"):
        suc = function.renameFile("tests/workDir/image/m51.fit")
        assert suc


def test_renameFile_6(function):
    hdu = fits.PrimaryHDU(np.arange(100.0))
    hdu.header["FILTER"] = "test"
    hduList = fits.HDUList([hdu])
    hduList.writeto("tests/workDir/image/m51.fit", overwrite=True)

    function.ui.rename1.clear()
    function.ui.rename1.addItem("Filter")

    with mock.patch.object(os, "rename"):
        suc = function.renameFile("tests/workDir/image/m51.fit")
        assert suc


def test_renameRunGUI_1(function):
    shutil.copy("tests/testData/m51.fit", "tests/workDir/image/m51.fit")
    function.ui.renameDir.setText("")
    suc = function.renameRunGUI()
    assert not suc


def test_renameRunGUI_2(function):
    function.ui.renameDir.setText("tests/workDir/img")
    suc = function.renameRunGUI()
    assert not suc


def test_renameRunGUI_3(function):
    function.ui.includeSubdirs.setChecked(True)
    function.ui.renameDir.setText("tests/workDir/image")
    with mock.patch.object(function, "getNumberFiles", return_value=0):
        suc = function.renameRunGUI()
        assert not suc


def test_renameRunGUI_4(function):
    shutil.copy("tests/testData/m51.fit", "tests/workDir/image/m51.fit")
    function.ui.renameDir.setText("tests/workDir/image")
    function.ui.includeSubdirs.setChecked(False)
    with mock.patch.object(function, "renameFile", return_value=True):
        suc = function.renameRunGUI()
        assert suc


def test_renameRunGUI_5(function):
    shutil.copy("tests/testData/m51.fit", "tests/workDir/image/m51.fit")
    function.ui.renameDir.setText("tests/workDir/image")
    with mock.patch.object(function, "renameFile", return_value=False):
        suc = function.renameRunGUI()
        assert suc


def test_chooseDir_1(function):
    with mock.patch.object(MWidget, "openDir", return_value=("", "", "")):
        suc = function.chooseDir()
        assert suc


def test_chooseDir_2(function):
    with mock.patch.object(MWidget, "openDir", return_value=("test", "", "")):
        suc = function.chooseDir()
        assert suc
