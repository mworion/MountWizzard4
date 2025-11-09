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
# standard libraries
import glob
import os
from pathlib import Path

# external packages
import pytest
from mw4.loader import extractDataFiles

# local import
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

tp = QThreadPool()


@pytest.fixture(autouse=True, scope="function")
def module_setup_teardown():
    global tp

    for d in mwglob:
        files = glob.glob(f"{mwglob[d]}/*.*")
        if "modelData" in d:
            continue
        for f in files:
            if "empty" in f:
                continue
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

    tp.waitForDone(3000)


def test_configAlpaca(qtbot, qapp):
    def run():
        qapp.exec_()

    app = MountWizzard4(mwGlob=mwglob, application=qapp)

    worker = Worker(run)
    tp.start(worker)
    qtbot.waitExposed(app.mainW, timeout=1000)

    qtbot.mouseClick(app.mainW.ui.cameraSetup, Qt.LeftButton)
    popup = app.mainW.popupUi
    qtbot.waitExposed(popup, timeout=1000)
    popup.ui.tab.setCurrentIndex(0)
    QTest.qWait(1000)

    popup.ui.alpacaHostAddress.setText("192.168.2.211")
    popup.ui.alpacaPort.setText("11111")
    popup.ui.alpacaCopyConfig.setChecked(True)
    qtbot.mouseClick(popup.ui.alpacaDiscover, Qt.LeftButton)
    QTest.qWait(1000)
    qtbot.mouseClick(popup.ui.ok, Qt.LeftButton)

    qtbot.mouseClick(app.mainW.ui.saveConfigQuit, Qt.LeftButton)
