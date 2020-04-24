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
import unittest.mock as mock

# external packages
import pytest
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QThreadPool
from PyQt5.QtTest import QTest

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
    del tp


def test_1(qtbot, qapp):
    def run():
        qapp.exec_()

    app = MountWizzard4(mwGlob=mwglob, application=qapp)
    qtbot.add_widget(app.mainW)

    worker = Worker(run)
    tp.start(worker)
    qtbot.wait_for_window_shown(app.mainW)

    qtbot.mouseClick(app.mainW.ui.openMessageW, Qt.LeftButton)
    qtbot.wait_for_window_shown(app.uiWindows['showMessageW']['classObj'])

    qtbot.mouseClick(app.mainW.ui.openImageW, Qt.LeftButton)
    qtbot.wait_for_window_shown(app.uiWindows['showImageW']['classObj'])

    qtbot.mouseClick(app.mainW.ui.openHemisphereW, Qt.LeftButton)
    qtbot.wait_for_window_shown(app.uiWindows['showHemisphereW']['classObj'])

    qtbot.mouseClick(app.mainW.ui.openMeasureW, Qt.LeftButton)
    qtbot.wait_for_window_shown(app.uiWindows['showMeasureW']['classObj'])

    qtbot.mouseClick(app.mainW.ui.openSatelliteW, Qt.LeftButton)
    qtbot.wait_for_window_shown(app.uiWindows['showSatelliteW']['classObj'])

    QTest.qWait(1000)
    qtbot.mouseClick(app.mainW.ui.saveConfig, Qt.LeftButton)

    #qtbot.mouseClick(app.mainW.ui.openMessageW, Qt.LeftButton)
    #qtbot.mouseClick(app.mainW.ui.openImageW, Qt.LeftButton)
    #qtbot.mouseClick(app.mainW.ui.openHemisphereW, Qt.LeftButton)
    #qtbot.mouseClick(app.mainW.ui.openMeasureW, Qt.LeftButton)
    #qtbot.mouseClick(app.mainW.ui.openSatelliteW, Qt.LeftButton)

    qtbot.mouseClick(app.mainW.ui.saveConfig, Qt.LeftButton)

    QTest.qWait(3000)

    qtbot.mouseClick(app.mainW.ui.saveConfigQuit, Qt.LeftButton)

