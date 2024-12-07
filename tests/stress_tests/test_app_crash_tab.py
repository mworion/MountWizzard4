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
import os
import glob
import random

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
    "dataDir": "tests/workDir/data",
    "configDir": "tests/workDir/config",
    "workDir": "tests/workDir",
    "imageDir": "tests/workDir/image",
    "tempDir": "tests/workDir/temp",
    "measureDir": "tests/workDir/measure",
    "modelDir": "tests/workDir/model",
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
