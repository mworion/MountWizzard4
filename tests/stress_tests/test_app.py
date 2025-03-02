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

# external packages
import pytest
from PySide6.QtCore import Qt
from PySide6.QtCore import QThreadPool

# local import
from mainApp import MountWizzard4
from base.tpool import Worker
from loader import extractDataFiles


mwglob = {
    "dataDir": "tests/work/data",
    "configDir": "tests/work/config",
    "workDir": "mw4/workDir",
    "imageDir": "tests/work/image",
    "tempDir": "tests/work/temp",
    "measureDir": "tests/work/measure",
    "modelDir": "tests/work/model",
    "modelData": "4.0",
}


@pytest.fixture(autouse=True, scope="function")
def module_setup_teardown():
    global tp

    tp = QThreadPool()

    for d in mwglob:
        files = glob.glob(f"{mwglob[d]}/*")
        if "modelData" in d:
            continue
        for f in files:
            if "empty" in f:
                continue
            os.remove(f)

    extractDataFiles(mwGlob=mwglob)

    yield

    for d in mwglob:
        files = glob.glob(f"{mwglob[d]}/*")
        if "modelData" in d:
            continue
        for f in files:
            if "empty" in f:
                continue
            os.remove(f)

    tp.waitForDone(3000)


def test_1(qtbot, qapp):
    # open all windows and close them
    def run():
        qapp.exec_()

    app = MountWizzard4(mwGlob=mwglob, application=qapp)

    worker = Worker(run)
    tp.start(worker)
    qtbot.waitExposed(app.mainW, timeout=1000)

    qtbot.mouseClick(app.mainW.ui.openAnalyseW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows["showAnalyseW"]["classObj"], timeout=1000)

    qtbot.mouseClick(app.mainW.ui.openHemisphereW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows["showHemisphereW"]["classObj"], timeout=1000)

    qtbot.mouseClick(app.mainW.ui.openImageW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows["showImageW"]["classObj"], timeout=1000)

    qtbot.mouseClick(app.mainW.ui.openKeypadW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows["showKeypadW"]["classObj"], timeout=1000)

    qtbot.mouseClick(app.mainW.ui.openMeasureW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows["showMeasureW"]["classObj"], timeout=1000)

    qtbot.mouseClick(app.mainW.ui.openMessageW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows["showMessageW"]["classObj"], timeout=1000)

    qtbot.mouseClick(app.mainW.ui.openSatelliteW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows["showSatelliteW"]["classObj"], timeout=1000)

    qtbot.mouseClick(app.mainW.ui.saveConfigQuit, Qt.LeftButton)


def test_2(qtbot, qapp):
    # Profile load / save
    # Open hemisphere and select all stars
    # open hemisphere and add horizon point / model point
    # get online and check if environment is present
    # select satellite open sat window
    # select indi camera simulator and open image window expose one image
    # select astap and solve on image
    # Rename images from tool
    # choosing simulation drivers
    # changing simulation drivers
    # Setting drivers
    # connect / disconnect ascom
    # updating mw
    pass
