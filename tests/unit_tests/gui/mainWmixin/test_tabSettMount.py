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
import pytest

# external packages
import wakeonlan

# local import
from tests.baseTestSetupMixins import App
from gui.utilities.toolsQtWidget import MWidget
from gui.widgets.main_ui import Ui_MainWindow
from gui.mainWmixin.tabSettMount import SettMount


@pytest.fixture(autouse=True, scope='module')
def module(qapp):
    yield


@pytest.fixture(autouse=True, scope='function')
def function(module):

    class Mixin(MWidget, SettMount):
        def __init__(self):
            super().__init__()
            self.app = App()
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)
            SettMount.__init__(self)

    window = Mixin()
    yield window


def test_initConfig_1(function):
    function.app.config['mainW'] = {}
    suc = function.initConfig()
    assert suc


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


def test_storeConfig_1(function):
    function.storeConfig()


def test_checkFormatMAC_1(function):
    val = function.checkFormatMAC('')
    assert val is None


def test_checkFormatMAC_2(function):
    val = function.checkFormatMAC(5)
    assert val is None


def test_checkFormatMAC_3(function):
    val = function.checkFormatMAC('test')
    assert val is None


def test_checkFormatMAC_4(function):
    val = function.checkFormatMAC('00:00:00')
    assert val is None


def test_checkFormatMAC_5(function):
    val = function.checkFormatMAC('00:00:00:00.00.kk')
    assert val is None


def test_checkFormatMAC_6(function):
    val = function.checkFormatMAC('00.11.22:ab:44:55')
    assert val == '00:11:22:AB:44:55'


def test_checkFormatMAC_7(function):
    val = function.checkFormatMAC('00.11.2:ab:44:55')
    assert val is None


def test_bootRackComp_1(function):
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


def test_mountHost(function):
    function.ui.mountHost.setText('test')
    function.mountHost()

    assert function.app.mount.host == 'test'


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


def test_setMountSettlingTime_1(function):
    suc = function.setMountSettlingTime()
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
