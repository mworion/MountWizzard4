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
import unittest.mock as mock
import shutil
import time
import os
import glob
import pytest

# external packages
import PyQt5

# local import
from mainApp import MountWizzard4
from base.loggerMW import setupLogging

setupLogging()


@pytest.fixture(autouse=True, scope='function')
def app(qapp):

    files = glob.glob('tests/workDir/data/*.bsp')
    for f in files:
        os.remove(f)
        yield


def test_start_parameters_1(qapp):
    mwGlob = {'configDir': 'tests/workDir/config',
              'dataDir': 'tests/workDir/data',
              'tempDir': 'tests/workDir/temp',
              'imageDir': 'tests/workDir/image',
              'modelDir': 'tests/workDir/model',
              'workDir': 'tests/workDir',
              }
    with open(mwGlob['workDir'] + '/test.txt', 'w+') as test:
        test.write('test')

    shutil.copy(r'tests/testData/de421_23.bsp', r'tests/workDir/data/de421_23.bsp')

    with mock.patch.object(PyQt5.QtWidgets.QWidget,
                           'show'):
        with mock.patch.object(PyQt5.QtCore.QTimer,
                               'start'):
            with mock.patch.object(PyQt5.QtCore.QBasicTimer,
                                   'start'):
                with mock.patch.object(MountWizzard4,
                                       'checkAndSetAutomation',
                                       return_value=None):
                    MountWizzard4(mwGlob=mwGlob, application=qapp)
                    time.sleep(5)


def test_start_parameters_2(qapp):
    mwGlob = {'configDir': 'tests/workDir/config',
              'dataDir': 'tests/workDir/data',
              'tempDir': 'tests/workDir/temp',
              'imageDir': 'tests/workDir/image',
              'modelDir': 'tests/workDir/model',
              'workDir': 'tests/workDir',
              }
    with open(mwGlob['workDir'] + '/test.txt', 'w+') as test:
        test.write('test')

    shutil.copy(r'tests/testData/de421_23.bsp', r'tests/workDir/data/de421_23.bsp')

    with mock.patch.object(PyQt5.QtWidgets.QWidget,
                           'show'):
        with mock.patch.object(PyQt5.QtCore.QTimer,
                               'start'):
            with mock.patch.object(PyQt5.QtCore.QBasicTimer,
                                   'start'):
                with mock.patch.object(MountWizzard4,
                                       'checkAndSetAutomation',
                                       return_value=None):
                    MountWizzard4(mwGlob=mwGlob, application=qapp)
                    time.sleep(5)
