# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion

import glob
import os
import pytest
import shutil
from mw4.base.bootstrap import extractDataFiles
from mw4.mainApp import MountWizzard4
from pathlib import Path
from PySide6.QtCore import Qt, QThreadPool
from PySide6.QtTest import QTest

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


def cleanupTestFiles() -> None:
    """Clean up test files from work directories."""
    for d, path in mwglob.items():
        if "modelData" in d:
            continue
        files = glob.glob(f"{path}/*.*")
        for f in files:
            if "empty" not in f and os.path.isfile(f):
                os.remove(f)


@pytest.fixture(autouse=True, scope="module")
def module_setup_teardown():
    global tp

    tp = QThreadPool()
    cleanupTestFiles()
    extractDataFiles(mwGlob=mwglob)
    shutil.copy("tests/testData/star1.fits", "tests/work/image/star1.fits")
    shutil.copy("tests/testData/star2.fits", "tests/work/image/star2.fits")
    shutil.copy("tests/testData/star3.fits", "tests/work/image/star3.fits")

    yield
    cleanupTestFiles()
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
        QTest.qWait(500)

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
        QTest.qWait(1000)

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

    imageW.ui.continous.setChecked(True)
    qtbot.mouseClick(imageW.ui.expose, Qt.LeftButton)
    QTest.qWait(3000)
    qtbot.mouseClick(imageW.ui.abortExpose, Qt.LeftButton)

    with qtbot.waitSignal(app.timeMgr.update10s, timeout=15000, raising=True):
        pass
