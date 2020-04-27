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
# Python  v3.7.5
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages
import pytest
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QThreadPool
from PyQt5.QtTest import QTest
import faulthandler
faulthandler.enable()

# local import
from mw4.mainApp import MountWizzard4
from mw4.base.tpool import Worker
from mw4.resource import resources


mwglob = {'dataDir': 'mw4/test/data',
          'configDir': 'mw4/test/config',
          'workDir': 'mw4/test',
          'imageDir': 'mw4/test/image',
          'tempDir': 'mw4/test/temp',
          'modelDir': 'mw4/test/model',
          'modelData': '4.0'
          }


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global tp

    tp = QThreadPool()

    yield

    tp.waitForDone(1000)


def test_1(qtbot, qapp):
    def run():
        qapp.exec_()

    app = MountWizzard4(mwGlob=mwglob, application=qapp)
    qtbot.add_widget(app.mainW)

    worker = Worker(run)
    tp.start(worker)
    qtbot.waitExposed(app.mainW, 1000)

    qtbot.mouseClick(app.mainW.ui.openMessageW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showMessageW']['classObj'], 1000)
    qtbot.mouseClick(app.mainW.ui.openImageW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showImageW']['classObj'], 1000)
    qtbot.mouseClick(app.mainW.ui.openHemisphereW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showHemisphereW']['classObj'], 1000)
    qtbot.mouseClick(app.mainW.ui.openMeasureW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showMeasureW']['classObj'], 1000)
    qtbot.mouseClick(app.mainW.ui.openSatelliteW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showSatelliteW']['classObj'], 1000)
    QTest.qWait(1000)
    qtbot.mouseClick(app.mainW.ui.saveConfigQuit, Qt.LeftButton)


def test_2(qtbot, qapp):
    def run():
        qapp.exec_()

    app = MountWizzard4(mwGlob=mwglob, application=qapp)
    qtbot.add_widget(app.mainW)

    worker = Worker(run)
    tp.start(worker)
    qtbot.waitExposed(app.mainW, 1000)

    qtbot.mouseClick(app.mainW.ui.openMessageW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showMessageW']['classObj'], 1000)
    qtbot.mouseClick(app.mainW.ui.openImageW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showImageW']['classObj'], 1000)
    qtbot.mouseClick(app.mainW.ui.openHemisphereW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showHemisphereW']['classObj'], 1000)
    qtbot.mouseClick(app.mainW.ui.openMeasureW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showMeasureW']['classObj'], 1000)
    qtbot.mouseClick(app.mainW.ui.openSatelliteW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showSatelliteW']['classObj'], 1000)
    QTest.qWait(1000)
    qtbot.mouseClick(app.mainW.ui.saveConfigQuit, Qt.LeftButton)


def test_3(qtbot, qapp):
    def run():
        qapp.exec_()

    app = MountWizzard4(mwGlob=mwglob, application=qapp)
    qtbot.add_widget(app.mainW)

    worker = Worker(run)
    tp.start(worker)
    qtbot.waitExposed(app.mainW, 1000)

    qtbot.mouseClick(app.mainW.ui.openMessageW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showMessageW']['classObj'], 1000)
    qtbot.mouseClick(app.mainW.ui.openImageW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showImageW']['classObj'], 1000)
    qtbot.mouseClick(app.mainW.ui.openHemisphereW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showHemisphereW']['classObj'], 1000)
    qtbot.mouseClick(app.mainW.ui.openMeasureW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showMeasureW']['classObj'], 1000)
    qtbot.mouseClick(app.mainW.ui.openSatelliteW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showSatelliteW']['classObj'], 1000)
    QTest.qWait(1000)
    qtbot.mouseClick(app.mainW.ui.saveConfigQuit, Qt.LeftButton)


def test_4(qtbot, qapp):
    def run():
        qapp.exec_()

    app = MountWizzard4(mwGlob=mwglob, application=qapp)
    qtbot.add_widget(app.mainW)

    worker = Worker(run)
    tp.start(worker)
    qtbot.waitExposed(app.mainW, 1000)

    qtbot.mouseClick(app.mainW.ui.openMessageW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showMessageW']['classObj'], 1000)
    qtbot.mouseClick(app.mainW.ui.openImageW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showImageW']['classObj'], 1000)
    qtbot.mouseClick(app.mainW.ui.openHemisphereW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showHemisphereW']['classObj'], 1000)
    qtbot.mouseClick(app.mainW.ui.openMeasureW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showMeasureW']['classObj'], 1000)
    qtbot.mouseClick(app.mainW.ui.openSatelliteW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showSatelliteW']['classObj'], 1000)
    QTest.qWait(1000)
    qtbot.mouseClick(app.mainW.ui.saveConfigQuit, Qt.LeftButton)


def test_5(qtbot, qapp):
    def run():
        qapp.exec_()

    app = MountWizzard4(mwGlob=mwglob, application=qapp)
    qtbot.add_widget(app.mainW)

    worker = Worker(run)
    tp.start(worker)
    qtbot.waitExposed(app.mainW, 1000)

    qtbot.mouseClick(app.mainW.ui.openMessageW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showMessageW']['classObj'], 1000)
    qtbot.mouseClick(app.mainW.ui.openImageW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showImageW']['classObj'], 1000)
    qtbot.mouseClick(app.mainW.ui.openHemisphereW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showHemisphereW']['classObj'], 1000)
    qtbot.mouseClick(app.mainW.ui.openMeasureW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showMeasureW']['classObj'], 1000)
    qtbot.mouseClick(app.mainW.ui.openSatelliteW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showSatelliteW']['classObj'], 1000)
    QTest.qWait(1000)
    qtbot.mouseClick(app.mainW.ui.saveConfigQuit, Qt.LeftButton)


def test_6(qtbot, qapp):
    def run():
        qapp.exec_()

    app = MountWizzard4(mwGlob=mwglob, application=qapp)
    qtbot.add_widget(app.mainW)

    worker = Worker(run)
    tp.start(worker)
    qtbot.waitExposed(app.mainW, 1000)

    qtbot.mouseClick(app.mainW.ui.openMessageW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showMessageW']['classObj'], 1000)
    qtbot.mouseClick(app.mainW.ui.openImageW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showImageW']['classObj'], 1000)
    qtbot.mouseClick(app.mainW.ui.openHemisphereW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showHemisphereW']['classObj'], 1000)
    qtbot.mouseClick(app.mainW.ui.openMeasureW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showMeasureW']['classObj'], 1000)
    qtbot.mouseClick(app.mainW.ui.openSatelliteW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showSatelliteW']['classObj'], 1000)
    QTest.qWait(1000)
    qtbot.mouseClick(app.mainW.ui.saveConfigQuit, Qt.LeftButton)


def test_7(qtbot, qapp):
    def run():
        qapp.exec_()

    app = MountWizzard4(mwGlob=mwglob, application=qapp)
    qtbot.add_widget(app.mainW)

    worker = Worker(run)
    tp.start(worker)
    qtbot.waitExposed(app.mainW, 1000)

    qtbot.mouseClick(app.mainW.ui.openMessageW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showMessageW']['classObj'], 1000)
    qtbot.mouseClick(app.mainW.ui.openImageW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showImageW']['classObj'], 1000)
    qtbot.mouseClick(app.mainW.ui.openHemisphereW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showHemisphereW']['classObj'], 1000)
    qtbot.mouseClick(app.mainW.ui.openMeasureW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showMeasureW']['classObj'], 1000)
    qtbot.mouseClick(app.mainW.ui.openSatelliteW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showSatelliteW']['classObj'], 1000)
    QTest.qWait(1000)
    qtbot.mouseClick(app.mainW.ui.saveConfigQuit, Qt.LeftButton)


def test_8(qtbot, qapp):
    def run():
        qapp.exec_()

    app = MountWizzard4(mwGlob=mwglob, application=qapp)
    qtbot.add_widget(app.mainW)

    worker = Worker(run)
    tp.start(worker)
    qtbot.waitExposed(app.mainW, 1000)

    qtbot.mouseClick(app.mainW.ui.openMessageW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showMessageW']['classObj'], 1000)
    qtbot.mouseClick(app.mainW.ui.openImageW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showImageW']['classObj'], 1000)
    qtbot.mouseClick(app.mainW.ui.openHemisphereW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showHemisphereW']['classObj'], 1000)
    qtbot.mouseClick(app.mainW.ui.openMeasureW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showMeasureW']['classObj'], 1000)
    qtbot.mouseClick(app.mainW.ui.openSatelliteW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showSatelliteW']['classObj'], 1000)
    QTest.qWait(1000)
    qtbot.mouseClick(app.mainW.ui.saveConfigQuit, Qt.LeftButton)


def test_9(qtbot, qapp):
    def run():
        qapp.exec_()

    app = MountWizzard4(mwGlob=mwglob, application=qapp)
    qtbot.add_widget(app.mainW)

    worker = Worker(run)
    tp.start(worker)
    qtbot.waitExposed(app.mainW, 1000)

    qtbot.mouseClick(app.mainW.ui.openMessageW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showMessageW']['classObj'], 1000)
    qtbot.mouseClick(app.mainW.ui.openImageW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showImageW']['classObj'], 1000)
    qtbot.mouseClick(app.mainW.ui.openHemisphereW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showHemisphereW']['classObj'], 1000)
    qtbot.mouseClick(app.mainW.ui.openMeasureW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showMeasureW']['classObj'], 1000)
    qtbot.mouseClick(app.mainW.ui.openSatelliteW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showSatelliteW']['classObj'], 1000)
    QTest.qWait(1000)
    qtbot.mouseClick(app.mainW.ui.saveConfigQuit, Qt.LeftButton)


def test_10(qtbot, qapp):
    def run():
        qapp.exec_()

    app = MountWizzard4(mwGlob=mwglob, application=qapp)
    qtbot.add_widget(app.mainW)

    worker = Worker(run)
    tp.start(worker)
    qtbot.waitExposed(app.mainW, 1000)

    qtbot.mouseClick(app.mainW.ui.openMessageW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showMessageW']['classObj'], 1000)
    qtbot.mouseClick(app.mainW.ui.openImageW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showImageW']['classObj'], 1000)
    qtbot.mouseClick(app.mainW.ui.openHemisphereW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showHemisphereW']['classObj'], 1000)
    qtbot.mouseClick(app.mainW.ui.openMeasureW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showMeasureW']['classObj'], 1000)
    qtbot.mouseClick(app.mainW.ui.openSatelliteW, Qt.LeftButton)
    qtbot.waitExposed(app.uiWindows['showSatelliteW']['classObj'], 1000)
    QTest.qWait(1000)
    qtbot.mouseClick(app.mainW.ui.saveConfigQuit, Qt.LeftButton)

