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
# written in python3 , (c) 2019, 2020 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
from unittest import mock
import pytest
import os
import json
import platform
import shutil
from unittest import mock

# external packages
from PyQt5.QtCore import QThreadPool, QObject

# local import
if not platform.system() == 'Windows':
    pytest.skip("skipping windows-only tests", allow_module_level=True)

from logic.automation.automateWindows import AutomateWindows
import winreg
from pywinauto import timings
import pywinauto

# todo: https://github.com/pywinauto/pywinauto/issues/858


@pytest.fixture(autouse=True, scope='module')
def module(qapp):
    yield


@pytest.fixture(autouse=True, scope='function')
def function(module):
    class Test(QObject):
        threadPool = QThreadPool()
        mwGlob = {'tempDir': 'tests/temp',
                  'dataDir': 'tests/data',
                  }

    for file in os.listdir('tests/data'):
        os.remove('tests/data/' + file)

    window = AutomateWindows(app=Test())

    yield window


def test_getRegistrationKeyPath_1(function):
    with mock.patch.object(platform,
                           'machine',
                           return_value='64'):
        val = function.getRegistryPath()
        assert val == 'SOFTWARE\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall'


def test_getRegistrationKeyPath_2(function):
    with mock.patch.object(platform,
                           'machine',
                           return_value='32'):
        val = function.getRegistryPath()
        assert val == 'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall'


def test_convertRegistryEntryToDict(function):
    with mock.patch.object(winreg,
                           'QueryInfoKey',
                           return_value=[0, 1]):
        with mock.patch.object(winreg,
                               'EnumValue',
                               return_value=['test', 'test']):
            val = function.convertRegistryEntryToDict('test')
            assert val


def test_searchNameInRegistry_1(function):
    with mock.patch.object(winreg,
                           'QueryInfoKey',
                           return_value=[1]):
        with mock.patch.object(winreg,
                               'EnumKey',
                               return_value=['test']):
            val = function.searchNameInRegistry('test', 'test')
            assert val


def test_searchNameInRegistry_2(function):
    with mock.patch.object(winreg,
                           'QueryInfoKey',
                           return_value=[1]):
        with mock.patch.object(winreg,
                               'EnumKey',
                               return_value=['test']):
            val = function.searchNameInRegistry('none', 'none')
            assert not val


def test_getNameKeyFromRegistry_1(function):
    with mock.patch.object(function,
                           'getRegistryPath',
                           return_value='test'):
        with mock.patch.object(winreg,
                               'OpenKey',
                               return_value='test'):
            with mock.patch.object(function,
                                   'searchNameInRegistry',
                                   return_value='test'):
                with mock.patch.object(winreg,
                                       'CloseKey',
                                       return_value='test'):
                    val = function.getNameKeyFromRegistry('test')
                    assert val == 'test'


def test_extractPropertiesFromRegistry_1(function):
    with mock.patch.object(function,
                           'getNameKeyFromRegistry',
                           return_value=''):
        avail, path, name = function.extractPropertiesFromRegistry('')
        assert not avail
        assert path == ''
        assert name == ''


def test_extractPropertiesFromRegistry_2(function):
    with mock.patch.object(function,
                           'getNameKeyFromRegistry',
                           return_value='test'):
        with mock.patch.object(function,
                               'getValuesForNameKeyFromRegistry',
                               return_value={}):
            avail, path, name = function.extractPropertiesFromRegistry('test')
            assert not avail
            assert path == ''
            assert name == ''


def test_extractPropertiesFromRegistry_3(function):
    with mock.patch.object(function,
                           'getNameKeyFromRegistry',
                           return_value='test'):
        with mock.patch.object(function,
                               'getValuesForNameKeyFromRegistry',
                               return_value={'DisplayName': 'test',
                                             'InstallLocation': 'test'}):
            avail, path, name = function.extractPropertiesFromRegistry('test')
            assert avail
            assert path == 'test'
            assert name == 'test'


def test_getAppSettings_1(function):
    with mock.patch.object(function,
                           'extractPropertiesFromRegistry',
                           return_value='test'):
        avail, path, name = function.getAppSettings('test')
        assert not avail
        assert path == ''
        assert name == ''


def test_getAppSettings_2(function):
    with mock.patch.object(function,
                           'extractPropertiesFromRegistry',
                           return_value='test',
                           side_effect=Exception()):
        avail, path, name = function.getAppSettings('test')
        assert not avail
        assert path == ''
        assert name == ''


def test_getAppSettings_3(function):
    with mock.patch.object(function,
                           'extractPropertiesFromRegistry',
                           return_value=(True, 'test', 'test')):
        avail, path, name = function.getAppSettings('test')
        assert avail
        assert path == 'test'
        assert name == 'test'


def test_checkFloatingPointErrorWindow_1(function):
    class Test1:
        @staticmethod
        def click():
            pass

    class Test:
        @staticmethod
        def window(handle=None):
            return {'OK': Test1()}

    function.updater = Test()
    with mock.patch.object(timings,
                           'wait_until_passes'):
        suc = function.checkFloatingPointErrorWindow()
        assert suc


def test_checkFloatingPointErrorWindow_2(function):
    class Test1:
        @staticmethod
        def click():
            pass

    class Test:
        @staticmethod
        def window(handle=None):
            return {'OK': Test1()}

    function.updater = Test()
    with mock.patch.object(timings,
                           'wait_until_passes',
                           side_effect=Exception()):
        suc = function.checkFloatingPointErrorWindow()
        assert not suc


def test_checkFloatingPointErrorWindow_3(function):
    class Test1:
        @staticmethod
        def click():
            pass

    class Test:
        @staticmethod
        def window(handle=None):
            return {'OK': Test1()}

    function.updater = Test()
    with mock.patch.object(timings,
                           'wait_until_passes',
                           side_effect=timings.TimeoutError):
        suc = function.checkFloatingPointErrorWindow()
        assert suc


def test_startUpdater_1(function):
    class Test:
        @staticmethod
        def start(a):
            pass

    with mock.patch.object(pywinauto,
                           'Application',
                           return_value=Test()):
        with mock.patch.object(Test,
                               'start',
                               side_effect=pywinauto.application.AppStartError()):
            suc = function.startUpdater()
            assert not suc


def test_startUpdater_2(function):
    class Test:
        @staticmethod
        def start(a):
            pass

    with mock.patch.object(pywinauto,
                           'Application',
                           return_value=Test()):
        with mock.patch.object(Test,
                               'start',
                               side_effect=Exception()):
            suc = function.startUpdater()
            assert not suc


def test_startUpdater_3(function):
    class Test:
        @staticmethod
        def start(a):
            pass

    with mock.patch.object(pywinauto,
                           'Application',
                           return_value=Test()):
        with mock.patch.object(function,
                               'checkFloatingPointErrorWindow'):
            suc = function.startUpdater()
            assert suc


def test_uploadEarthRotationData_1(function):
    function.actualWorkDir = os.getcwd()
    with mock.patch.object(function,
                           'prepareUpdater'):
        with mock.patch.object(function,
                               'uploadEarthRotationDataCommands',
                               side_effect=Exception()):
            suc = function.uploadEarthRotationData()
            assert not suc


def test_uploadEarthRotationData_2(function):
    function.actualWorkDir = os.getcwd()
    with mock.patch.object(function,
                           'prepareUpdater'):
        with mock.patch.object(function,
                               'uploadEarthRotationDataCommands'):
            with mock.patch.object(function,
                                   'doUploadAndCloseInstaller',
                                   return_value=False):
                suc = function.uploadEarthRotationData()
                assert not suc


def test_uploadEarthRotationData_3(function):
    function.actualWorkDir = os.getcwd()
    with mock.patch.object(function,
                           'prepareUpdater'):
        with mock.patch.object(function,
                               'uploadEarthRotationDataCommands'):
            with mock.patch.object(function,
                                   'doUploadAndCloseInstaller',
                                   return_value=True):
                suc = function.uploadEarthRotationData()
                assert suc


def test_writeEarthRotationData_1(function):
    suc = function.writeEarthRotationData()
    assert not suc


def test_writeEarthRotationData_2(function):
    shutil.copy('tests/testData/tai-utc.dat', 'tests/data/tai-utc.dat')
    suc = function.writeEarthRotationData()
    assert not suc


def test_writeEarthRotationData_3(function):
    shutil.copy('tests/testData/tai-utc.dat', 'tests/data/tai-utc.dat')
    shutil.copy('tests/testData/finals.data', 'tests/data/finals.data')
    suc = function.writeEarthRotationData()
    assert suc


def test_writeCometMPC_1(function):
    function.installPath = 'tests/temp'

    suc = function.writeCometMPC()
    assert not suc


def test_writeCometMPC_2(function):
    function.installPath = 'tests/temp'

    data = {'test': 'test'}

    suc = function.writeCometMPC(datas=data)
    assert not suc


def test_writeCometMPC_3(function):
    function.installPath = 'tests/temp'

    data = [{'test': 'test'}]

    suc = function.writeCometMPC(datas=data)
    assert suc
    assert os.path.isfile('tests/temp/minorPlanets.mpc')


def test_writeCometMPC_4(function):
    function.installPath = 'tests/temp'

    with open('tests/testData/mpc_comet_test.json') as f:
        data = json.load(f)

    testData = [data[0]]

    suc = function.writeCometMPC(datas=testData)
    assert suc


def test_writeCometMPC_5(function):
    function.installPath = 'tests/temp'

    with open('tests/testData/mpc_comet_test.json') as f:
        data = json.load(f)

    testData = [data[0]]

    suc = function.writeCometMPC(datas=testData)
    assert suc

    with open('tests/temp/minorPlanets.mpc', 'r') as f:
        testLine = f.readline()

    with open('tests/testData/mpc_comet_test.txt', 'r') as f:
        refLine = f.readline()

    assert testLine == refLine

"""
def test_writeCometMPC_6(function):
    function.installPath = 'tests/temp'

    with open('tests/testData/mpc_comet_test.json') as f:
        data = json.load(f)

    suc = function.writeCometMPC(datas=data)
    assert suc

    with open('tests/temp/minorPlanets.mpc', 'r') as f:
        testLines = f.readlines()

    with open('tests/testData/mpc_comet_test.txt', 'r') as f:
        refLines = f.readlines()

    for test, ref in zip(testLines, refLines):
        assert test == ref
"""


def test_writeAsteroidMPC_1(function):
    function.installPath = 'tests/temp'

    suc = function.writeAsteroidMPC()
    assert not suc


def test_writeAsteroidMPC_2(function):
    function.installPath = 'tests/temp'

    data = {'test': 'test'}

    suc = function.writeAsteroidMPC(datas=data)
    assert not suc


def test_writeAsteroidMPC_3(function):
    function.installPath = 'tests/temp'

    data = [{'test': 'test'}]

    suc = function.writeAsteroidMPC(datas=data)
    assert suc
    assert os.path.isfile('tests/temp/minorPlanets.mpc')


def test_writeAsteroidMPC_4(function):
    function.installPath = 'tests/temp'

    with open('tests/testData/mpc_asteroid_test.json') as f:
        data = json.load(f)

    testData = [data[0]]

    suc = function.writeAsteroidMPC(datas=testData)
    assert suc

"""
def test_writeAsteroidMPC_5(function):
    function.installPath = 'tests/temp'

    with open('tests/testData/mpc_Asteroid_test.json') as f:
        data = json.load(f)

    testData = [data[0]]

    suc = function.writeAsteroidMPC(datas=testData)
    assert suc

    with open('tests/temp/minorPlanets.mpc', 'r') as f:
        testLine = f.readline()

    with open('tests/testData/mpc_asteroid_test.txt', 'r') as f:
        refLine = f.readline()

    assert testLine == refLine


def test_writeAsteroidMPC_6(function):
    function.installPath = 'tests/temp'

    with open('tests/testData/mpc_asteroid_test.json') as f:
        data = json.load(f)

    suc = function.writeAsteroidMPC(datas=data)
    assert suc

    with open('tests/temp/minorPlanets.mpc', 'r') as f:
        testLines = f.readlines()

    with open('tests/testData/mpc_asteroid_test.txt', 'r') as f:
        refLines = f.readlines()

    for test, ref in zip(testLines, refLines):
        assert test == ref
"""
