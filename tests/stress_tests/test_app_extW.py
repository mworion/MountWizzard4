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
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import os
import glob
import pytest

# external packages
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QThreadPool

# local import
from gui.utilities.toolsQtWidget import sleepAndEvents
from mainApp import MountWizzard4
from base.tpool import Worker
from loader import extractDataFiles
from resource import resources


mwglob = {'dataDir': 'tests/workDir/data',
          'configDir': 'tests/workDir/config',
          'workDir': 'mw4/workDir',
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
        files = glob.glob(f'{mwglob[d]}/*')
        if 'modelData' in d:
            continue
        for f in files:
            if 'empty' in f:
                continue
            os.remove(f)

    extractDataFiles(mwGlob=mwglob)

    yield

    for d in mwglob:
        files = glob.glob(f'{mwglob[d]}/*')
        if 'modelData' in d:
            continue
        for f in files:
            if 'empty' in f:
                continue
            os.remove(f)

    tp.waitForDone(3000)


def test_1(qtbot, qapp):
    def run():
        qapp.exec_()

    app = MountWizzard4(mwGlob=mwglob, application=qapp)

    worker = Worker(run)
    tp.start(worker)
    qtbot.waitExposed(app.mainW, timeout=1000)

    qtbot.mouseClick(app.mainW.ui.openAnalyseW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showAnalyseW']['classObj'], timeout=1000)

    qtbot.mouseClick(app.mainW.ui.openHemisphereW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showHemisphereW']['classObj'], timeout=1000)

    qtbot.mouseClick(app.mainW.ui.openImageW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showImageW']['classObj'], timeout=1000)

    qtbot.mouseClick(app.mainW.ui.openKeypadW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showKeypadW']['classObj'], timeout=1000)

    qtbot.mouseClick(app.mainW.ui.openMeasureW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showMeasureW']['classObj'], timeout=1000)

    qtbot.mouseClick(app.mainW.ui.openMessageW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showMessageW']['classObj'], timeout=1000)

    qtbot.mouseClick(app.mainW.ui.openSatelliteW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showSatelliteW']['classObj'], timeout=1000)

    sleepAndEvents(1000)
    qtbot.mouseClick(app.mainW.ui.saveConfigQuit, Qt.LeftButton)


def test_2(qtbot, qapp):
    def run():
        qapp.exec_()

    app = MountWizzard4(mwGlob=mwglob, application=qapp)

    worker = Worker(run)
    tp.start(worker)
    qtbot.waitExposed(app.mainW, timeout=1000)

    qtbot.mouseClick(app.mainW.ui.openAnalyseW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showAnalyseW']['classObj'], timeout=1000)

    sleepAndEvents(1000)
    qtbot.mouseClick(app.mainW.ui.saveConfigQuit, Qt.LeftButton)


def test_3(qtbot, qapp):
    def run():
        qapp.exec_()

    app = MountWizzard4(mwGlob=mwglob, application=qapp)

    worker = Worker(run)
    tp.start(worker)
    qtbot.waitExposed(app.mainW, timeout=1000)

    qtbot.mouseClick(app.mainW.ui.openHemisphereW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showHemisphereW']['classObj'], timeout=1000)

    sleepAndEvents(1000)
    qtbot.mouseClick(app.mainW.ui.saveConfigQuit, Qt.LeftButton)


def test_4(qtbot, qapp):
    def run():
        qapp.exec_()

    app = MountWizzard4(mwGlob=mwglob, application=qapp)

    worker = Worker(run)
    tp.start(worker)
    qtbot.waitExposed(app.mainW, timeout=1000)

    qtbot.mouseClick(app.mainW.ui.openImageW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showImageW']['classObj'], timeout=1000)

    sleepAndEvents(1000)
    qtbot.mouseClick(app.mainW.ui.saveConfigQuit, Qt.LeftButton)


def test_5(qtbot, qapp):
    def run():
        qapp.exec_()

    app = MountWizzard4(mwGlob=mwglob, application=qapp)

    worker = Worker(run)
    tp.start(worker)
    qtbot.waitExposed(app.mainW, timeout=1000)

    qtbot.mouseClick(app.mainW.ui.openKeypadW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showKeypadW']['classObj'], timeout=1000)

    sleepAndEvents(1000)
    qtbot.mouseClick(app.mainW.ui.saveConfigQuit, Qt.LeftButton)


def test_6(qtbot, qapp):
    def run():
        qapp.exec_()

    app = MountWizzard4(mwGlob=mwglob, application=qapp)

    worker = Worker(run)
    tp.start(worker)
    qtbot.waitExposed(app.mainW, timeout=1000)

    qtbot.mouseClick(app.mainW.ui.openMeasureW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showMeasureW']['classObj'], timeout=1000)

    sleepAndEvents(1000)
    qtbot.mouseClick(app.mainW.ui.saveConfigQuit, Qt.LeftButton)


def test_7(qtbot, qapp):
    def run():
        qapp.exec_()

    app = MountWizzard4(mwGlob=mwglob, application=qapp)

    worker = Worker(run)
    tp.start(worker)
    qtbot.waitExposed(app.mainW, timeout=1000)

    qtbot.mouseClick(app.mainW.ui.openMessageW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showMessageW']['classObj'], timeout=1000)

    sleepAndEvents(1000)
    qtbot.mouseClick(app.mainW.ui.saveConfigQuit, Qt.LeftButton)


def test_8(qtbot, qapp):
    def run():
        qapp.exec_()

    app = MountWizzard4(mwGlob=mwglob, application=qapp)

    worker = Worker(run)
    tp.start(worker)
    qtbot.waitExposed(app.mainW, timeout=1000)

    qtbot.mouseClick(app.mainW.ui.openSatelliteW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showSatelliteW']['classObj'], timeout=1000)

    sleepAndEvents(1000)
    qtbot.mouseClick(app.mainW.ui.saveConfigQuit, Qt.LeftButton)
