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
import copy
import os
import glob
import random
import shutil
import json

# external packages
import pytest
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QThreadPool
from PyQt5.QtTest import QTest

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
            print(f)
            os.remove(f)
    extractDataFiles(mwGlob=mwglob)
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


def test_1(qtbot, qapp):
    # open all windows and close them
    def run():
        qapp.exec_()

    cfg = {"imageW": {
            "imageFileName": "tests/workdir/image/star1.fits",
        }
    }
    with open('tests/workDir/config/profile', 'w') as f:
        f.write('config.cfg')
    with open('tests/workDir/config/config.cfg', 'w') as f:
        json.dump(cfg, f, sort_keys=True, indent=4)

    shutil.copy('tests/testData/star1.fits', 'tests/workdir/image/star1.fits')
    app = MountWizzard4(mwGlob=mwglob, application=qapp)
    worker = Worker(run)
    tp.start(worker)
    qtbot.waitExposed(app.mainW, 1000)

    qtbot.mouseClick(app.mainW.ui.openImageW, Qt.LeftButton)
    imageW = app.uiWindows['showImageW']['classObj']
    qtbot.waitExposed(imageW, 1000)

    for i in range(1):
        name = f'star{i%1 + 1}.fits'
        imageW.ui.imageFileName.setText(name)
        app.showImage.emit(f'tests/workdir/image/star{i%1 + 1}.fits')

    qtbot.mouseClick(app.mainW.ui.saveConfigQuit, Qt.LeftButton)


def dddtest_1(qtbot, qapp):
    # open all windows and close them
    def run():
        qapp.exec_()

    app = MountWizzard4(mwGlob=mwglob, application=qapp)
    worker = Worker(run)
    tp.start(worker)
    qtbot.waitExposed(app.mainW, 1000)
    shutil.copy('tests/testData/m51.fit', 'tests/workdir/image/m51.fit')
    shutil.copy('tests/testData/star1.fits', 'tests/workdir/image/star1.fits')
    shutil.copy('tests/testData/star2.fits', 'tests/workdir/image/star2.fits')

    for i in range(1):
        qtbot.mouseClick(app.mainW.ui.openImageW, Qt.LeftButton)
        imageW = app.uiWindows['showImageW']['classObj']
        qtbot.waitExposed(imageW, 1000)
        imageW.ui.imageFileName.setText('m51.fit')
        app.showImage.emit('tests/workdir/image/m51.fit')
        QTest.qWait(1000)
        qtbot.mouseClick(app.mainW.ui.openImageW, Qt.LeftButton)
        QTest.qWait(1000)

    qtbot.mouseClick(app.mainW.ui.saveConfigQuit, Qt.LeftButton)
