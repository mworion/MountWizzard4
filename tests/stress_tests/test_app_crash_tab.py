# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion

import glob
import os
import pytest
import random
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
    yield
    cleanupTestFiles()
    tp.waitForDone(1000)


def test_1(qtbot, qapp):
    # open all windows and close them
    app = MountWizzard4(mwGlob=mwglob, application=qapp, test=1)
    qtbot.waitExposed(app.mainW, timeout=1000)

    qtbot.mouseClick(app.mainW.ui.mainTabWidget, Qt.LeftButton)
    for index in range(50):
        index = int(random.random() * app.mainW.ui.mainTabWidget.count())
        app.mainW.ui.mainTabWidget.setCurrentIndex(index)
        index = int(random.random() * app.mainW.ui.settingsTabWidget.count())
        app.mainW.ui.settingsTabWidget.setCurrentIndex(index)
        QTest.qWait(100)
    qtbot.mouseClick(app.mainW.ui.isOnline, Qt.LeftButton)
    for index in range(50):
        index = int(random.random() * app.mainW.ui.mainTabWidget.count())
        app.mainW.ui.mainTabWidget.setCurrentIndex(index)
        index = int(random.random() * app.mainW.ui.settingsTabWidget.count())
        app.mainW.ui.settingsTabWidget.setCurrentIndex(index)
        QTest.qWait(100)
    qtbot.mouseClick(app.mainW.ui.mountHost, Qt.LeftButton)
    app.mainW.ui.mountHost.setText("192.168.2.15")
    qtbot.keyPress(app.mainW.ui.mountHost, "\r")
    for index in range(50):
        index = int(random.random() * app.mainW.ui.mainTabWidget.count())
        app.mainW.ui.mainTabWidget.setCurrentIndex(index)
        index = int(random.random() * app.mainW.ui.settingsTabWidget.count())
        app.mainW.ui.settingsTabWidget.setCurrentIndex(index)
        QTest.qWait(100)

    with qtbot.waitSignal(app.timeMgr.update10s, timeout=15000, raising=True):
        pass
