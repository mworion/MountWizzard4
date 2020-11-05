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
from skyfield.api import load

# local import
if not platform.system() == 'Windows':
    pytest.skip("skipping windows-only tests", allow_module_level=True)

from logic.automation.automateWindows import AutomateWindows
import winreg
from pywinauto import timings
import pywinauto
import pywinauto.controls.win32_controls as controls
# todo: https://github.com/pywinauto/pywinauto/issues/858


@pytest.fixture(autouse=True, scope='module')
def module(qapp):
    yield


@pytest.fixture(autouse=True, scope='function')
def function(module):

    class MountObsSite:
        ts = load.timescale(builtin=True)

    class Mount:
        obsSite = MountObsSite()

    class Test(QObject):
        threadPool = QThreadPool()
        mount = Mount()
        mwGlob = {'tempDir': 'tests/temp',
                  'dataDir': 'tests/data',
                  }

    for file in ['tai-utc.dat', 'finals2000A.all']:
        path = 'tests/data/' + file
        if os.path.isfile(path):
            os.remove(path)

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


def test_uploadEarthRotationDataCommands(function):
    class Test:
        @staticmethod
        def click():
            pass

        @staticmethod
        def check_by_click():
            pass

        @staticmethod
        def set_text(a):
            pass

    win = {'UTC / Earth rotation data': Test(),
           'Edit...1': Test(),
           }
    popup = {'Import files...': Test()
             }
    dialog = {'Button16': Test(),
              'Edit13': Test(),
              }
    ok = {'OK': Test()
          }
    function.updater = {'10 micron control box update': win,
                        'UTC / Earth rotation data': popup,
                        'Open finals data': dialog,
                        'Open tai-utc.dat': dialog,
                        'UTC data': ok
                        }
    with mock.patch.object(controls,
                           'ButtonWrapper'):
        with mock.patch.object(controls,
                               'EditWrapper'):
            suc = function.uploadEarthRotationDataCommands()
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


def test_clearUploadMenuCommands(function):
    class Test:
        @staticmethod
        def click():
            pass

        @staticmethod
        def uncheck_by_click():
            pass

    win = {'next': Test(),
           'Control box firmware': Test(),
           'Orbital parameters of comets': Test(),
           'Orbital parameters of asteroids': Test(),
           'Orbital parameters of satellites': Test(),
           'UTC / Earth rotation data': Test()
           }
    function.updater = {'10 micron control box update': win}
    with mock.patch.object(controls,
                           'ButtonWrapper'):
        suc = function.clearUploadMenuCommands()
        assert suc


def test_clearUploadMenu_1(function):
    with mock.patch.object(function,
                           'clearUploadMenuCommands'):
        suc = function.clearUploadMenu()
        assert suc


def test_clearUploadMenu_2(function):
    with mock.patch.object(function,
                           'clearUploadMenuCommands',
                           side_effect=Exception()):
        suc = function.clearUploadMenu()
        assert not suc


def test_prepareUpdater_1(function):
    with mock.patch.object(os,
                           'chdir'):
        with mock.patch.object(function,
                               'startUpdater',
                               return_value=False):
            suc = function.prepareUpdater()
            assert not suc


def test_prepareUpdater_2(function):
    with mock.patch.object(os,
                           'chdir'):
        with mock.patch.object(function,
                               'startUpdater',
                               return_value=True):
            with mock.patch.object(function,
                                   'clearUploadMenu',
                                   return_value=False):
                suc = function.prepareUpdater()
                assert not suc


def test_prepareUpdater_3(function):
    with mock.patch.object(os,
                           'chdir'):
        with mock.patch.object(function,
                               'startUpdater',
                               return_value=True):
            with mock.patch.object(function,
                                   'clearUploadMenu',
                                   return_value=True):
                suc = function.prepareUpdater()
                assert suc


def test_doUploadAndCloseInstallerCommands(function):
    class Test:
        @staticmethod
        def click():
            pass

    win = {'next': Test(),
           'Update Now': Test(),
           'OK': Test()
           }
    function.updater = {'10 micron control box update': win}
    with mock.patch.object(timings,
                           'wait_until_passes'):
        suc = function.doUploadAndCloseInstallerCommands()
        assert suc


def test_pressOK(function):
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
        suc = function.pressOK()
        assert suc


def test_doUploadAndCloseInstaller_1(function):
    with mock.patch.object(function,
                           'doUploadAndCloseInstallerCommands'):
        with mock.patch.object(function,
                               'pressOK'):
            suc = function.doUploadAndCloseInstaller()
            assert suc


def test_doUploadAndCloseInstaller_2(function):
    with mock.patch.object(function,
                           'doUploadAndCloseInstallerCommands'):
        with mock.patch.object(function,
                               'pressOK',
                               side_effect=Exception()):
            suc = function.doUploadAndCloseInstaller()
            assert not suc


def test_uploadMPCDataCommands_1(function):
    class Test:
        @staticmethod
        def click():
            pass

        @staticmethod
        def check_by_click():
            pass

        @staticmethod
        def set_text(a):
            pass

    win = {'Orbital parameters of comets': Test(),
           'Orbital parameters of asteroids': Test(),
           'Edit...4': Test(),
           'Edit...3': Test(),
           }
    popup = {'MPC file': Test(),
             'Close': Test(),
             }
    dialog = {'Button16': Test(),
              'Edit13': Test(),
              }
    function.updater = {'10 micron control box update': win,
                        'Asteroid orbits': popup,
                        'Comet orbits': popup,
                        'Dialog': dialog,
                        }
    with mock.patch.object(controls,
                           'ButtonWrapper'):
        with mock.patch.object(controls,
                               'EditWrapper'):
            suc = function.uploadMPCDataCommands()
            assert suc


def test_uploadMPCDataCommands_2(function):
    class Test:
        @staticmethod
        def click():
            pass

        @staticmethod
        def check_by_click():
            pass

        @staticmethod
        def set_text(a):
            pass

    win = {'Orbital parameters of comets': Test(),
           'Orbital parameters of asteroids': Test(),
           'Edit...4': Test(),
           'Edit...3': Test(),
           }
    popup = {'MPC file': Test(),
             'Close': Test(),
             }
    dialog = {'Button16': Test(),
              'Edit13': Test(),
              }
    function.updater = {'10 micron control box update': win,
                        'Asteroid orbits': popup,
                        'Comet orbits': popup,
                        'Dialog': dialog,
                        }
    with mock.patch.object(controls,
                           'ButtonWrapper'):
        with mock.patch.object(controls,
                               'EditWrapper'):
            suc = function.uploadMPCDataCommands(comets=True)
            assert suc


def test_uploadMPCData_1(function):
    function.actualWorkDir = os.getcwd()
    with mock.patch.object(function,
                           'prepareUpdater'):
        with mock.patch.object(function,
                               'uploadMPCDataCommands'):
            with mock.patch.object(function,
                                   'doUploadAndCloseInstaller',
                                   return_value=False):
                suc = function.uploadMPCData()
                assert not suc


def test_uploadMPCData_2(function):
    function.actualWorkDir = os.getcwd()
    with mock.patch.object(function,
                           'prepareUpdater'):
        with mock.patch.object(function,
                               'uploadMPCDataCommands'):
            with mock.patch.object(function,
                                   'doUploadAndCloseInstaller',
                                   return_value=True):
                suc = function.uploadMPCData()
                assert suc


def test_uploadMPCData_3(function):
    function.actualWorkDir = os.getcwd()
    with mock.patch.object(function,
                           'prepareUpdater'):
        with mock.patch.object(function,
                               'uploadMPCDataCommands',
                               side_effect=Exception()):
            suc = function.uploadMPCData()
            assert not suc


def test_writeEarthRotationData_1(function):
    suc = function.writeEarthRotationData()
    assert not suc


def test_writeEarthRotationData_2(function):
    shutil.copy('tests/testData/tai-utc.dat', 'tests/data/tai-utc.dat')
    suc = function.writeEarthRotationData()
    assert not suc


def test_writeEarthRotationData_3(function):
    shutil.copy('tests/testData/tai-utc.dat', 'tests/data/tai-utc.dat')
    shutil.copy('tests/testData/finals2000A.all', 'tests/data/finals2000A.all')
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


def test_generateCycleCountPackedText(function):
    cycles = [
        0,
        1,
        13,
        108,
        127,
        162,
        193,
        360,
        418,
    ]
    texts = [
        '00',
        '01',
        '13',
        'A8',
        'C7',
        'G2',
        'J3',
        'a0',
        'f8'
    ]
    for cycle, text in zip(cycles, texts):
        val = function.generateCycleCountTextPacked(cycle)
        assert val == text


def test_generatePackedDesignation_1(function):
    designations = [
        '1995 XA',
        '1995 XL1',
        '1995 FB13',
        '1998 SQ108',
        '1998 SV127',
        '1998 SS162',
        '2099 AZ193',
        '2008 AA360',
        '2007 TA418'
    ]
    results = [
        'J95X00A',
        'J95X01L',
        'J95F13B',
        'J98SA8Q',
        'J98SC7V',
        'J98SG2S',
        'K99AJ3Z',
        'K08Aa0A',
        'K07Tf8A'
    ]

    for desig, res in zip(designations, results):
        val = function.generateDesignationPacked(desig)
        assert val == res


def test_convertDatePacked(function):
    values = ['01', '10', '30', '01', '22', '99']
    results = ['1', 'A', 'U', '1', 'M', ' ']

    for value, result in zip(values, results):
        val = function.convertDatePacked(value)
        assert val == result


def test_generateDatePacked(function):

    months = ['01', '01', '09', '10', '10']
    days = ['01', '10', '30', '01', '22']
    results = ['11', '1A', '9U', 'A1', 'AM']

    for mon, day, result in zip(months, days, results):
        val = function.generateDatePacked(mon, day)
        assert val == result


def test_generateEpochPacked(function):
    epoch = 2458600.5
    epochPackedText = 'K194R'
    val = function.generateEpochPacked(epoch)
    assert val == epochPackedText


def test_generateOldDesignationPacked_1(function):
    numberTexts = ['(1)', '(100)', '(5986)', '(12345)', '(123456)']
    results = ['00001  ', '00100  ', '05986  ', '12345  ', 'C3456  ']

    for numberText, result in zip(numberTexts, results):
        val = function.generateOldDesignationPacked(numberText)
        assert val == result


def test_generateOldDesignationPacked_2(function):
    val = function.generateOldDesignationPacked('')
    assert val == 'xxxxxxx'


def test_writeAsteroidMPC_1(function):
    function.installPath = 'tests/temp'

    suc = function.writeAsteroidMPC()
    assert not suc


def test_writeAsteroidMPC_2(function):
    function.installPath = 'tests/temp'

    data = {'Principal_desig': '2016 NU22'}

    suc = function.writeAsteroidMPC(datas=data)
    assert not suc


def test_writeAsteroidMPC_3(function):
    function.installPath = 'tests/temp'

    data = [{}]

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


def test_writeAsteroidMPC_5(function):
    function.installPath = 'tests/temp'

    with open('tests/testData/mpc_asteroid_test.json') as f:
        data = json.load(f)

    testData = [data[0]]

    suc = function.writeAsteroidMPC(datas=testData)
    assert suc

    with open('tests/temp/minorPlanets.mpc', 'r') as f:
        testLine = f.readline()

    with open('tests/testData/mpc_asteroid_test.txt', 'r') as f:
        refLine = f.readline()

    assert testLine[:202] == refLine[:202]


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
        assert test[0:8] == ref[0:8]
        assert test[14:202] == ref[14:202]


def test_writeAsteroidMPC_7(function):
    function.installPath = 'tests/temp'

    with open('tests/testData/nea_extended_test.json') as f:
        data = json.load(f)

    testData = [data[0]]

    suc = function.writeAsteroidMPC(datas=testData)
    assert suc

    with open('tests/temp/minorPlanets.mpc', 'r') as f:
        testLine = f.readline()

    with open('tests/testData/nea_extended_test.txt', 'r') as f:
        refLine = f.readline()

    assert testLine[:202] == refLine[:202]


def test_writeAsteroidMPC_8(function):
    function.installPath = 'tests/temp'

    with open('tests/testData/nea_extended_test.json') as f:
        data = json.load(f)

    suc = function.writeAsteroidMPC(datas=data)
    assert suc

    with open('tests/temp/minorPlanets.mpc', 'r') as f:
        testLines = f.readlines()

    with open('tests/testData/nea_extended_test.txt', 'r') as f:
        refLines = f.readlines()

    for test, ref in zip(testLines, refLines):
        if ref[0:3] in ['PLS']:
            continue

        assert test[0:7] == ref[0:7]
        assert test[21:140] == ref[21:140]
        assert test[142:167] == ref[142:167]

