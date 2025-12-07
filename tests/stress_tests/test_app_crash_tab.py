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
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################

import glob
import os
import random
from pathlib import Path


import pytest
from mw4.loader import extractDataFiles


from mw4.mainApp import MountWizzard4
from PySide6.QtCore import Qt, QThreadPool
from PySide6.QtTest import QTest

from mw4.base.tpool import Worker

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
            print(f)
            os.remove(f)
    extractDataFiles(mwGlob=mwglob)
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


def test_1(qtbot, qapp):
    # open all windows and close them
    def run():
        qapp.exec_()

    app = MountWizzard4(mwGlob=mwglob, application=qapp)
    worker = Worker(run)
    tp.start(worker)
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

    QTest.qWait(1000)
    qtbot.mouseClick(app.mainW.ui.saveConfigQuit, Qt.LeftButton)
