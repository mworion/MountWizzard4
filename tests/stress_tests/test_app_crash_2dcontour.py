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
# GUI with PyQT5 for python
#
# written in python3, (c) 2019-2022 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import os
import glob
import shutil

# external packages
import pytest
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QThreadPool
from PyQt5.QtTest import QTest
from random import randint

# local import
from mainApp import MountWizzard4
from base.tpool import Worker
from loader import extractDataFiles
from resource import resources


mwglob = {'dataDir': 'tests/workDir/data',
          'configDir': 'tests/workDir/config',
          'workDir': 'tests/workDir',
          'imageDir': 'tests/workDir/image',
          'tempDir': 'tests/workDir/temp',
          'measureDir': 'tests/workDir/measure',
          'modelDir': 'tests/workDir/model',
          'modelData': '4.0'
          }


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global tp

    tp = QThreadPool()
    for d in mwglob:
        files = glob.glob(f'{mwglob[d]}/*.*')
        if 'modelData' in d:
            continue
        for f in files:
            if 'empty' in f:
                continue
            os.remove(f)
    extractDataFiles(mwGlob=mwglob)
    shutil.copy('tests/testData/star1.fits', 'tests/workDir/image/star1.fits')

    yield
    for d in mwglob:
        files = glob.glob(f'{mwglob[d]}/*.*')
        if 'modelData' in d:
            continue
        for f in files:
            if 'empty' in f:
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
    imageW = app.uiWindows['showImageW']['classObj']
    imageW.move(900, 100)

    qtbot.mouseClick(app.mainW.ui.openMessageW, Qt.LeftButton)
    messageW = app.uiWindows['showMessageW']['classObj']
    messageW.move(1700, 100)

    qtbot.waitExposed(imageW, timeout=1000)
    qtbot.waitExposed(messageW, timeout=1000)
    imageW.ui.photometryGroup.setChecked(True)
    imageW.ui.timeTagImage.setChecked(False)

    for i in range(20):
        imageW.ui.isoLayer.setChecked(randint(0, 1))
        imageW.ui.tabImage.setCurrentIndex(0)
        app.showImage.emit('tests/workDir/image/star1.fits')
        QTest.qWait(randint(50, 2000))
        imageW.ui.tabImage.setCurrentIndex(1)
        QTest.qWait(randint(50, 2000))
        for j in range(9):
            imageW.ui.tabImage.setCurrentIndex(j)
            QTest.qWait(randint(20, 50))
        imageW.ui.tabImage.setCurrentIndex(0)

    QTest.qWait(1000)
    qtbot.mouseClick(app.mainW.ui.saveConfigQuit, Qt.LeftButton)
