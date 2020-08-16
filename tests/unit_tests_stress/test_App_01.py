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
# written in python 3, (c) 2019, 2020 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import os

# external packages
import pytest
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QThreadPool
from PyQt5.QtTest import QTest
# local import
from mainApp import MountWizzard4
from base.tpool import Worker
from resource import resources


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
    if os.path.isfile('mw4/test/config/config.cfg'):
        os.remove('mw4/test/config/config.cfg')
    if os.path.isfile('mw4/test/config/profile'):
        os.remove('mw4/test/config/profile')

    yield

    tp.waitForDone(3000)


def test_1(qtbot, qapp):
    # open all windows and close them
    def run():
        qapp.exec_()

    app = MountWizzard4(mwGlob=mwglob, application=qapp)

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