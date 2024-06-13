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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import pytest
import datetime
import webbrowser

# external packages
import PySide6
from PySide6.QtWidgets import QWidget, QInputDialog
from skyfield.api import Angle, wgs84

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.utilities.toolsQtWidget import MWidget
from gui.widgets.main_ui import Ui_MainWindow
from gui.mainWmixin.tabMount import Mount
import gui.mainWmixin.tabMount
import mountcontrol


@pytest.fixture(autouse=True, scope='module')
def function(qapp):
    class Mixin(MWidget, Mount):
        def __init__(self):
            super().__init__()
            self.app = App()
            self.msg = self.app.msg
            self.deviceStat = self.app.deviceStat
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)
            Mount.__init__(self)

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


def test_setMeridianLimitTrack_1(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=False):
        function.app.mount.setting.meridianLimitTrack = None
        with mock.patch.object(PySide6.QtWidgets.QMessageBox,
                               'critical',
                               return_value=True):
            suc = function.setMeridianLimitTrack()
            assert not suc


def test_setMeridianLimitTrack_2(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.meridianLimitTrack = 10
        with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                               'getInt',
                               return_value=(10, False)):
            suc = function.setMeridianLimitTrack()
            assert not suc


def test_setMeridianLimitTrack_3(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.meridianLimitTrack = 10
        with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                               'getInt',
                               return_value=(10, True)):
            with mock.patch.object(function.app.mount.setting,
                                   'setMeridianLimitTrack',
                                   return_value=False):
                suc = function.setMeridianLimitTrack()
                assert not suc


def test_setMeridianLimitTrack_4(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.meridianLimitTrack = 10
        with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                               'getInt',
                               return_value=(10, True)):
            with mock.patch.object(function.app.mount.setting,
                                   'setMeridianLimitTrack',
                                   return_value=True):
                suc = function.setMeridianLimitTrack()
                assert suc


def test_setMeridianLimitSlew_1(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=False):
        function.app.mount.setting.meridianLimitSlew = None
        with mock.patch.object(PySide6.QtWidgets.QMessageBox,
                               'critical',
                               return_value=True):
            suc = function.setMeridianLimitSlew()
            assert not suc


def test_setMeridianLimitSlew_2(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.meridianLimitSlew = 10
        with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                               'getInt',
                               return_value=(10, False)):
            suc = function.setMeridianLimitSlew()
            assert not suc


def test_setMeridianLimitSlew_3(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.meridianLimitSlew = 10
        with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                               'getInt',
                               return_value=(10, True)):
            with mock.patch.object(function.app.mount.setting,
                                   'setMeridianLimitSlew',
                                   return_value=False):
                suc = function.setMeridianLimitSlew()
                assert not suc


def test_setMeridianLimitSlew_4(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.meridianLimitSlew = 10
        with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                               'getInt',
                               return_value=(10, True)):
            with mock.patch.object(function.app.mount.setting,
                                   'setMeridianLimitSlew',
                                   return_value=True):
                suc = function.setMeridianLimitSlew()
                assert suc


def test_setHorizonLimitHigh_1(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=False):
        function.app.mount.setting.horizonLimitHigh = None
        with mock.patch.object(PySide6.QtWidgets.QMessageBox,
                               'critical',
                               return_value=True):
            suc = function.setHorizonLimitHigh()
            assert not suc


def test_setHorizonLimitHigh_2(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.horizonLimitHigh = 10
        with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                               'getInt',
                               return_value=(10, False)):
            suc = function.setHorizonLimitHigh()
            assert not suc


def test_setHorizonLimitHigh_3(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.horizonLimitHigh = 10
        with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                               'getInt',
                               return_value=(10, True)):
            with mock.patch.object(function.app.mount.setting,
                                   'setHorizonLimitHigh',
                                   return_value=False):
                suc = function.setHorizonLimitHigh()
                assert not suc


def test_setHorizonLimitHigh_4(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.horizonLimitHigh = 10
        with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                               'getInt',
                               return_value=(10, True)):
            with mock.patch.object(function.app.mount.setting,
                                   'setHorizonLimitHigh',
                                   return_value=True):
                suc = function.setHorizonLimitHigh()
                assert suc


def test_setHorizonLimitLow_1(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=False):
        function.app.mount.setting.horizonLimitLow = None
        with mock.patch.object(PySide6.QtWidgets.QMessageBox,
                               'critical',
                               return_value=True):
            suc = function.setHorizonLimitLow()
            assert not suc


def test_setHorizonLimitLow_2(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.horizonLimitLow = 10
        with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                               'getInt',
                               return_value=(10, False)):
            suc = function.setHorizonLimitLow()
            assert not suc


def test_setHorizonLimitLow_3(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.horizonLimitLow = 10
        with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                               'getInt',
                               return_value=(10, True)):
            with mock.patch.object(function.app.mount.setting,
                                   'setHorizonLimitLow',
                                   return_value=False):
                suc = function.setHorizonLimitLow()
                assert not suc


def test_setHorizonLimitLow_4(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.horizonLimitLow = 10
        with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                               'getInt',
                               return_value=(10, True)):
            with mock.patch.object(function.app.mount.setting,
                                   'setHorizonLimitLow',
                                   return_value=True):
                suc = function.setHorizonLimitLow()
                assert suc


def test_setSlewRate_1(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=False):
        suc = function.setSlewRate()
        assert not suc


def test_setSlewRate_2(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.slewRate = 10
        with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                               'getInt',
                               return_value=(10, False)):
            suc = function.setSlewRate()
            assert not suc


def test_setSlewRate_3(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.slewRate = 10
        with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                               'getInt',
                               return_value=(10, True)):
            with mock.patch.object(function.app.mount.setting,
                                   'setSlewRate',
                                   return_value=False):
                suc = function.setSlewRate()
                assert not suc


def test_setSlewRate_4(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.slewRate = 10
        with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                               'getInt',
                               return_value=(10, True)):
            with mock.patch.object(function.app.mount.setting,
                                   'setSlewRate',
                                   return_value=True):
                suc = function.setSlewRate()
                assert suc


def test_setLocationValues_1(function):
    function.app.mount.obsSite.location = wgs84.latlon(longitude_degrees=1,
                                                       latitude_degrees=2,
                                                       elevation_m=3)
    function.app.deviceStat['mount'] = True
    with mock.patch.object(function.app.mount,
                           'getLocation'):
        with mock.patch.object(function.app.mount.obsSite,
                               'setLocation'):
            suc = function.setLocationValues()
            assert suc


def test_setLocationValues_2(function):
    function.app.mount.obsSite.location = wgs84.latlon(longitude_degrees=1,
                                                       latitude_degrees=2,
                                                       elevation_m=3)
    function.app.deviceStat['mount'] = False
    with mock.patch.object(function,
                           'updateLocGUI'):
        suc = function.setLocationValues()
        assert suc


def test_setLongitude_1(function):
    function.app.mount.obsSite.location = None
    suc = function.setLongitude()
    assert not suc


def test_setLongitude_2(function):
    function.app.mount.obsSite.location = wgs84.latlon(longitude_degrees=1,
                                                       latitude_degrees=2,
                                                       elevation_m=3)
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                           'getText',
                           return_value=('011E 40 40', False)):
        suc = function.setLongitude()
        assert not suc


def test_setLongitude_3(function):
    function.app.mount.obsSite.location = wgs84.latlon(longitude_degrees=1,
                                                       latitude_degrees=2,
                                                       elevation_m=3)
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                           'getText',
                           return_value=('011E 40 40', True)):
        with mock.patch.object(function,
                               'setLocationValues'):
            suc = function.setLongitude()
            assert suc


def test_setLatitude_1(function):
    function.app.mount.obsSite.location = None
    suc = function.setLatitude()
    assert not suc


def test_setLatitude_2(function):
    function.app.mount.obsSite.location = wgs84.latlon(longitude_degrees=1,
                                                       latitude_degrees=2,
                                                       elevation_m=3)
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                           'getText',
                           return_value=('48N 00 00', False)):
        suc = function.setLatitude()
        assert not suc


def test_setLatitude_3(function):
    function.app.mount.obsSite.location = wgs84.latlon(longitude_degrees=1,
                                                       latitude_degrees=2,
                                                       elevation_m=3)
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                           'getText',
                           return_value=('48N 00 00', True)):
        with mock.patch.object(function,
                               'setLocationValues'):
            suc = function.setLatitude()
            assert suc


def test_setElevation_1(function):
    function.app.mount.obsSite.location = None
    suc = function.setElevation()
    assert not suc


def test_setElevation_2(function):
    function.app.mount.obsSite.location = wgs84.latlon(longitude_degrees=1,
                                                       latitude_degrees=2,
                                                       elevation_m=3)
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                           'getDouble',
                           return_value=(10.0, False)):
        suc = function.setElevation()
        assert not suc


def test_setElevation_3(function):
    function.app.mount.obsSite.location = wgs84.latlon(longitude_degrees=1,
                                                       latitude_degrees=2,
                                                       elevation_m=3)
    with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                           'getDouble',
                           return_value=(10.0, True)):
        with mock.patch.object(function,
                               'setLocationValues'):
            suc = function.setElevation()
            assert suc


def test_setUnattendedFlip_1(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=False):
        suc = function.setUnattendedFlip()
        assert not suc


def test_setUnattendedFlip_2(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.statusUnattendedFlip = True
        with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                               'getItem',
                               return_value=('ON', False)):
            suc = function.setUnattendedFlip()
            assert not suc


def test_setUnattendedFlip_3(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.statusUnattendedFlip = True
        with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                               'getItem',
                               return_value=('ON', True)):
            with mock.patch.object(function.app.mount.setting,
                                   'setUnattendedFlip',
                                   return_value=False):
                suc = function.setUnattendedFlip()
                assert not suc


def test_setUnattendedFlip_4(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.statusUnattendedFlip = True
        with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                               'getItem',
                               return_value=('ON', True)):
            with mock.patch.object(function.app.mount.setting,
                                   'setUnattendedFlip',
                                   return_value=True):
                suc = function.setUnattendedFlip()
                assert suc


def test_setDualAxisTracking_1(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=False):
        suc = function.setDualAxisTracking()
        assert not suc


def test_setDualAxisTracking_2(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.statusDualAxisTracking = True
        with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                               'getItem',
                               return_value=('ON', False)):
            suc = function.setDualAxisTracking()
            assert not suc


def test_setDualAxisTracking_3(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.statusDualAxisTracking = True
        with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                               'getItem',
                               return_value=('ON', True)):
            with mock.patch.object(function.app.mount.setting,
                                   'setDualAxisTracking',
                                   return_value=False):
                suc = function.setDualAxisTracking()
                assert not suc


def test_setDualAxisTracking_4(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.statusDualAxisTracking = True
        with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                               'getItem',
                               return_value=('ON', True)):
            with mock.patch.object(function.app.mount.setting,
                                   'setDualAxisTracking',
                                   return_value=True):
                suc = function.setDualAxisTracking()
                assert suc


def test_setRefractionTemp_1(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=False):
        suc = function.setRefractionTemp()
        assert not suc


def test_setRefractionTemp_2(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.slewRate = 10
        with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                               'getDouble',
                               return_value=(10, False)):
            suc = function.setRefractionTemp()
            assert not suc


def test_setRefractionTemp_3(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.slewRate = 10
        with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                               'getDouble',
                               return_value=(10, True)):
            with mock.patch.object(function.app.mount.setting,
                                   'setRefractionTemp',
                                   return_value=False):
                suc = function.setRefractionTemp()
                assert not suc


def test_setRefractionTemp_4(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.slewRate = 10
        with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                               'getDouble',
                               return_value=(10, True)):
            with mock.patch.object(function.app.mount.setting,
                                   'setRefractionTemp',
                                   return_value=True):
                suc = function.setRefractionTemp()
                assert suc


def test_setRefractionPress_1(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=False):
        suc = function.setRefractionPress()
        assert not suc


def test_setRefractionPress_2(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.slewRate = 10
        with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                               'getDouble',
                               return_value=(10, False)):
            suc = function.setRefractionPress()
            assert not suc


def test_setRefractionPress_3(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.slewRate = 10
        with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                               'getDouble',
                               return_value=(10, True)):
            with mock.patch.object(function.app.mount.setting,
                                   'setRefractionPress',
                                   return_value=False):
                suc = function.setRefractionPress()
                assert not suc


def test_setRefractionPress_4(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.slewRate = 10
        with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                               'getDouble',
                               return_value=(10, True)):
            with mock.patch.object(function.app.mount.setting,
                                   'setRefractionPress',
                                   return_value=True):
                suc = function.setRefractionPress()
                assert suc


def test_setRefraction_1(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=False):
        suc = function.setRefraction()
        assert not suc


def test_setRefraction_2(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.statusRefraction = True
        with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                               'getItem',
                               return_value=('ON', False)):
            suc = function.setRefraction()
            assert not suc


def test_setRefraction_3(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.statusRefraction = True
        with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                               'getItem',
                               return_value=('ON', True)):
            with mock.patch.object(function.app.mount.setting,
                                   'setRefraction',
                                   return_value=False):
                suc = function.setRefraction()
                assert not suc


def test_setRefraction_4(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.statusRefraction = True
        with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                               'getItem',
                               return_value=('ON', True)):
            with mock.patch.object(function.app.mount.setting,
                                   'setRefraction',
                                   return_value=True):
                suc = function.setRefraction()
                assert suc


def test_setWOL_1(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=False):
        suc = function.setWOL()
        assert not suc


def test_setWOL_2(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.statusWOL = '0'
        with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                               'getItem',
                               return_value=('ON', False)):
            suc = function.setWOL()
            assert not suc


def test_setWOL_3(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.statusWOL = '0'
        with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                               'getItem',
                               return_value=('ON', True)):
            with mock.patch.object(function.app.mount.setting,
                                   'setWOL',
                                   return_value=False):
                suc = function.setWOL()
                assert not suc


def test_setWOL_4(function, qtbot):
    with mock.patch.object(function,
                           'checkMount',
                           return_value=True):
        function.app.mount.setting.statusWOL = '0'
        with mock.patch.object(PySide6.QtWidgets.QInputDialog,
                               'getItem',
                               return_value=('ON', True)):
            with mock.patch.object(function.app.mount.setting,
                                   'setWOL',
                                   return_value=True):
                suc = function.setWOL()
                assert suc


def test_updatePointGui_ra_j2000(function):
    function.ui.coordsJ2000.setChecked(True)
    value = Angle(hours=45)
    function.app.mount.obsSite.raJNow = value
    value = Angle(degrees=45)
    function.app.mount.obsSite.decJNow = value
    function.updatePointGUI(function.app.mount.obsSite)


def test_showOffset_1(function):
    function.ui.clockSync.setChecked(False)
    suc = function.showOffset()
    assert suc


@mock.patch('tests.unit_tests.unitTestAddOns.baseTestApp.App.mount'
            '.obsSite.timeDiff', 0.003)
def test_showOffset_2(function):
    function.ui.clockSync.setChecked(True)
    suc = function.showOffset()
    assert suc


@mock.patch('tests.unit_tests.unitTestAddOns.baseTestApp.App.mount'
            '.obsSite.timeDiff', 0.3)
def test_showOffset_3(function):
    function.ui.clockSync.setChecked(True)
    suc = function.showOffset()
    assert suc


@mock.patch('tests.unit_tests.unitTestAddOns.baseTestApp.App.mount.obsSite'
            '.timeDiff', 0.6)
def test_showOffset_4(function):
    function.ui.clockSync.setChecked(True)
    suc = function.showOffset()
    assert suc


def test_openCommandProtocol_1(function):
    with mock.patch.object(webbrowser,
                           'open',
                           return_value=True):
        suc = function.openCommandProtocol()
        assert suc


def test_openCommandProtocol_2(function):
    with mock.patch.object(webbrowser,
                           'open',
                           return_value=False):
        suc = function.openCommandProtocol()
        assert suc


def test_openUpdateTimeDelta_1(function):
    with mock.patch.object(webbrowser,
                           'open',
                           return_value=True):
        suc = function.openUpdateTimeDelta()
        assert suc


def test_openUpdateTimeDelta_2(function):
    with mock.patch.object(webbrowser,
                           'open',
                           return_value=False):
        suc = function.openUpdateTimeDelta()
        assert suc


def test_openUpdateFirmware_1(function):
    with mock.patch.object(webbrowser,
                           'open',
                           return_value=True):
        suc = function.openUpdateFirmware()
        assert suc


def test_openUpdateFirmware_2(function):
    with mock.patch.object(webbrowser,
                           'open',
                           return_value=False):
        suc = function.openUpdateFirmware()
        assert suc


def test_openMountDocumentation_1(function):
    function.app.mount.firmware.product = 'tester'
    with mock.patch.object(webbrowser,
                           'open',
                           return_value=True):
        suc = function.openMountDocumentation()
        assert not suc


def test_openMountDocumentation_2(function):
    function.app.mount.firmware.product = '10micron GM1000HPS'
    with mock.patch.object(webbrowser,
                           'open',
                           return_value=False):
        suc = function.openMountDocumentation()
        assert suc


def test_openMountDocumentation_3(function):
    function.app.mount.firmware.product = '10micron GM1000HPS'
    with mock.patch.object(webbrowser,
                           'open',
                           return_value=True):
        suc = function.openMountDocumentation()
        assert suc


def test_moveDuration_1(function):
    function.ui.moveDuration.setCurrentIndex(1)
    with mock.patch.object(gui.mainWmixin.tabMount,
                           'sleepAndEvents'):
        with mock.patch.object(function,
                               'stopMoveAll'):
            suc = function.moveDuration()
            assert suc


def test_moveDuration_2(function):
    function.ui.moveDuration.setCurrentIndex(2)
    with mock.patch.object(gui.mainWmixin.tabMount,
                           'sleepAndEvents'):
        with mock.patch.object(function,
                               'stopMoveAll'):
            suc = function.moveDuration()
            assert suc


def test_moveDuration_3(function):
    function.ui.moveDuration.setCurrentIndex(3)
    with mock.patch.object(gui.mainWmixin.tabMount,
                           'sleepAndEvents'):
        with mock.patch.object(function,
                               'stopMoveAll'):
            suc = function.moveDuration()
            assert suc


def test_moveDuration_4(function):
    function.ui.moveDuration.setCurrentIndex(4)
    with mock.patch.object(gui.mainWmixin.tabMount,
                           'sleepAndEvents'):
        with mock.patch.object(function,
                               'stopMoveAll'):
            suc = function.moveDuration()
            assert suc


def test_moveDuration_5(function):
    function.ui.moveDuration.setCurrentIndex(0)
    with mock.patch.object(gui.mainWmixin.tabMount,
                           'sleepAndEvents'):
        suc = function.moveDuration()
        assert not suc


def test_moveClassicGameController_1(function):
    with mock.patch.object(function,
                           'stopMoveAll'):
        suc = function.moveClassicGameController(128, 128)
        assert suc


def test_moveClassicGameController_2(function):
    with mock.patch.object(function,
                           'moveClassic'):
        suc = function.moveClassicGameController(0, 0)
        assert suc


def test_moveClassicGameController_3(function):
    with mock.patch.object(function,
                           'moveClassic'):
        suc = function.moveClassicGameController(255, 255)
        assert suc


def test_moveClassicUI_1(function):
    def Sender():
        return function.ui.moveNorthEast

    function.deviceStat['mount'] = False
    function.sender = Sender
    suc = function.moveClassicUI()
    assert not suc


def test_moveClassicUI_2(function):
    def Sender():
        return function.ui.moveNorthEast

    function.deviceStat['mount'] = True
    function.sender = Sender
    suc = function.moveClassicUI()
    assert suc


def test_moveClassic_1(function):
    with mock.patch.object(function,
                           'moveDuration'):
        suc = function.moveClassic([1, 1])
        assert suc


def test_moveClassic_2(function):
    with mock.patch.object(function,
                           'moveDuration'):
        suc = function.moveClassic([-1, -1])
        assert suc


def test_moveClassic_3(function):
    with mock.patch.object(function,
                           'moveDuration'):
        suc = function.moveClassic([0, 0])
        assert suc


def test_stopMoveAll(function):
    with mock.patch.object(function.app.mount.obsSite,
                           'stopMoveAll',
                           return_value=True):
        suc = function.stopMoveAll()
        assert suc


def test_setSlewSpeed_1(function):
    def Sender():
        return function.ui.renameStart

    function.sender = Sender

    suc = function.setSlewSpeed()
    assert not suc


def test_setSlewSpeed_2(function):
    def Sender():
        return function.ui.slewSpeedMax

    def test():
        return

    function.slewSpeeds = {function.ui.slewSpeedMax: test}
    function.sender = Sender

    suc = function.setSlewSpeed()
    assert suc


def test_moveAltAzDefault(function):
    suc = function.moveAltAzDefault()
    assert suc


def test_moveAltAzUI_1(function):
    def Sender():
        return function.ui.moveNorthEastAltAz

    function.sender = Sender
    function.deviceStat['mount'] = False
    with mock.patch.object(function,
                           'moveAltAz'):
        suc = function.moveAltAzUI()
        assert not suc


def test_moveAltAzUI_2(function):
    def Sender():
        return function.ui.moveNorthEastAltAz

    function.sender = Sender
    function.deviceStat['mount'] = True
    with mock.patch.object(function,
                           'moveAltAz'):
        suc = function.moveAltAzUI()
        assert not suc


def test_moveAltAzGameController_1(function):
    with mock.patch.object(function,
                           'moveAltAz'):
        suc = function.moveAltAzGameController(0)
        assert suc


def test_moveAltAzGameController_2(function):
    with mock.patch.object(function,
                           'moveAltAz'):
        suc = function.moveAltAzGameController(2)
        assert suc


def test_moveAltAzGameController_3(function):
    with mock.patch.object(function,
                           'moveAltAz'):
        suc = function.moveAltAzGameController(4)
        assert suc


def test_moveAltAzGameController_4(function):
    with mock.patch.object(function,
                           'moveAltAz'):
        suc = function.moveAltAzGameController(6)
        assert suc


def test_moveAltAzGameController_5(function):
    with mock.patch.object(function,
                           'moveAltAz'):
        suc = function.moveAltAzGameController(99)
        assert not suc


def test_moveAltAz_1(function):
    function.targetAlt = None
    function.targetAz = None
    function.app.mount.obsSite.Alt = None
    function.app.mount.obsSite.Az = Angle(degrees=10)

    with mock.patch.object(function,
                           'slewTargetAltAz',
                           return_value=False):
        suc = function.moveAltAz([1, 1])
        assert not suc


def test_moveAltAz_2(function):
    function.targetAlt = None
    function.targetAz = None
    function.app.mount.obsSite.Alt = Angle(degrees=10)
    function.app.mount.obsSite.Az = Angle(degrees=10)

    with mock.patch.object(function,
                           'slewTargetAltAz',
                           return_value=False):
        suc = function.moveAltAz([1, 1])
        assert not suc


def test_moveAltAz_3(function):
    function.targetAlt = 10
    function.targetAz = 10
    function.app.mount.obsSite.Alt = Angle(degrees=10)
    function.app.mount.obsSite.Az = Angle(degrees=10)

    with mock.patch.object(function,
                           'slewTargetAltAz',
                           return_value=True):
        suc = function.moveAltAz([1, 1])
        assert suc


def test_setRA_1(function):
    with mock.patch.object(QInputDialog,
                           'getText',
                           return_value=('', False)):
        suc = function.setRA()
        assert not suc


def test_setRA_2(function):
    with mock.patch.object(QInputDialog,
                           'getText',
                           return_value=('', True)):
        suc = function.setRA()
        assert not suc


def test_setRA_3(function):
    with mock.patch.object(QInputDialog,
                           'getText',
                           return_value=('12H', True)):
        suc = function.setRA()
        assert suc


def test_setDEC_1(function):
    with mock.patch.object(QInputDialog,
                           'getText',
                           return_value=('', False)):
        suc = function.setDEC()
        assert not suc


def test_setDEC_2(function):
    with mock.patch.object(QInputDialog,
                           'getText',
                           return_value=('', True)):
        suc = function.setDEC()
        assert not suc


def test_setDEC_3(function):
    with mock.patch.object(QInputDialog,
                           'getText',
                           return_value=('12', True)):
        suc = function.setDEC()
        assert suc


def test_moveAltAzAbsolute_1(function):
    function.ui.moveCoordinateAlt.setText('50h')
    function.ui.moveCoordinateAz.setText('50h')
    suc = function.moveAltAzAbsolute()
    assert not suc


def test_moveAltAzAbsolute_2(function):
    function.ui.moveCoordinateAlt.setText('50')
    function.ui.moveCoordinateAz.setText('50h')
    suc = function.moveAltAzAbsolute()
    assert not suc


def test_moveAltAzAbsolute_3(function):
    function.app.mount.setting.horizonLimitLow = 10
    function.app.mount.setting.horizonLimitHigh = 70
    function.ui.moveCoordinateAlt.setText('50')
    function.ui.moveCoordinateAz.setText('50')
    with mock.patch.object(function,
                           'slewTargetAltAz',
                           return_value=False):
        suc = function.moveAltAzAbsolute()
        assert not suc


def test_moveAltAzAbsolute_4(function):
    function.app.mount.setting.horizonLimitLow = 10
    function.app.mount.setting.horizonLimitHigh = 70
    function.ui.moveCoordinateAlt.setText('50')
    function.ui.moveCoordinateAz.setText('50')
    with mock.patch.object(function,
                           'slewTargetAltAz',
                           return_value=True):
        suc = function.moveAltAzAbsolute()
        assert suc


def test_moveRaDecAbsolute_1(function):
    function.ui.moveCoordinateRa.setText('asd')
    function.ui.moveCoordinateDec.setText('asd')
    suc = function.moveRaDecAbsolute()
    assert not suc


def test_moveRaDecAbsolute_2(function):
    function.ui.moveCoordinateRa.setText('12H')
    function.ui.moveCoordinateDec.setText('asd')
    suc = function.moveRaDecAbsolute()
    assert not suc


def test_moveRaDecAbsolute_3(function):
    function.ui.moveCoordinateRa.setText('12H')
    function.ui.moveCoordinateDec.setText('30 30')
    a = function.app.mount.obsSite.timeJD
    function.app.mount.obsSite.timeJD = None
    suc = function.moveRaDecAbsolute()
    assert not suc
    function.app.mount.obsSite.timeJD = a


def test_moveRaDecAbsolute_4(function):
    function.ui.moveCoordinateRa.setText('12H')
    function.ui.moveCoordinateDec.setText('30 30')
    with mock.patch.object(function.app.mount.obsSite,
                           'setTargetRaDec'):
        with mock.patch.object(function,
                               'slewSelectedTargetWithDome',
                               return_value=False):
            suc = function.moveRaDecAbsolute()
            assert not suc


def test_moveRaDecAbsolute_5(function):
    function.ui.moveCoordinateRa.setText('12H')
    function.ui.moveCoordinateDec.setText('30 30')
    with mock.patch.object(function.app.mount.obsSite,
                           'setTargetRaDec'):
        with mock.patch.object(function,
                               'slewSelectedTargetWithDome',
                               return_value=True):
            suc = function.moveRaDecAbsolute()
            assert suc


def test_moveRaDecAbsolute_6(function):
    function.ui.moveCoordinateRa.setText('12H')
    function.ui.moveCoordinateDec.setText('30 30')
    with mock.patch.object(function.app.mount.obsSite,
                           'timeJD',
                           return_value=None):
        with mock.patch.object(function.app.mount.obsSite,
                               'setTargetRaDec'):
            with mock.patch.object(function,
                                   'slewSelectedTargetWithDome',
                                   return_value=False):
                suc = function.moveRaDecAbsolute()
                assert not suc


def test_commandRaw_1(function):
    with mock.patch.object(mountcontrol.connection.Connection,
                           'communicateRaw',
                           return_value=(True, False, '')):
        suc = function.commandRaw()
        assert suc


def test_commandRaw_2(function):
    with mock.patch.object(mountcontrol.connection.Connection,
                           'communicateRaw',
                           return_value=(True, True, '')):
        suc = function.commandRaw()
        assert suc
