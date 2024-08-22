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
        function.mountBoot()


def test_mountBoot_2(function):
    with mock.patch.object(function.app.mount,
                           'bootMount',
                           return_value=True):
        function.mountBoot()


def test_mountShutdown_1(function):
    with mock.patch.object(function.app.mount,
                           'shutdown',
                           return_value=False):
        function.mountShutdown()


def test_mountShutdown_2(function):
    with mock.patch.object(function.app.mount,
                           'shutdown',
                           return_value=True):
        function.mountShutdown()


def test_bootRackComp_1(function):
    with mock.patch.object(gui.mainWaddon.tabSett_Mount,
                           'checkFormatMAC',
                           return_value=False):
        with mock.patch.object(wakeonlan,
                               'send_magic_packet',
                               return_value=False):
            function.bootRackComp()


def test_bootRackComp_2(function):
    function.ui.rackCompMAC.setText('00:00:00:00:00:xy')
    with mock.patch.object(wakeonlan,
                           'send_magic_packet',
                           return_value=True):
        function.bootRackComp()


def test_mountHost_1(function):
    function.ui.port3492.setChecked(True)
    function.ui.mountHost.setText('')
    function.mountHost()


def test_mountHost_2(function):
    function.ui.port3490.setChecked(True)
    function.ui.mountHost.setText('192.168.2.1')
    with mock.patch.object(socket,
                           'gethostbyname',
                           return_value=True,
                           side_effect=Exception):
        function.mountHost()


def test_mountHost_3(function):
    function.ui.port3490.setChecked(True)
    function.ui.mountHost.setText('192.168.2.1')
    function.mountHost()
    assert function.app.mount.host == ('192.168.2.1', 3490)


def test_mountMAC(function):
    function.ui.mountMAC.setText('00:00:00:00:00:00')
    function.mountMAC()

    assert function.app.mount.MAC == '00:00:00:00:00:00'


def test_setMountMAC_1(function):
    function.setMountMAC()


def test_setMountMAC_2(function):
    class Test:
        addressLanMAC = None
        typeConnection = 0
    function.setMountMAC(sett=Test())


def test_setMountMAC_3(function):
    class Test:
        addressLanMAC = ''
        typeConnection = 0
    function.setMountMAC(sett=Test())


def test_setMountMAC_4(function):
    class Test:
        addressLanMAC = None
        typeConnection = 0
    function.app.mount.MAC = None
    function.setMountMAC(sett=Test())


def test_setMountMAC_5(function):
    class Test:
        addressLanMAC = '00:00:0xx:00:00:00'
        typeConnection = 3
    function.setMountMAC(sett=Test())


def test_setMountMAC_6(function):
    class Test:
        addressLanMAC = '00:00:00:00:00:00'
        typeConnection = 3
    function.app.mount.MAC = '00:00:00:00:00:00'
    function.setMountMAC(Test())


def test_updateFwGui_1(function):
    function.updateFwGui(function.app.mount.firmware)


def test_setWaitTimeFlip_1(function):
    function.setWaitTimeFlip()


def test_toggleClockSync_1(function):
    function.ui.clockSync.setChecked(True)
    function.toggleClockSync()


def test_toggleClockSync_2(function):
    function.ui.clockSync.setChecked(False)
    function.toggleClockSync()


def test_syncClock_1(function):
    function.ui.syncTimeNone.setChecked(True)
    function.syncClock()


def test_syncClock_2(function):
    function.ui.syncTimeNotTrack.setChecked(True)
    function.app.deviceStat['mount'] = False
    function.syncClock()


def test_syncClock_3(function):
    function.ui.syncTimeNotTrack.setChecked(True)
    function.app.deviceStat['mount'] = True
    function.app.mount.obsSite.status = 0
    function.syncClock()


@mock.patch('tests.unit_tests.unitTestAddOns.baseTestApp.App.mount.obsSite.timeDiff', 0.005)
def test_syncClock_4(function):
    function.ui.syncTimeCont.setChecked(True)
    function.app.deviceStat['mount'] = True
    function.app.mount.obsSite.status = 1
    function.syncClock()


@mock.patch('tests.unit_tests.unitTestAddOns.baseTestApp.App.mount.obsSite.timeDiff', 1)
def test_syncClock_5(function):
    function.ui.syncTimeCont.setChecked(False)
    function.app.deviceStat['mount'] = True
    function.app.mount.obsSite.status = 1
    with mock.patch.object(function.app.mount.obsSite,
                           'adjustClock',
                           return_value=False):
        function.syncClock()


@mock.patch('tests.unit_tests.unitTestAddOns.baseTestApp.App.mount.obsSite.timeDiff', -1)
def test_syncClock_6(function):
    function.ui.syncTimeCont.setChecked(True)
    function.app.deviceStat['mount'] = True
    function.app.mount.obsSite.status = 1
    with mock.patch.object(function.app.mount.obsSite,
                           'adjustClock',
                           return_value=True):
        function.syncClock()


def test_updateTelescopeParametersToGui_1(function):
    function.app.telescope.data['TELESCOPE_INFO.TELESCOPE_FOCAL_LENGTH'] = 1
    function.app.telescope.data['TELESCOPE_INFO.TELESCOPE_APERTURE'] = 1

    function.updateTelescopeParametersToGui()


def test_updateTelescopeParametersToGuiCyclic_1(function):
    function.ui.automaticTelescope.setChecked(False)
    function.updateTelescopeParametersToGuiCyclic()


def test_updateTelescopeParametersToGuiCyclic_2(function):
    function.ui.automaticTelescope.setChecked(True)
    with mock.patch.object(function,
                           'updateTelescopeParametersToGui'):
        function.updateTelescopeParametersToGuiCyclic()

