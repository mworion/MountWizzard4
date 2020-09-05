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
import glob
from tr import tr

# external packages
import pytest
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtCore import QThreadPool
from PyQt5.QtTest import QTest

# local import
from mainApp import MountWizzard4
from base.tpool import Worker
from loader import extractDataFiles
from resource import resources


mwglob = {'dataDir': 'tests/data',
          'configDir': 'tests/config',
          'workDir': 'mw4/test',
          'imageDir': 'tests/image',
          'tempDir': 'tests/temp',
          'measureDir': 'tests/measure',
          'modelDir': 'tests/model',
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


def test_configAlpaca(qtbot, qapp):
    # open all windows and close them
    def run():
        qapp.exec_()

    app = MountWizzard4(mwGlob=mwglob, application=qapp)

    worker = Worker(run)
    tp.start(worker)
    qtbot.waitExposed(app.mainW, 1000)

    qtbot.mouseClick(app.mainW.ui.cameraSetup, Qt.LeftButton)
    popup = app.mainW.popupUi
    qtbot.waitExposed(popup, 1000)

    popup.ui.tab.setCurrentIndex(1)
    popup.ui.alpacaHostAddress.setText('192.168.2.211')
    popup.ui.alpacaPort.setText('11111')
    qtbot.mouseClick(popup.ui.alpacaDiscover, Qt.LeftButton)

    QTest.qWait(1000)
    qtbot.mouseClick(popup.ui.ok, Qt.LeftButton)

    QTest.qWait(1000)
    qtbot.mouseClick(app.mainW.ui.saveConfigQuit, Qt.LeftButton)
