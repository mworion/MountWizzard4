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
import unittest.mock as mock
import pytest
import platform
import faulthandler
faulthandler.enable()

# external packages
import PyQt5.QtWidgets
import PyQt5.QtTest
import PyQt5.QtCore
from PyQt5.QtGui import QCloseEvent
from indibase.indiBase import Device
if platform.system() == 'Windows':
    import win32com.client
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QObject

# local import
from gui.extWindows.devicePopupW import DevicePopup
from mw4.base.indiClass import IndiClass
from indibase.qtIndiBase import Client
from gui.utilities.widget import MWidget
from logic.astrometry import Astrometry


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown(qtbot):
    global app, data, geometry, availFramework

    class Test1(QObject):
        threadPool = QThreadPool()
        message = pyqtSignal(object, object)
        mwGlob = {'tempDir': 'mw4/test/temp'}

    class Test:
        astrometry = Astrometry(app=Test1())

    data = {
        'telescope':
            {
                'indiDeviceList': ['test1', 'test2']
                }
            }
    geometry = [100, 100, 100, 100]
    availFramework = ['indi', 'alpaca']

    with mock.patch.object(DevicePopup,
                           'show'):
        app = DevicePopup(app=Test(),
                          geometry=geometry,
                          data=data,
                          availFramework=availFramework,
                          driver='telescope',
                          deviceType='telescope')
        qtbot.addWidget(app)

        yield


def test_initConfig_1():
    suc = app.initConfig()
    assert suc


def test_initConfig_2():
    app.data = {
        'telescope':
            {
                'indiName': 'telescope',
                'indiDeviceList': ['telescope', 'test2']
                }
            }

    suc = app.initConfig()
    assert suc


def test_initConfig_3():
    app.data = {
            }

    suc = app.initConfig()
    assert suc


def test_initConfig_4():
    app.data = {
        'telescope':
            {
                'astrometryName': 'telescope',
                'astrometryDeviceList': ['telescope', 'test2']
                }
            }

    suc = app.initConfig()
    assert suc


def test_storeConfig_1(qtbot):
    app.close = MWidget().close
    app.deleteLater = MWidget().deleteLater
    qtbot.addWidget(app)

    suc = app.storeConfig()
    assert suc


def test_closeEvent_1(qtbot):
    app.close = MWidget().close
    app.deleteLater = MWidget().deleteLater
    qtbot.addWidget(app)
    app.closeEvent(QCloseEvent())


def test_copyAllIndiSettings_1(qtbot):
    suc = app.copyAllIndiSettings()
    assert suc


def test_copyAllAlpacaSettings_1(qtbot):
    suc = app.copyAllAlpacaSettings()
    assert suc


def test_AddDevicesWithType_1(qtbot):
    device = Device()
    app._indiClass = IndiClass()
    with mock.patch.object(device,
                           'getText',
                           return_value={'DRIVER_INTERFACE': None}):
        suc = app.addDevicesWithType('telescope', 'test')
        assert not suc


def test_AddDevicesWithType_2(qtbot):
    device = Device()
    app._indiClass = IndiClass()
    app._indiClass.client.devices['telescope'] = device
    with mock.patch.object(device,
                           'getText',
                           return_value={'DRIVER_INTERFACE': None}):
        suc = app.addDevicesWithType('telescope', 'test')
        assert not suc


def test_AddDevicesWithType_3(qtbot):
    device = Device()
    app._indiClass = IndiClass()
    app._indiClass.client.devices['telescope'] = device
    app._indiSearchType = None
    with mock.patch.object(device,
                           'getText',
                           return_value={'DRIVER_INTERFACE': 0}):
        suc = app.addDevicesWithType('telescope', 'test')
        assert not suc


def test_AddDevicesWithType_4(qtbot):
    device = Device()
    app._indiClass = IndiClass()
    app._indiClass.client.devices['telescope'] = device
    app._indiSearchType = 1
    app._indiSearchNameList = list()
    with mock.patch.object(device,
                           'getText',
                           return_value={'DRIVER_INTERFACE': 1}):
        suc = app.addDevicesWithType('telescope', 'test')
        assert suc


def test_searchDevices_1(qtbot):
    suc = app.searchDevices()
    assert suc


def test_searchDevices_2(qtbot):
    app.driver = 'test'
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'information',
                           return_value=True):
        with mock.patch.object(Client,
                               'connectServer'):
            with mock.patch.object(Client,
                                   'watchDevice'):
                with mock.patch.object(Client,
                                       'disconnectServer'):
                    suc = app.searchDevices()
                    assert suc


def test_selectAstrometryIndexPath_1(qtbot):
    with mock.patch.object(MWidget,
                           'openDir',
                           return_value=('', '', '')):
        suc = app.selectAstrometryIndexPath()
        assert not suc


def test_selectAstrometryIndexPath_2(qtbot):
    with mock.patch.object(MWidget,
                           'openDir',
                           return_value=('test', 'test', 'test')):
        suc = app.selectAstrometryIndexPath()
        assert suc


def test_selectAstrometryAppPath_1(qtbot):
    with mock.patch.object(MWidget,
                           'openDir',
                           return_value=('', '', '')):
        suc = app.selectAstrometryAppPath()
        assert not suc


def test_selectAstrometryAppPath_2(qtbot):
    with mock.patch.object(MWidget,
                           'openDir',
                           return_value=('test', 'test', 'test')):
        suc = app.selectAstrometryAppPath()
        assert suc


def test_selectAstapIndexPath_1(qtbot):
    with mock.patch.object(MWidget,
                           'openDir',
                           return_value=('', '', '')):
        suc = app.selectAstapIndexPath()
        assert not suc


def test_selectAstapIndexPath_2(qtbot):
    with mock.patch.object(MWidget,
                           'openDir',
                           return_value=('test', 'test', 'test')):
        suc = app.selectAstapIndexPath()
        assert suc


def test_selectAstapAppPath_1(qtbot):
    with mock.patch.object(MWidget,
                           'openDir',
                           return_value=('', '', '')):
        suc = app.selectAstapAppPath()
        assert not suc


def test_selectAstapAppPath_2(qtbot):
    with mock.patch.object(MWidget,
                           'openDir',
                           return_value=('test', 'test', 'test')):
        suc = app.selectAstapAppPath()
        assert suc


def test_setupAscomDriver_1():
    if platform.system() != 'Windows':
        return

    with mock.patch.object(win32com.client,
                           'Dispatch',
                           side_effect=Exception()):
        suc = app.setupAscomDriver()
        assert not suc


def test_setupAscomDriver_2():
    if platform.system() != 'Windows':
        return

    class Test:
        DeviceType = None

        @staticmethod
        def Choose(name):
            return name

    app.ui.ascomDevice.setText('test')

    with mock.patch.object(win32com.client,
                           'Dispatch',
                           return_value=Test()):
        suc = app.setupAscomDriver()
        assert suc
        assert app.ui.ascomDevice.text() == 'test'
