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
import pytest
import socket
import astropy

# external packages
import wakeonlan
from PySide6.QtWidgets import QWidget

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
import gui
from gui.widgets.main_ui import Ui_MainWindow
from gui.mainWaddon.tabSett_Mount import SettMount


@pytest.fixture(autouse=True, scope='module')
def function(qapp):

    mainW = QWidget()
    mainW.app = App()
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)
    window = SettMount(mainW)
    yield window
    mainW.app.threadPool.waitForDone(1000)


def test_initConfig_1(function):
    function.app.config['mainW'] = {'automaticWOL': True}
    with mock.patch.object(function,
                           'mountBoot'):
        function.initConfig()


def test_storeConfig1(function):
    function.storeConfig()


def test_mountBoot_1(function):
    with mock.patch.object(function.app.mount,
                           'bootMount',
                           return_value=False):
        suc = function.mountBoot()
        assert not suc


def test_mountBoot_2(function):
    with mock.patch.object(function.app.mount,
                           'bootMount',
                           return_value=True):
        suc = function.mountBoot()
        assert suc


def test_mountShutdown_1(function):
    with mock.patch.object(function.app.mount,
                           'shutdown',
                           return_value=False):
        suc = function.mountShutdown()
        assert not suc


def test_mountShutdown_2(function):
    with mock.patch.object(function.app.mount,
                           'shutdown',
                           return_value=True):
        suc = function.mountShutdown()
        assert suc


def test_bootRackComp_1(function):
    with mock.patch.object(gui.mainWaddon.tabSett_Mount,
                           'checkFormatMAC',
                           return_value=False):
        with mock.patch.object(wakeonlan,
                               'send_magic_packet',
                               return_value=False):
            suc = function.bootRackComp()
            assert suc


def test_bootRackComp_2(function):
    function.ui.rackCompMAC.setText('00:00:00:00:00:xy')
    with mock.patch.object(wakeonlan,
                           'send_magic_packet',
                           return_value=True):
        suc = function.bootRackComp()
        assert not suc


def test_mountHost_1(function):
    function.ui.port3492.setChecked(True)
    function.ui.mountHost.setText('')
    suc = function.mountHost()
    assert not suc


def test_mountHost_2(function):
    function.ui.port3490.setChecked(True)
    function.ui.mountHost.setText('192.168.2.1')
    with mock.patch.object(socket,
                           'gethostbyname',
                           return_value=True,
                           side_effect=Exception):
        suc = function.mountHost()
        assert not suc


def test_mountHost_3(function):
    function.ui.port3490.setChecked(True)
    function.ui.mountHost.setText('192.168.2.1')
    suc = function.mountHost()
    assert suc
    assert function.app.mount.host == ('192.168.2.1', 3490)


def test_mountMAC(function):
    function.ui.mountMAC.setText('00:00:00:00:00:00')
    function.mountMAC()

    assert function.app.mount.MAC == '00:00:00:00:00:00'


def test_setMountMAC_1(function):
    suc = function.setMountMAC()
    assert not suc


def test_setMountMAC_2(function):
    class Test:
        addressLanMAC = None
        typeConnection = 0
    suc = function.setMountMAC(sett=Test())
    assert not suc


def test_setMountMAC_3(function):
    class Test:
        addressLanMAC = ''
        typeConnection = 0
    suc = function.setMountMAC(sett=Test())
    assert not suc


def test_setMountMAC_4(function):
    class Test:
        addressLanMAC = None
        typeConnection = 0
    function.app.mount.MAC = None
    suc = function.setMountMAC(sett=Test())
    assert not suc


def test_setMountMAC_5(function):
    class Test:
        addressLanMAC = '00:00:0xx:00:00:00'
        typeConnection = 3
    suc = function.setMountMAC(sett=Test())
    assert suc


def test_setMountMAC_6(function):
    class Test:
        addressLanMAC = '00:00:00:00:00:00'
        typeConnection = 3
    function.app.mount.MAC = '00:00:00:00:00:00'
    suc = function.setMountMAC(Test())
    assert suc


def test_setWaitTimeFlip_1(function):
    suc = function.setWaitTimeFlip()
    assert suc


def test_updateFwGui_productName(function):
    value = 'Test1234'
    function.app.mount.firmware.product = value
    function.updateFwGui(function.app.mount.firmware)
    assert value == function.ui.product.text()
    value = None
    function.app.mount.firmware.product = value
    function.updateFwGui(function.app.mount.firmware)
    assert '-' == function.ui.product.text()


def test_updateFwGui_hwVersion(function):
    value = 'Test1234'
    function.app.mount.firmware.hardware = value
    function.updateFwGui(function.app.mount.firmware)
    assert value == function.ui.hardware.text()
    value = None
    function.app.mount.firmware.hardware = value
    function.updateFwGui(function.app.mount.firmware)
    assert '-' == function.ui.hardware.text()


def test_updateFwGui_numberString(function):
    value = '2.15.18'
    function.app.mount.firmware.vString = value
    function.updateFwGui(function.app.mount.firmware)
    assert value == function.ui.vString.text()
    value = None
    function.app.mount.firmware.vString = value
    function.updateFwGui(function.app.mount.firmware)
    assert '-' == function.ui.vString.text()


def test_updateFwGui_fwdate(function):
    value = 'Test1234'
    function.app.mount.firmware.date = value
    function.updateFwGui(function.app.mount.firmware)
    assert value == function.ui.fwdate.text()
    value = None
    function.app.mount.firmware.date = value
    function.updateFwGui(function.app.mount.firmware)
    assert '-' == function.ui.fwdate.text()


def test_updateFwGui_fwtime(function):
    value = 'Test1234'
    function.app.mount.firmware.time = value
    function.updateFwGui(function.app.mount.firmware)
    assert value == function.ui.fwtime.text()
    value = None
    function.app.mount.firmware.time = value
    function.updateFwGui(function.app.mount.firmware)
    assert '-' == function.ui.fwtime.text()


def test_toggleClockSync_1(function):
    function.ui.clockSync.setChecked(True)
    suc = function.toggleClockSync()
    assert suc


def test_toggleClockSync_2(function):
    function.ui.clockSync.setChecked(False)
    suc = function.toggleClockSync()
    assert suc


def test_syncClock_1(function):
    function.ui.syncTimeNone.setChecked(True)
    suc = function.syncClock()
    assert not suc


def test_syncClock_2(function):
    function.ui.syncTimeNotTrack.setChecked(True)
    function.app.deviceStat['mount'] = False
    suc = function.syncClock()
    assert not suc


def test_syncClock_3(function):
    function.ui.syncTimeNotTrack.setChecked(True)
    function.app.deviceStat['mount'] = True
    function.app.mount.obsSite.status = 0
    suc = function.syncClock()
    assert not suc


@mock.patch('tests.unit_tests.unitTestAddOns.baseTestApp.App.mount.obsSite.timeDiff', 0.005)
def test_syncClock_4(function):
    function.ui.syncTimeCont.setChecked(True)
    function.app.deviceStat['mount'] = True
    function.app.mount.obsSite.status = 1
    suc = function.syncClock()
    assert not suc


@mock.patch('tests.unit_tests.unitTestAddOns.baseTestApp.App.mount.obsSite.timeDiff', 1)
def test_syncClock_5(function):
    function.ui.syncTimeCont.setChecked(False)
    function.app.deviceStat['mount'] = True
    function.app.mount.obsSite.status = 1
    with mock.patch.object(function.app.mount.obsSite,
                           'adjustClock',
                           return_value=False):
        suc = function.syncClock()
        assert not suc


@mock.patch('tests.unit_tests.unitTestAddOns.baseTestApp.App.mount.obsSite.timeDiff', -1)
def test_syncClock_6(function):
    function.ui.syncTimeCont.setChecked(True)
    function.app.deviceStat['mount'] = True
    function.app.mount.obsSite.status = 1
    with mock.patch.object(function.app.mount.obsSite,
                           'adjustClock',
                           return_value=True):
        suc = function.syncClock()
        assert suc


def test_updateTelescopeParametersToGui_1(function):
    function.app.telescope.data['TELESCOPE_INFO.TELESCOPE_FOCAL_LENGTH'] = 1
    function.app.telescope.data['TELESCOPE_INFO.TELESCOPE_APERTURE'] = 1

    suc = function.updateTelescopeParametersToGui()
    assert suc


def test_updateTelescopeParametersToGuiCyclic_1(function):
    function.ui.automaticTelescope.setChecked(False)
    suc = function.updateTelescopeParametersToGuiCyclic()
    assert not suc


def test_updateTelescopeParametersToGuiCyclic_2(function):
    function.ui.automaticTelescope.setChecked(True)
    with mock.patch.object(function,
                           'updateTelescopeParametersToGui'):
        suc = function.updateTelescopeParametersToGuiCyclic()
        assert suc
