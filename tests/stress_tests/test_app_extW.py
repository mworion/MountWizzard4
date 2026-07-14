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
from mw4.gui.utilities.qtHelpers import sleepAndEvents
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
        path = Path(mwglob[d])
        path.mkdir(parents=True, exist_ok=True)
        files = glob.glob(f"{mwglob[d]}/*")
        if "modelData" in d:
            continue
        for f in files:
            if "empty" in f:
                continue
            if os.path.isfile(f):
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
            if os.path.isfile(f):
                os.remove(f)

    tp.waitForDone(3000)


def test_1(qtbot, qapp):
    app = MountWizzard4(mwGlob=mwglob, application=qapp, test=1)

    qtbot.waitExposed(app.mainW, timeout=1000)

    qtbot.mouseClick(app.mainW.ui.openAnalyseW, Qt.LeftButton)
    qtbot.waitExposed(
        app.mainW.externalWindows.uiWindows["showAnalyseW"]["classObj"], timeout=1000
    )

    qtbot.mouseClick(app.mainW.ui.openHemisphereW, Qt.LeftButton)
    qtbot.waitExposed(
        app.mainW.externalWindows.uiWindows["showHemisphereW"]["classObj"], timeout=1000
    )

    qtbot.mouseClick(app.mainW.ui.openImageW, Qt.LeftButton)
    qtbot.waitExposed(
        app.mainW.externalWindows.uiWindows["showImageW"]["classObj"], timeout=1000
    )

    qtbot.mouseClick(app.mainW.ui.openKeypadW, Qt.LeftButton)
    qtbot.waitExposed(
        app.mainW.externalWindows.uiWindows["showKeypadW"]["classObj"], timeout=1000
    )

    qtbot.mouseClick(app.mainW.ui.openMeasureW, Qt.LeftButton)
    qtbot.waitExposed(
        app.mainW.externalWindows.uiWindows["showMeasureW"]["classObj"], timeout=1000
    )

    qtbot.mouseClick(app.mainW.ui.openMessageW, Qt.LeftButton)
    qtbot.waitExposed(
        app.mainW.externalWindows.uiWindows["showMessageW"]["classObj"], timeout=1000
    )

    qtbot.mouseClick(app.mainW.ui.openSatelliteW, Qt.LeftButton)
    qtbot.waitExposed(
        app.mainW.externalWindows.uiWindows["showSatelliteW"]["classObj"], timeout=1000
    )

    with qtbot.waitSignal(app.timeMgr.update10s, timeout=15000, raising=True):
        pass


def test_2(qtbot, qapp):
    app = MountWizzard4(mwGlob=mwglob, application=qapp, test=1)

    qtbot.waitExposed(app.mainW, timeout=1000)

    qtbot.mouseClick(app.mainW.ui.openAnalyseW, Qt.LeftButton)
    qtbot.waitExposed(
        app.mainW.externalWindows.uiWindows["showAnalyseW"]["classObj"], timeout=1000
    )

    sleepAndEvents(1000)
    with qtbot.waitSignal(app.timeMgr.update10s, timeout=15000, raising=True):
        pass


def test_3(qtbot, qapp):
    app = MountWizzard4(mwGlob=mwglob, application=qapp, test=1)

    qtbot.waitExposed(app.mainW, timeout=1000)

    qtbot.mouseClick(app.mainW.ui.openHemisphereW, Qt.LeftButton)
    qtbot.waitExposed(
        app.mainW.externalWindows.uiWindows["showHemisphereW"]["classObj"], timeout=1000
    )

    sleepAndEvents(1000)
    with qtbot.waitSignal(app.timeMgr.update10s, timeout=15000, raising=True):
        pass


def test_4(qtbot, qapp):
    app = MountWizzard4(mwGlob=mwglob, application=qapp, test=1)

    qtbot.waitExposed(app.mainW, timeout=1000)

    qtbot.mouseClick(app.mainW.ui.openImageW, Qt.LeftButton)
    qtbot.waitExposed(
        app.mainW.externalWindows.uiWindows["showImageW"]["classObj"], timeout=1000
    )

    sleepAndEvents(1000)
    with qtbot.waitSignal(app.timeMgr.update10s, timeout=15000, raising=True):
        pass


def test_5(qtbot, qapp):
    app = MountWizzard4(mwGlob=mwglob, application=qapp, test=1)

    qtbot.waitExposed(app.mainW, timeout=1000)

    qtbot.mouseClick(app.mainW.ui.openKeypadW, Qt.LeftButton)
    qtbot.waitExposed(
        app.mainW.externalWindows.uiWindows["showKeypadW"]["classObj"], timeout=1000
    )

    sleepAndEvents(1000)
    with qtbot.waitSignal(app.timeMgr.update10s, timeout=15000, raising=True):
        pass


def test_6(qtbot, qapp):
    app = MountWizzard4(mwGlob=mwglob, application=qapp, test=1)

    qtbot.waitExposed(app.mainW, timeout=1000)

    qtbot.mouseClick(app.mainW.ui.openMeasureW, Qt.LeftButton)
    qtbot.waitExposed(
        app.mainW.externalWindows.uiWindows["showMeasureW"]["classObj"], timeout=1000
    )

    sleepAndEvents(1000)
    with qtbot.waitSignal(app.timeMgr.update10s, timeout=15000, raising=True):
        pass


def test_7(qtbot, qapp):
    app = MountWizzard4(mwGlob=mwglob, application=qapp, test=1)

    qtbot.waitExposed(app.mainW, timeout=1000)

    qtbot.mouseClick(app.mainW.ui.openMessageW, Qt.LeftButton)
    qtbot.waitExposed(
        app.mainW.externalWindows.uiWindows["showMessageW"]["classObj"], timeout=1000
    )

    sleepAndEvents(1000)
    with qtbot.waitSignal(app.timeMgr.update10s, timeout=15000, raising=True):
        pass


def test_8(qtbot, qapp):
    app = MountWizzard4(mwGlob=mwglob, application=qapp, test=1)

    qtbot.waitExposed(app.mainW, timeout=1000)

    qtbot.mouseClick(app.mainW.ui.openSatelliteW, Qt.LeftButton)
    qtbot.waitExposed(
        app.mainW.externalWindows.uiWindows["showSatelliteW"]["classObj"],
        timeout=1000,
    )

    sleepAndEvents(1000)
    with qtbot.waitSignal(app.timeMgr.update10s, timeout=15000, raising=True):
        pass
