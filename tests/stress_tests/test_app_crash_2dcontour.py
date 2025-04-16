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
from random import randint
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
    "configDir":  Path("tests/work/config"),
    "workDir":  Path("tests/work"),
    "imageDir":  Path("tests/work/image"),
    "tempDir":  Path("tests/work/temp"),
    "measureDir":  Path("tests/work/measure"),
    "modelDir":  Path("tests/work/model"),
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
    imageW = app.mainW.externalWindows.uiWindows["showImageW"]["classObj"]
    imageW.move(900, 100)

    qtbot.waitExposed(imageW, timeout=1000)
    imageW.ui.photometryGroup.setChecked(True)
    imageW.ui.timeTagImage.setChecked(False)
    app.showImage.emit("tests/work/image/star1.fits")
    TAB = [1, 4]

    for i in range(20):
        if randint(0, 1):
            qtbot.mouseClick(imageW.ui.isoLayer, Qt.LeftButton)
        index = TAB[randint(0, 1)]
        imageW.ui.tabImage.setCurrentIndex(index)
        QTest.qWait(randint(50, 500))

    QTest.qWait(5000)
    qtbot.mouseClick(app.mainW.ui.saveConfigQuit, Qt.LeftButton)
