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
# GUI with PySide for python
#
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import shutil
import time
import os
import glob
import pytest
import astropy

# external packages
import PySide6

# local import
from mainApp import MountWizzard4
from base.loggerMW import setupLogging

setupLogging()


@pytest.fixture(autouse=True, scope='function')
def app(qapp):
    if not os.path.isfile('tests/workDir/data/de440_mw4.bsp'):
        shutil.copy(r'tests/testData/de440_mw4.bsp',
                    r'tests/workDir/data/de440_mw4.bsp')


def test_start_parameters_1(qapp):
    mwGlob = {'configDir': 'tests/workDir/config',
              'dataDir': 'tests/workDir/data',
              'tempDir': 'tests/workDir/temp',
              'imageDir': 'tests/workDir/image',
              'modelDir': 'tests/workDir/model',
              'workDir': 'tests/workDir',
              }
    with open(mwGlob['workDir'] + '/test.run', 'w+') as test:
        test.write('test')

    with mock.patch.object(PySide6.QtWidgets.QWidget,
                           'show'):
        with mock.patch.object(PySide6.QtCore.QTimer,
                               'start'):
            with mock.patch.object(PySide6.QtCore.QBasicTimer,
                                   'start'):
                with mock.patch.object(MountWizzard4,
                                       'checkAndSetAutomation',
                                       return_value=None):
                    MountWizzard4(mwGlob=mwGlob, application=qapp)
                    time.sleep(10)


def test_start_parameters_2(qapp):
    mwGlob = {'configDir': 'tests/workDir/config',
              'dataDir': 'tests/workDir/data',
              'tempDir': 'tests/workDir/temp',
              'imageDir': 'tests/workDir/image',
              'modelDir': 'tests/workDir/model',
              'workDir': 'tests/workDir',
              }
    with open(mwGlob['workDir'] + '/test.run', 'w+') as test:
        test.write('test')

    with mock.patch.object(PySide6.QtWidgets.QWidget,
                           'show'):
        with mock.patch.object(PySide6.QtCore.QTimer,
                               'start'):
            with mock.patch.object(PySide6.QtCore.QBasicTimer,
                                   'start'):
                with mock.patch.object(MountWizzard4,
                                       'checkAndSetAutomation',
                                       return_value=None):
                    MountWizzard4(mwGlob=mwGlob, application=qapp)
                    time.sleep(10)