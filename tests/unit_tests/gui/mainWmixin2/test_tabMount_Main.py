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

# external packages
from skyfield.api import Angle

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.utilities.toolsQtWidget import MWidget
from gui.widgets.main_ui import Ui_MainWindow
from gui.mainWmixin.tabMount_Main import MountMain
import mountcontrol


@pytest.fixture(autouse=True, scope='module')
def function(qapp):
    class Mixin(MWidget, MountMain):
        def __init__(self):
            super().__init__()
            self.app = App()
            self.msg = self.app.msg
            self.deviceStat = self.app.deviceStat
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)
            MountMain.__init__(self)

    window = Mixin()
    yield window


def test_initConfig_1(function):
    function.app.config['mainW'] = {}
    suc = function.initConfig()
    assert suc


def test_initConfig_2(function):
    del function.app.config['mainW']
    suc = function.initConfig()
    assert suc


def test_storeConfig_1(function):
    function.app.config['mainW'] = {}
    suc = function.storeConfig()
    assert suc


def test_updatePointGui_ra_j2000(function):
    function.ui.coordsJ2000.setChecked(True)
    value = Angle(hours=45)
    function.app.mount.obsSite.raJNow = value
    value = Angle(degrees=45)
    function.app.mount.obsSite.decJNow = value
    function.updatePointGUI(function.app.mount.obsSite)


def test_updatePointGUI_sidereal_1(function):
    value = Angle(hours=12)
    function.app.mount.obsSite.timeSidereal = value
    function.updatePointGUI(function.app.mount.obsSite)
    assert '12:00:00' == function.ui.timeSidereal.text()


def test_updatePointGUI_sidereal_2(function):
    value = None
    function.app.mount.obsSite.timeSidereal = value
    function.updatePointGUI(function.app.mount.obsSite)
    assert '-' == function.ui.timeSidereal.text()


def test_updatePointGui_alt(function):
    value = Angle(degrees=45)
    function.app.mount.obsSite.Alt = value
    function.updatePointGUI(function.app.mount.obsSite)
    assert '45.00' == function.ui.ALT.text()
    value = None
    function.app.mount.obsSite.Alt = value
    function.updatePointGUI(function.app.mount.obsSite)
    assert '-' == function.ui.ALT.text()


def test_updatePointGui_az(function):
    value = Angle(degrees=45)
    function.app.mount.obsSite.Az = value
    function.updatePointGUI(function.app.mount.obsSite)
    assert '45.00' == function.ui.AZ.text()
    value = None
    function.app.mount.obsSite.Az = value
    function.updatePointGUI(function.app.mount.obsSite)
    assert '-' == function.ui.AZ.text()


def test_updatePointGui_ra(function):
    function.ui.coordsJ2000.setChecked(True)
    function.app.mount.obsSite.raJNow = Angle(hours=0)
    function.updatePointGUI(function.app.mount.obsSite)
    assert '23:58:53' == function.ui.RA.text()


def test_updatePointGui_dec_1(function):
    function.ui.coordsJ2000.setChecked(True)
    function.app.mount.obsSite.decJNow = Angle(degrees=0)
    function.updatePointGUI(function.app.mount.obsSite)
    assert '-00:07:13' == function.ui.DEC.text()


def test_updatePointGui_dec_2(function):
    function.app.mount.obsSite.decJNow = None
    function.ui.coordsJ2000.setChecked(False)
    function.updatePointGUI(function.app.mount.obsSite)
    assert '-' == function.ui.DEC.text()


def test_updatePointGui_pierside(function):
    value = 'W'
    function.app.mount.obsSite.pierside = value
    function.updatePointGUI(function.app.mount.obsSite)
    assert 'WEST' == function.ui.pierside.text()


def test_updatePointGui_ha_1(function):
    value = Angle(hours=12)
    function.app.mount.obsSite.haJNow = value
    function.app.mount.obsSite.timeSidereal = value
    function.updatePointGUI(function.app.mount.obsSite)
    assert '12:00:00' == function.ui.HA.text()


def test_updatePointGui_ha_2(function):
    value = None
    function.app.mount.obsSite.timeSidereal = value
    function.app.mount.obsSite.haJNow = value
    function.updatePointGUI(function.app.mount.obsSite)
    assert '-' == function.ui.HA.text()


def test_checkMount_1(function):
    function.app.deviceStat['mount'] = False
    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        suc = function.checkMount()
        assert not suc


def test_checkMount_2(function):
    function.app.deviceStat['mount'] = True
    with mock.patch.object(function,
                           'messageDialog',
                           return_value=True):
        suc = function.checkMount()
        assert suc


def test_changeTrackingGameController_1(function):
    with mock.patch.object(function,
                           'changeTracking'):
        suc = function.changeTrackingGameController(4)
        assert suc


def test_changeTracking_ok1(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=False):
        suc = function.changeTracking()
        assert not suc


def test_changeTracking_ok2(function, qtbot):
    function.app.mount.obsSite.status = 0
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        with mock.patch.object(function.app.mount.obsSite,
                               'stopTracking',
                               return_value=False):
            suc = function.changeTracking()
            assert suc


def test_changeTracking_ok3(function, qtbot):
    function.app.mount.obsSite.status = 0
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        with mock.patch.object(function.app.mount.obsSite,
                               'stopTracking',
                               return_value=True):
            suc = function.changeTracking()
            assert suc


def test_changeTracking_ok4(function):
    function.app.mount.obsSite.status = 1
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        with mock.patch.object(function.app.mount.obsSite,
                               'startTracking',
                               return_value=True):
            suc = function.changeTracking()
            assert suc


def test_changeTracking_ok5(function):
    function.app.mount.obsSite.status = 1
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        with mock.patch.object(function.app.mount.obsSite,
                               'startTracking',
                               return_value=False):
            suc = function.changeTracking()
            assert suc


def test_changeParkGameController_1(function):
    with mock.patch.object(function,
                           'changePark'):
        suc = function.changeParkGameController(1)
        assert suc


def test_changePark_ok1(function):
    function.app.mount.obsSite.status = 5
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        with mock.patch.object(function.app.mount.obsSite,
                               'unpark',
                               return_value=False):
            suc = function.changePark()
            assert suc


def test_changePark_ok2(function):
    function.app.mount.obsSite.status = 5
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        with mock.patch.object(function.app.mount.obsSite,
                               'unpark',
                               return_value=True):
            suc = function.changePark()
            assert suc


def test_changePark_ok3(function):
    function.app.mount.obsSite.status = 1
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        with mock.patch.object(function.app.mount.obsSite,
                               'park',
                               return_value=False):
            suc = function.changePark()
            assert suc


def test_changePark_ok4(function):
    function.app.mount.obsSite.status = 1
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        with mock.patch.object(function.app.mount.obsSite,
                               'park',
                               return_value=True):
            suc = function.changePark()
            assert suc


def test_changePark_notok(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=False):
        with mock.patch.object(function.app.mount.obsSite,
                               'park',
                               return_value=True):
            suc = function.changePark()
            assert not suc


def test_setLunarTracking_1(function):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        with mock.patch.object(function.app.mount.setting,
                               'setLunarTracking',
                               return_value=True):
            suc = function.setLunarTracking()
            assert suc


def test_setLunarTracking_2(function):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        with mock.patch.object(function.app.mount.setting,
                               'setLunarTracking',
                               return_value=False):
            suc = function.setLunarTracking()
            assert not suc


def test_setLunarTracking_3(function):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=False):
        with mock.patch.object(function.app.mount.setting,
                               'setLunarTracking',
                               return_value=True):
            suc = function.setLunarTracking()
            assert not suc


def test_setSiderealTracking_1(function):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=False):
        suc = function.setSiderealTracking()
        assert not suc


def test_setSiderealTracking_2(function):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        with mock.patch.object(function.app.mount.setting,
                               'setSiderealTracking',
                               return_value=False):
            suc = function.setSiderealTracking()
            assert not suc


def test_setSiderealTracking_3(function):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        with mock.patch.object(function.app.mount.setting,
                               'setSiderealTracking',
                               return_value=True):
            suc = function.setSiderealTracking()
            assert suc


def test_setSolarTracking_1(function):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=False):
        suc = function.setSolarTracking()
        assert not suc


def test_setSolarTracking_2(function):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        with mock.patch.object(function.app.mount.setting,
                               'setSolarTracking',
                               return_value=False):
            suc = function.setSolarTracking()
            assert not suc


def test_setSolarTracking_3(function):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        with mock.patch.object(function.app.mount.setting,
                               'setSolarTracking',
                               return_value=True):
            suc = function.setSolarTracking()
            assert suc


def test_flipMountGameController_1(function):
    with mock.patch.object(function,
                           'flipMount'):
        suc = function.flipMountGameController(2)
        assert suc


def test_flipMount_1(function):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        with mock.patch.object(function.app.mount.obsSite,
                               'flip',
                               return_value=False):
            suc = function.flipMount()
            assert not suc


def test_flipMount_2(function):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        with mock.patch.object(function.app.mount.obsSite,
                               'flip',
                               return_value=True):
            suc = function.flipMount()
            assert suc


def test_flipMount_3(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=False):
        with mock.patch.object(function.app.mount.obsSite,
                               'flip',
                               return_value=True):
            suc = function.flipMount()
            assert not suc


def test_stopGameController_1(function):
    with mock.patch.object(function,
                           'flipMount'):
        suc = function.stopGameController(8)
        assert suc


def test_stop_1(function):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        with mock.patch.object(function.app.mount.obsSite,
                               'stop',
                               return_value=True):
            suc = function.stop()
            assert suc


def test_stop_2(function):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        with mock.patch.object(function.app.mount.obsSite,
                               'stop',
                               return_value=False):
            suc = function.stop()
            assert not suc


def test_test_stop_3(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=False):
        with mock.patch.object(function.app.mount.obsSite,
                               'stop',
                               return_value=True):
            suc = function.stop()
            assert not suc
