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
import pytest
import astropy
from unittest import mock

# external packages
import numpy as np
from PySide6.QtWidgets import QWidget

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.mainWaddon.tabEnvironWeather import EnvironWeather
from gui.widgets.main_ui import Ui_MainWindow
from base.loggerMW import setupLogging
setupLogging()


@pytest.fixture(autouse=True, scope='module')
def function(qapp):

    mainW = QWidget()
    mainW.app = App()
    mainW.ui = Ui_MainWindow()
    mainW.ui.setupUi(mainW)
    window = EnvironWeather(mainW)
    yield window
    mainW.app.threadPool.waitForDone(1000)


def test_initConfig_1(function):
    function.initConfig()


def test_storeConfig_1(function):
    function.storeConfig()


def test_smartEnvironGui_1(function):
    function.app.deviceStat['sensor1Weather'] = False
    function.app.deviceStat['sensor2Weather'] = False
    function.app.deviceStat['sensor3Weather'] = False
    function.app.deviceStat['onlineWeather'] = False
    function.app.deviceStat['directWeather'] = False
    function.smartEnvironGui()
    assert not function.ui.sensor1Group.isEnabled()
    assert not function.ui.sensor2Group.isEnabled()
    assert not function.ui.sensor3Group.isEnabled()
    assert not function.ui.onlineGroup.isEnabled()
    assert not function.ui.directGroup.isEnabled()


def test_smartEnvironGui_2(function):
    function.app.deviceStat['sensor1Weather'] = True
    function.app.deviceStat['sensor2Weather'] = True
    function.app.deviceStat['sensor3Weather'] = True
    function.app.deviceStat['onlineWeather'] = True
    function.app.deviceStat['directWeather'] = True
    function.smartEnvironGui()
    assert function.ui.sensor1Group.isEnabled()
    assert function.ui.sensor2Group.isEnabled()
    assert function.ui.sensor3Group.isEnabled()
    assert function.ui.onlineGroup.isEnabled()
    assert function.ui.directGroup.isEnabled()


def test_smartEnvironGui_3(function):
    function.app.deviceStat['sensor1Weather'] = None
    function.app.deviceStat['sensor2Weather'] = None
    function.app.deviceStat['sensor3Weather'] = None
    function.app.deviceStat['onlineWeather'] = None
    function.app.deviceStat['directWeather'] = False
    function.smartEnvironGui()
    assert not function.ui.sensor1Group.isEnabled()
    assert not function.ui.sensor2Group.isEnabled()
    assert not function.ui.sensor3Group.isEnabled()
    assert not function.ui.onlineGroup.isEnabled()
    assert not function.ui.directGroup.isEnabled()


def test_updateRefractionUpdateType_1(function):
    function.app.mount.setting.weatherStatus = 3
    function.refractionSource = 'onlineWeather'
    suc = function.updateRefractionUpdateType()
    assert not suc


def test_updateRefractionUpdateType_2(function):
    function.app.mount.setting.weatherStatus = 3
    function.refractionSource = 'directWeather'
    suc = function.updateRefractionUpdateType()
    assert not suc


def test_updateRefractionUpdateType_3(function):
    function.app.mount.setting.weatherStatus = 0
    function.refractionSource = 'directWeather'
    function.ui.refracManual.setChecked(False)
    suc = function.updateRefractionUpdateType()
    assert suc
    assert function.ui.refracManual.isChecked()


def test_updateRefractionUpdateType_4(function):
    function.app.mount.setting.weatherStatus = 1
    function.refractionSource = 'directWeather'
    function.ui.refracNoTrack.setChecked(False)
    suc = function.updateRefractionUpdateType()
    assert suc


def test_updateRefractionUpdateType_5(function):
    function.app.mount.setting.weatherStatus = 2
    function.refractionSource = 'directWeather'
    function.ui.refracCont.setChecked(False)
    suc = function.updateRefractionUpdateType()
    assert suc


def test_setRefractionUpdateType_0(function):
    function.ui.showTabEnviron.setChecked(False)
    suc = function.setRefractionUpdateType()
    assert not suc


def test_setRefractionUpdateType_1(function):
    function.ui.showTabEnviron.setChecked(True)
    function.refractionSource = 'onlineWeather'
    with mock.patch.object(function.app.mount.setting,
                           'setDirectWeatherUpdateType',
                           return_value=True):
        suc = function.setRefractionUpdateType()
        assert suc


def test_setRefractionUpdateType_2(function):
    function.ui.showTabEnviron.setChecked(True)
    function.app.mount.setting.weatherStatus = 1
    function.refractionSource = 'directWeather'
    function.ui.refracManual.setChecked(True)
    with mock.patch.object(function.app.mount.setting,
                           'setDirectWeatherUpdateType',
                           return_value=True):
        suc = function.setRefractionUpdateType()
        assert suc


def test_setRefractionUpdateType_3(function):
    function.ui.showTabEnviron.setChecked(True)
    function.refractionSource = 'directWeather'
    function.app.mount.setting.weatherStatus = 1
    function.ui.refracNoTrack.setChecked(True)
    with mock.patch.object(function.app.mount.setting,
                           'setDirectWeatherUpdateType',
                           return_value=True):
        suc = function.setRefractionUpdateType()
        assert suc


def test_setRefractionUpdateType_4(function):
    function.ui.showTabEnviron.setChecked(True)
    function.refractionSource = 'directWeather'
    function.app.mount.setting.weatherStatus = 0
    function.ui.refracCont.setChecked(True)
    with mock.patch.object(function.app.mount.setting,
                           'setDirectWeatherUpdateType',
                           return_value=True):
        suc = function.setRefractionUpdateType()
        assert suc


def test_setRefractionSourceGui_1(function):
    function.setRefractionSourceGui()


def test_setRefractionSourceGui_2(function):
    function.refractionSource = 'onlineWeather'
    function.setRefractionSourceGui()


def test_selectRefractionSource_1(function):
    function.ui.onlineGroup.setChecked(False)
    function.refractionSource = 'onlineWeather'
    with mock.patch.object(function,
                           'setRefractionSourceGui'):
        with mock.patch.object(function,
                               'setRefractionUpdateType'):
            function.selectRefractionSource('onlineWeather')


def test_selectRefractionSource_2(function):
    function.ui.onlineGroup.setChecked(True)
    function.refractionSource = 'directWeather'
    with mock.patch.object(function,
                           'setRefractionSourceGui'):
        with mock.patch.object(function,
                               'setRefractionUpdateType'):
            function.selectRefractionSource('onlineWeather')


def test_updateFilterRefractionParameters_1(function):
    function.refractionSource = 'onlineWeather'
    function.app.onlineWeather.data.clear()
    suc = function.updateFilterRefractionParameters()
    assert not suc


def test_updateFilterRefractionParameters_2(function):
    function.refractionSource = 'weather'
    function.app.onlineWeather.data['WEATHER_PARAMETERS.WEATHER_TEMPERATURE'] = 10
    function.app.onlineWeather.data['WEATHER_PARAMETERS.WEATHER_PRESSURE'] = 1000
    suc = function.updateFilterRefractionParameters()
    assert not suc


def test_updateFilterRefractionParameters_3(function):
    function.refractionSource = 'onlineWeather'
    function.app.onlineWeather.data['WEATHER_PARAMETERS.WEATHER_TEMPERATURE'] = 10
    function.app.onlineWeather.data['WEATHER_PARAMETERS.WEATHER_PRESSURE'] = 1000
    suc = function.updateFilterRefractionParameters()
    assert suc


def test_updateFilterRefractionParameters_4(function):
    function.refractionSource = 'sensor1Weather'
    function.app.onlineWeather.data.clear()
    suc = function.updateFilterRefractionParameters()
    assert not suc


def test_updateFilterRefractionParameters_5(function):
    function.refractionSource = 'sensor1Weather'
    function.app.sensor1Weather.data['WEATHER_PARAMETERS.WEATHER_TEMPERATURE'] = 10
    function.app.sensor1Weather.data['WEATHER_PARAMETERS.WEATHER_PRESSURE'] = 1000
    suc = function.updateFilterRefractionParameters()
    assert suc


def test_updateFilterRefractionParameters_6(function):
    function.refractionSource = 'sensor1Weather'
    function.filteredTemperature = None
    function.app.sensor1Weather.data['WEATHER_PARAMETERS.WEATHER_TEMPERATURE'] = 10
    function.app.sensor1Weather.data['WEATHER_PARAMETERS.WEATHER_PRESSURE'] = 1000
    suc = function.updateFilterRefractionParameters()
    assert suc


def test_updateFilterRefractionParameters_7(function):
    function.refractionSource = 'sensor1Weather'
    function.filteredPressure = None
    function.app.sensor1Weather.data['WEATHER_PARAMETERS.WEATHER_TEMPERATURE'] = 10
    function.app.sensor1Weather.data['WEATHER_PARAMETERS.WEATHER_PRESSURE'] = 1000
    suc = function.updateFilterRefractionParameters()
    assert suc


def test_updateFilterRefractionParameters_8(function):
    function.refractionSource = 'sensor1Weather'
    function.filteredTemperature = np.full(100, 10)
    function.app.sensor1Weather.data['WEATHER_PARAMETERS.WEATHER_TEMPERATURE'] = 10
    function.app.sensor1Weather.data['WEATHER_PARAMETERS.WEATHER_PRESSURE'] = 1000
    suc = function.updateFilterRefractionParameters()
    assert suc


def test_updateFilterRefractionParameters_9(function):
    function.refractionSource = 'sensor1Weather'
    function.filteredPressure = np.full(100, 1000)
    function.app.sensor1Weather.data['WEATHER_PARAMETERS.WEATHER_TEMPERATURE'] = 10
    function.app.sensor1Weather.data['WEATHER_PARAMETERS.WEATHER_PRESSURE'] = 1000
    suc = function.updateFilterRefractionParameters()
    assert suc


def test_movingAverageRefractionParameters_1(function):
    function.app.sensor1Weather.data.clear()
    function.filteredPressure = None
    function.filteredTemperature = None
    v1, v2 = function.movingAverageRefractionParameters()
    assert v1 is None
    assert v2 is None


def test_movingAverageRefractionParameters_2(function):
    function.filteredTemperature = np.full(100, 10)
    function.filteredPressure = np.full(100, 1000)
    v1, v2 = function.movingAverageRefractionParameters()
    assert v1 == 10.0
    assert v2 == 1000.0


def test_updateRefractionParameters_1(function):
    function.refractionSource = 'directWeather'

    suc = function.updateRefractionParameters()
    assert not suc


def test_updateRefractionParameters_2(function):
    function.refractionSource = 'onlineWeather'
    function.app.deviceStat['mount'] = False

    suc = function.updateRefractionParameters()
    assert not suc


def test_updateRefractionParameters_3(function):
    function.refractionSource = 'onlineWeather'
    function.app.deviceStat['mount'] = True
    with mock.patch.object(function,
                           'movingAverageRefractionParameters',
                           return_value=(None, None)):
        suc = function.updateRefractionParameters()
        assert not suc


def test_updateRefractionParameters_4(function):
    function.refractionSource = 'onlineWeather'
    function.app.deviceStat['mount'] = True
    function.ui.refracManual.setChecked(True)
    with mock.patch.object(function,
                           'movingAverageRefractionParameters',
                           return_value=(10, 10)):
        suc = function.updateRefractionParameters()
        assert not suc


def test_updateRefractionParameters_5(function):
    function.refractionSource = 'onlineWeather'
    function.app.deviceStat['mount'] = True
    function.ui.refracManual.setChecked(False)
    function.ui.refracNoTrack.setChecked(True)
    function.app.mount.obsSite.status = 0
    with mock.patch.object(function,
                           'movingAverageRefractionParameters',
                           return_value=(10, 10)):
        suc = function.updateRefractionParameters()
        assert not suc


def test_updateRefractionParameters_6(function):
    function.refractionSource = 'onlineWeather'
    function.app.deviceStat['mount'] = True
    function.ui.refracNoTrack.setChecked(True)
    function.app.mount.obsSite.status = 1

    with mock.patch.object(function,
                           'movingAverageRefractionParameters',
                           return_value=(10, 10)):
        with mock.patch.object(function.app.mount.setting,
                               'setRefractionParam',
                               return_value=False):
            suc = function.updateRefractionParameters()
            assert not suc


def test_updateRefractionParameters_7(function, qtbot):
    function.refractionSource = 'onlineWeather'
    function.app.deviceStat['mount'] = True
    function.ui.refracNoTrack.setChecked(True)
    function.app.mount.obsSite.status = 1

    with mock.patch.object(function,
                           'movingAverageRefractionParameters',
                           return_value=(10, 10)):
        with mock.patch.object(function.app.mount.setting,
                               'setRefractionParam',
                               return_value=True):
            suc = function.updateRefractionParameters()
            assert suc


def test_updateSourceGui_1(function):
    function.app.sensor1Weather.data['WEATHER_PARAMETERS.WEATHER_TEMPERATURE'] = 10.5
    function.app.sensor1Weather.data['WEATHER_PARAMETERS.WEATHER_PRESSURE'] = 1000
    function.app.sensor1Weather.data['WEATHER_PARAMETERS.WEATHER_DEWPOINT'] = 10.5
    function.app.sensor1Weather.data['WEATHER_PARAMETERS.WEATHER_HUMIDITY'] = 10
    function.updateSourceGui()
    assert function.ui.temperature1.text() == '10.5'
    assert function.ui.pressure1.text() == '1000'
    assert function.ui.dewPoint1.text() == '10.5'
    assert function.ui.humidity1.text() == ' 10'


def test_clearSourceGui_1(function):
    function.clearSourceGui('test')
    assert function.ui.temperature1.text() == '-'
    assert function.ui.pressure1.text() == '-'
    assert function.ui.dewPoint1.text() == '-'
    assert function.ui.humidity1.text() == '-'
