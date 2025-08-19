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
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import os
import glob
import shutil
from pathlib import Path

# external packages
import pytest
from PySide6.QtCore import Qt
from PySide6.QtCore import QThreadPool
from PySide6.QtTest import QTest

# local import
from mainApp import MountWizzard4
from base.tpool import Worker
from loader import extractDataFiles


mwglob = {
    "dataDir": Path("tests/work/data"),
    "configDir": Path("tests/work/config"),
    "workDir": Path("tests/work"),
    "imageDir": Path("tests/work/image"),
    "tempDir": Path("tests/work/temp"),
    "measureDir": Path("tests/work/measure"),
    "modelDir": Path("tests/work/model"),
    "modelData": "4.0",
}


@pytest.fixture(autouse=True, scope="function")
def module_setup_teardown():
    global tp

    tp = QThreadPool()
    for d in mwglob:
        files = glob.glob(f"{mwglob[d]}/*.*")
        if "modelData" in d:
            continue
        for f in files:
            if "empty" in f:
                continue
            os.remove(f)
    extractDataFiles(mwGlob=mwglob)
    shutil.copy("tests/testData/star1.fits", "tests/work/image/star1.fits")
    shutil.copy("tests/testData/star2.fits", "tests/work/image/star2.fits")
    shutil.copy("tests/testData/star3.fits", "tests/work/image/star3.fits")

    yield
    for d in mwglob:
        files = glob.glob(f"{mwglob[d]}/*.*")
        if "modelData" in d:
            continue
        for f in files:
            if "empty" in f:
                continue
            os.remove(f)
    tp.waitForDone(1000)


def test_showImages(qtbot, qapp):
    # open all windows and close them
    def run():
        qapp.exec_()

    app = MountWizzard4(mwGlob=mwglob, application=qapp)
    worker = Worker(run)
    tp.start(worker)
    app.mainW.move(100, 100)
    qtbot.waitExposed(app.mainW, timeout=1000)

    qtbot.mouseClick(app.mainW.ui.openImageW, Qt.LeftButton)
    imageW = app.mainW.externalWindows.uiWindows["showImageW"]["classObj"]
    imageW.move(900, 100)
    qtbot.waitExposed(imageW, timeout=1000)

    for i in range(50):
        app.showImage.emit(f"tests/work/image/star{i % 3 + 1}.fits")
        QTest.qWait(500)

    QTest.qWait(1000)
    qtbot.mouseClick(app.mainW.ui.saveConfigQuit, Qt.LeftButton)


def test_showImagesPhotometry(qtbot, qapp):
    # open all windows and close them
    def run():
        qapp.exec_()

    app = MountWizzard4(mwGlob=mwglob, application=qapp)
    worker = Worker(run)
    tp.start(worker)
    app.mainW.move(100, 100)
    qtbot.waitExposed(app.mainW, timeout=1000)

    qtbot.mouseClick(app.mainW.ui.openImageW, Qt.LeftButton)
    imageW = app.uiWindows["showImageW"]["classObj"]
    imageW.move(900, 100)

    qtbot.waitExposed(imageW, timeout=1000)
    imageW.ui.photometryGroup.setChecked(True)

    for i in range(50):
        app.showImage.emit(f"tests/work/image/star{i % 3 + 1}.fits")
        QTest.qWait(1000)

    QTest.qWait(1000)
    qtbot.mouseClick(app.mainW.ui.saveConfigQuit, Qt.LeftButton)


def test_showImagesPhotometryN(qtbot, qapp):
    # open all windows and close them
    def run():
        qapp.exec_()

    app = MountWizzard4(mwGlob=mwglob, application=qapp)
    worker = Worker(run)
    tp.start(worker)
    app.mainW.move(100, 100)
    qtbot.waitExposed(app.mainW, timeout=1000)

    qtbot.mouseClick(app.mainW.ui.openImageW, Qt.LeftButton)
    imageW = app.uiWindows["showImageW"]["classObj"]
    imageW.move(900, 100)

    qtbot.waitExposed(imageW, timeout=1000)
    imageW.ui.photometryGroup.setChecked(True)

    qtbot.mouseClick(imageW.ui.exposeN, Qt.LeftButton)
    QTest.qWait(3000)
    qtbot.mouseClick(imageW.ui.abortExpose, Qt.LeftButton)

    QTest.qWait(1000)
    qtbot.mouseClick(app.mainW.ui.saveConfigQuit, Qt.LeftButton)
