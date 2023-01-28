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
from random import randint

# external packages
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QThreadPool
import numpy as np

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
    count = 59
    app.measure.data = {
        'time': np.empty(shape=[0, 1], dtype='datetime64'),
        'sensorWeatherTemp': np.array([1] * count),
        'onlineWeatherTemp': np.array([1] * count),
        'directWeatherTemp': np.array([1] * count),
        'skyTemp': np.array([1] * count),
        'powTemp': np.array([1] * count),
    }
    for i in range(count):
        value = np.datetime64(f'2014-12-12 20:20:{count:02d}')
        app.measure.data['time'] = np.append(app.measure.data['time'], value)

    worker = Worker(run)
    tp.start(worker)
    qtbot.waitExposed(app.mainW, timeout=1000)
    sleepAndEvents(100)

    for index in range(5):
        qtbot.mouseClick(app.mainW.ui.openMeasureW, Qt.LeftButton)
        c = app.uiWindows['showMeasureW']['classObj']
        qtbot.waitExposed(c, timeout=3000)
        c.ui.set0.setCurrentIndex(3)
        sleepAndEvents(50)
        c.drawMeasure()
        sleepAndEvents(randint(500, 1500))
        c.close()
        sleepAndEvents(50)
    qtbot.mouseClick(app.mainW.ui.saveConfigQuit, Qt.LeftButton)
