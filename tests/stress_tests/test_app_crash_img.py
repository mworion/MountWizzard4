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

import glob
import os
import pytest
import shutil
from mw4.base.bootstrap import extractDataFiles
from mw4.base.threadUtils import mainThreadSleep
from mw4.mainApp import MountWizzard4
from pathlib import Path
from PySide6.QtCore import Qt, QThreadPool

mwglob = {
    "dataDir": Path("tests/work/assets"),
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
            if os.path.isfile(f):
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
            if os.path.isfile(f):
                os.remove(f)
    tp.waitForDone(1000)


def test_showImages(qtbot, qapp):
    # open all windows and close them
    app = MountWizzard4(mwGlob=mwglob, application=qapp, test=1)
    app.mainW.move(100, 100)
    qtbot.waitExposed(app.mainW, timeout=1000)

    qtbot.mouseClick(app.mainW.ui.openImageW, Qt.LeftButton)
    imageW = app.mainW.externalWindows.uiWindows["showImageW"]["classObj"]
    imageW.move(900, 100)
    qtbot.waitExposed(imageW, timeout=1000)

    for i in range(50):
        app.showImage.emit(f"tests/work/image/star{i % 3 + 1}.fits")
        mainThreadSleep(500)

    with qtbot.waitSignal(app.timeMgr.update10s, timeout=15000, raising=True):
        pass


def test_showImagesPhotometry(qtbot, qapp):
    # open all windows and close them
    app = MountWizzard4(mwGlob=mwglob, application=qapp, test=1)
    app.mainW.move(100, 100)
    qtbot.waitExposed(app.mainW, timeout=1000)

    qtbot.mouseClick(app.mainW.ui.openImageW, Qt.LeftButton)
    imageW = app.mainW.externalWindows.uiWindows["showImageW"]["classObj"]
    imageW.move(900, 100)

    qtbot.waitExposed(imageW, timeout=1000)
    imageW.ui.photometryGroup.setChecked(True)

    for i in range(50):
        app.showImage.emit(f"tests/work/image/star{i % 3 + 1}.fits")
        mainThreadSleep(1000)

    with qtbot.waitSignal(app.timeMgr.update10s, timeout=15000, raising=True):
        pass


def test_showImagesPhotometryN(qtbot, qapp):
    # open all windows and close them
    app = MountWizzard4(mwGlob=mwglob, application=qapp, test=1)
    app.mainW.move(100, 100)
    qtbot.waitExposed(app.mainW, timeout=1000)

    qtbot.mouseClick(app.mainW.ui.openImageW, Qt.LeftButton)
    imageW = app.mainW.externalWindows.uiWindows["showImageW"]["classObj"]
    imageW.move(900, 100)

    qtbot.waitExposed(imageW, timeout=1000)
    imageW.ui.photometryGroup.setChecked(True)

    qtbot.mouseClick(imageW.ui.exposeN, Qt.LeftButton)
    mainThreadSleep(3000)
    qtbot.mouseClick(imageW.ui.abortExpose, Qt.LeftButton)

    with qtbot.waitSignal(app.timeMgr.update10s, timeout=15000, raising=True):
        pass
