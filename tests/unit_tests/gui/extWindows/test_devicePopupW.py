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
import unittest.mock as mock
import pytest
import platform
import logging

# external packages
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QWidget
if platform.system() == 'Windows':
    import win32com.client


# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.utilities.toolsQtWidget import MWidget
from gui.extWindows.devicePopupW import DevicePopup
from base.indiClass import IndiClass
from base.alpacaClass import AlpacaClass
from base.sgproClass import SGProClass
from base.ninaClass import NINAClass
from base.loggerMW import addLoggingLevel


@pytest.fixture(autouse=True, scope='function')
def function(qapp):

    data = {
        'framework': 'indi',
        'frameworks': {
            'indi': {
                'deviceName': 'test',
                'deviceList': ['1', '2']}
            },
    }
    widget = QWidget()
    with mock.patch.object(DevicePopup,
                           'show'):
        window = DevicePopup(widget,
                             app=App(),
                             data=data,
                             driver='telescope',
                             deviceType='telescope')
        window.log = logging.getLogger()
        addLoggingLevel('TRACE', 5)
        yield window


def test_initConfig_1(function):
    suc = function.initConfig()
    assert suc


def test_initConfig_2(function):
    function.data['framework'] = 'astap'
    with mock.patch.object(function,
                           'populateTabs'):
        with mock.patch.object(function,
                               'selectTabs'):
            with mock.patch.object(function,
                                   'updatePlateSolverStatus'):
                suc = function.initConfig()
                assert suc


def test_initConfig_3(function):
    function.data = {
        'framework': 'indi',
        'frameworks':
            {
                'indi': {
                    'deviceName': 'telescope',
                    'deviceList': ['telescope', 'test2'],

                }
            },
    }
    suc = function.initConfig()
    assert suc


def test_closeEvent_1(function):
    with mock.patch.object(function,
                           'show'):
        with mock.patch.object(MWidget,
                               'closeEvent'):
            function.closeEvent(QCloseEvent)


def test_selectTabs_1(function):
    function.data = {
        'framework': '',
        'frameworks': {
            'astap': {
                'test': 1,
            }
        }
    }
    suc = function.selectTabs()
    assert suc


def test_selectTabs_2(function):
    function.data = {
        'framework': 'astap',
        'frameworks': {
            'astap': {
                'test': 1,
            }
        }
    }
    suc = function.selectTabs()
    assert suc


def test_selectTabs_3(function):
    function.data = {
        'framework': 'test',
        'frameworks': {
            'test': {
                'test': 1,
            }
        }
    }
    suc = function.selectTabs()
    assert suc


def test_populateTabs_1(function):
    function.data = {
        'framework': 'astap',
        'frameworks': {
            'astap': {
                'deviceName': 'astap',
                'deviceList': ['test', 'test1'],
                'searchRadius': 30,
                'appPath': 'test',
            },
        }
    }
    suc = function.populateTabs()
    assert suc


def test_populateTabs_2(function):
    function.data = {
        'framework': 'indi',
        'frameworks': {
            'indi': {
                'deviceName': 'astap',
                'deviceList': ['test', 'test1'],
                'host': 'test',
                'messages': True,
            }
        }
    }
    suc = function.populateTabs()
    assert suc


def test_readTabs_1(function):
    function.data = {
        'framework': 'astap',
        'frameworks': {
            'astap': {
                'deviceName': 'astap',
                'deviceList': ['test', 'test1'],
                'searchRadius': 30,
                'appPath': 'test',
            },
        }
    }
    suc = function.readTabs()
    assert suc


def test_readTabs_2(function):
    function.framework2gui['astap']['appPath'].setText('100')
    function.data = {
        'framework': 'astap',
        'frameworks': {
            'astap': {
                'deviceName': 'astap',
                'deviceList': ['test', 'test1'],
                'searchRadius': 30,
                'appPath': 100,
            },
        }
    }
    suc = function.readTabs()
    assert suc


def test_readTabs_3(function):
    function.framework2gui['astap']['appPath'].setText('100')
    function.data = {
        'framework': 'astap',
        'frameworks': {
            'astap': {
                'deviceName': 'astap',
                'deviceList': ['test', 'test1'],
                'searchRadius': 30,
                'appPath': 100.0,
            },
        }
    }
    suc = function.readTabs()
    assert suc


def test_readTabs_4(function):
    function.data = {
        'framework': 'indi',
        'frameworks': {
            'indi': {
                'deviceName': 'astap',
                'deviceList': ['test', 'test1'],
                'host': 'test',
                'messages': True,
            }
        }
    }
    suc = function.readTabs()
    assert suc


def test_readFramework_1(function):
    suc = function.readFramework()
    assert suc


def test_storeConfig_1(function):
    with mock.patch.object(function,
                           'readFramework'):
        with mock.patch.object(function,
                               'readTabs'):
            with mock.patch.object(function,
                                   'close'):
                suc = function.storeConfig()
                assert suc


def test_updateIndiDeviceNameList_1(function):
    suc = function.updateIndiDeviceNameList(['test1', 'test2'])
    assert suc


def test_discoverIndiDevices_1(function):
    with mock.patch.object(IndiClass,
                           'discoverDevices',
                           return_value=()):
        suc = function.discoverIndiDevices()
        assert not suc


def test_discoverIndiDevices_2(function):
    with mock.patch.object(IndiClass,
                           'discoverDevices',
                           return_value=('Test1', 'Test2')):
        suc = function.discoverIndiDevices()
        assert suc


def test_updateAlpacaDeviceNameList_1(function):
    with mock.patch.object(function.ui.alpacaDeviceList,
                           'clear'):
        with mock.patch.object(function.ui.alpacaDeviceList,
                               'setView'):
            suc = function.updateAlpacaDeviceNameList(['test1', 'test2'])
            assert suc


def test_discoverAlpacaDevices_1(function):
    with mock.patch.object(AlpacaClass,
                           'discoverDevices',
                           return_value=()):
        suc = function.discoverAlpacaDevices()
        assert not suc


def test_discoverAlpacaDevices_2(function):
    with mock.patch.object(AlpacaClass,
                           'discoverDevices',
                           return_value=('Test1', 'Test2')):
        suc = function.discoverAlpacaDevices()
        assert suc


def test_updateSGProDeviceNameList_1(function):
    with mock.patch.object(function.ui.sgproDeviceList,
                           'clear'):
        with mock.patch.object(function.ui.sgproDeviceList,
                               'setView'):
            suc = function.updateSGProDeviceNameList(['test1', 'test2'])
            assert suc


def test_discoverSGProDevices_1(function):
    with mock.patch.object(SGProClass,
                           'discoverDevices',
                           return_value=[]):
        suc = function.discoverSGProDevices()
        assert suc


def test_discoverSGProDevices_2(function):
    with mock.patch.object(SGProClass,
                           'discoverDevices',
                           return_value=['Test1', 'Test2']):
        suc = function.discoverSGProDevices()
        assert suc


def test_updateNINADeviceNameList_1(function):
    with mock.patch.object(function.ui.ninaDeviceList,
                           'clear'):
        with mock.patch.object(function.ui.ninaDeviceList,
                               'setView'):
            suc = function.updateNINADeviceNameList(['test1', 'test2'])
            assert suc


def test_discoverNINADevices_1(function):
    with mock.patch.object(NINAClass,
                           'discoverDevices',
                           return_value=[]):
        suc = function.discoverNINADevices()
        assert suc


def test_discoverNINADevices_2(function):
    with mock.patch.object(NINAClass,
                           'discoverDevices',
                           return_value=['Test1', 'Test2']):
        suc = function.discoverNINADevices()
        assert suc


def test_checkPlateSolveAvailability_1(function):
    class Avail:
        @staticmethod
        def checkAvailability(appPath=0, indexPath=0):
            return True, True

    function.app.plateSolve.run['astap'] = Avail()
    suc = function.checkPlateSolveAvailability('astap', 'test', 'test')
    assert suc


def test_checkPlateSolveAvailability_2(function):
    class Avail:
        @staticmethod
        def checkAvailability(appPath=0, indexPath=0):
            return True, True

    function.app.plateSolve.run['watney'] = Avail()
    suc = function.checkPlateSolveAvailability('watney', 'test', 'test')
    assert suc


def test_checkPlateSolveAvailability_3(function):
    class Avail:
        @staticmethod
        def checkAvailability(appPath=0, indexPath=0):
            return True, True

    function.app.plateSolve.run['astrometry'] = Avail()
    suc = function.checkPlateSolveAvailability('astrometry', 'test', 'test')
    assert suc


def test_updatePlateSolverStatus(function):
    with mock.patch.object(function,
                           'checkPlateSolveAvailability'):
        suc = function.updatePlateSolverStatus()
        assert suc


def test_selectAstrometryIndexPath_1(function):
    with mock.patch.object(MWidget,
                           'openDir',
                           return_value=('', '', '')):
        suc = function.selectAstrometryIndexPath()
        assert not suc


def test_selectAstrometryIndexPath_2(function):
    class Test:
        @staticmethod
        def checkAvailability():
            return True, True

    function.app.plateSolve.run = {'astrometry': Test()}
    with mock.patch.object(MWidget,
                           'openDir',
                           return_value=('test', 'test', 'test')):
        with mock.patch.object(function,
                               'checkPlateSolveAvailability',
                               return_value=True):
            suc = function.selectAstrometryIndexPath()
            assert suc


def test_selectAstrometryAppPath_1(function):
    with mock.patch.object(MWidget,
                           'openDir',
                           return_value=('', '', '')):
        suc = function.selectAstrometryAppPath()
        assert not suc


def test_selectAstrometryAppPath_2(function):
    with mock.patch.object(MWidget,
                           'openDir',
                           return_value=('test', 'test', 'test')):
        with mock.patch.object(function,
                               'checkPlateSolveAvailability',
                               return_value=True):
            suc = function.selectAstrometryAppPath()
            assert suc


def test_selectAstrometryAppPath_3(function):
    with mock.patch.object(MWidget,
                           'openDir',
                           return_value=('test', 'test', '.app')):
        with mock.patch.object(platform,
                               'system',
                               return_value=('Darwin')):
            with mock.patch.object(function,
                                   'checkPlateSolveAvailability',
                                   return_value=True):
                suc = function.selectAstrometryAppPath()
                assert suc


def test_selectAstrometryAppPath_4(function):
    with mock.patch.object(MWidget,
                           'openDir',
                           return_value=('Astrometry.app', 'test', '.app')):
        with mock.patch.object(platform,
                               'system',
                               return_value=('Darwin')):
            with mock.patch.object(function,
                                   'checkPlateSolveAvailability',
                                   return_value=True):
                suc = function.selectAstrometryAppPath()
                assert suc


def test_selectAstapIndexPath_1(function):
    with mock.patch.object(MWidget,
                           'openDir',
                           return_value=('', '', '')):
        suc = function.selectAstapIndexPath()
        assert not suc


def test_selectAstapIndexPath_2(function):
    class Test:
        @staticmethod
        def checkAvailability():
            return True, True

        @staticmethod
        def selectAstapIndexPath():
            return True

    function.app.plateSolve.run = {'astap': Test()}
    with mock.patch.object(MWidget,
                           'openDir',
                           return_value=('test', 'test', 'test')):
        with mock.patch.object(function,
                               'checkPlateSolveAvailability',
                               return_value=True):
            suc = function.selectAstapIndexPath()
            assert suc


def test_selectAstapAppPath_1(function):
    with mock.patch.object(MWidget,
                           'openDir',
                           return_value=('', '', '')):
        suc = function.selectAstapAppPath()
        assert not suc


def test_selectAstapAppPath_2(function):
    with mock.patch.object(MWidget,
                           'openDir',
                           return_value=('test', 'test', 'test')):
        with mock.patch.object(function,
                               'checkPlateSolveAvailability',
                               return_value=True):
            suc = function.selectAstapAppPath()
            assert suc


def test_selectAstapAppPath_3(function):
    with mock.patch.object(MWidget,
                           'openDir',
                           return_value=('test', 'test', '.app')):
        with mock.patch.object(platform,
                               'system',
                               return_value=('Darwin')):
            with mock.patch.object(function,
                                   'checkPlateSolveAvailability',
                                   return_value=True):
                suc = function.selectAstapAppPath()
                assert suc


def test_selectWatneyIndexPath_1(function):
    with mock.patch.object(MWidget,
                           'openDir',
                           return_value=('', '', '')):
        suc = function.selectWatneyIndexPath()
        assert not suc


def test_selectWatneyIndexPath_2(function):
    class Test:
        @staticmethod
        def checkAvailability():
            return True, True

        @staticmethod
        def selectWatneyIndexPath():
            return True

    function.app.plateSolve.run = {'astap': Test()}
    with mock.patch.object(MWidget,
                           'openDir',
                           return_value=('test', 'test', 'test')):
        with mock.patch.object(function,
                               'checkPlateSolveAvailability',
                               return_value=True):
            suc = function.selectWatneyIndexPath()
            assert suc


def test_selectWatneyAppPath_1(function):
    with mock.patch.object(MWidget,
                           'openDir',
                           return_value=('', '', '')):
        suc = function.selectWatneyAppPath()
        assert not suc


def test_selectWatneyAppPath_2(function):
    with mock.patch.object(MWidget,
                           'openDir',
                           return_value=('test', 'test', 'test')):
        with mock.patch.object(function,
                               'checkPlateSolveAvailability',
                               return_value=True):
            suc = function.selectWatneyAppPath()
            assert suc


def test_selectWatneyAppPath_3(function):
    with mock.patch.object(MWidget,
                           'openDir',
                           return_value=('test', 'test', '.app')):
        with mock.patch.object(platform,
                               'system',
                               return_value=('Darwin')):
            with mock.patch.object(function,
                                   'checkPlateSolveAvailability',
                                   return_value=True):
                suc = function.selectWatneyAppPath()
                assert suc


def test_selectAscomDriver_1(function):
    if platform.system() != 'Windows':
        return

    with mock.patch.object(win32com.client,
                           'Dispatch',
                           side_effect=Exception()):
        suc = function.selectAscomDriver()
        assert not suc


def test_selectAscomDriver_2(function):
    if platform.system() != 'Windows':
        return

    class Test:
        DeviceType = None

        @staticmethod
        def Choose(name):
            return name

    function.ui.ascomDevice.setText('test')

    with mock.patch.object(win32com.client,
                           'Dispatch',
                           return_value=Test()):
        suc = function.selectAscomDriver()
        assert suc
        assert function.ui.ascomDevice.text() == 'test'
