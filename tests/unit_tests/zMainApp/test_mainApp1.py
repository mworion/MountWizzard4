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
# written in python3, (c) 2019-2021 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import os
import glob
import json
import unittest.mock as mock
import logging
import platform
import shutil
import time

# external packages
import pytest
import PyQt5

# local import
from mainApp import MountWizzard4
from base.loggerMW import setupLogging

setupLogging()


@pytest.fixture(autouse=True, scope='module')
def app(qapp):
    global mwGlob
    mwGlob = {'configDir': 'tests/workDir/config',
              'dataDir': 'tests/workDir/data',
              'tempDir': 'tests/workDir/temp',
              'imageDir': 'tests/workDir/image',
              'modelDir': 'tests/workDir/model',
              'workDir': 'mw4/tests/workdir',
              }

    files = glob.glob('tests/workDir/config/*.cfg')
    for f in files:
        os.remove(f)

    shutil.copy(r'tests/testData/de421_23.bsp', r'tests/workDir/data/de421_23.bsp')

    with mock.patch.object(PyQt5.QtWidgets.QWidget,
                           'show'):
        with mock.patch.object(PyQt5.QtCore.QTimer,
                               'start'):
            with mock.patch.object(PyQt5.QtCore.QBasicTimer,
                                   'start'):
                with mock.patch.object(os.path,
                                       'isfile',
                                       return_value=True):
                    app = MountWizzard4(mwGlob=mwGlob, application=qapp)
                    app.log = logging.getLogger()
                    with mock.patch.object(app.mainW,
                                           'setupSatelliteNameList'):
                        yield app
                        app.threadPool.waitForDone(5000)


def test():
    pass
