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

import gc
import glob
import os
import pytest
import shutil
from mw4.base.bootstrap import extractDataFiles
from mw4.base.threadUtils import mainThreadSleep
from mw4.mainApp import MountWizzard4
from pathlib import Path
from PySide6.QtCore import Qt, QThreadPool
from random import randint

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
    imageW.ui.timeTagImage.setChecked(False)

    app.showImage.emit(Path("tests/work/image/star1.fits"))
    qtbot.wait(3000)

    TAB = [1, 4]
    gc.disable()
    for i in range(20):
        if randint(0, 1):
            imageW.ui.isoLayer.click()
            qtbot.wait(50)
        index = TAB[randint(0, 1)]
        imageW.ui.tabImage.setCurrentIndex(index)
        qtbot.wait(randint(50, 200))
    gc.enable()

    with qtbot.waitSignal(app.timeMgr.update10s, timeout=15000, raising=True):
        pass
