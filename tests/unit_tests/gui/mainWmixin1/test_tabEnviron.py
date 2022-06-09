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
# written in python3, (c) 2019-2022 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
from unittest import mock
import shutil

# external packages
import numpy as np

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from gui.mainWmixin.tabEnviron import Environ
from gui.widgets.main_ui import Ui_MainWindow
from gui.utilities.toolsQtWidget import MWidget
from base.loggerMW import setupLogging
setupLogging()


@pytest.fixture(autouse=True, scope='function')
def function(qapp):
    shutil.copy('tests/testData/meteoblue.data',
                'tests/workDir/data/meteoblue.data')
    shutil.copy('tests/testData/openweathermap.data',
                'tests/workDir/data/openweathermap.data')

    class Mixin(MWidget, Environ):
        def __init__(self):
            super().__init__()
            self.app = App()
            self.deviceStat = {}
            self.threadPool = self.app.threadPool
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)
            Environ.__init__(self)

    window = Mixin()
    yield window


def test_initConfig_1(function):
    suc = function.initConfig()
    assert suc


def test_storeConfig_1(function):
    suc = function.storeConfig()
    assert suc


def test_updateRefractionUpdateType_1(function):
    class Test:
        weatherStatus = 3
    function.refractionSource = 'onlineWeather'
    suc = function.updateRefractionUpdateType(setting=Test())
    assert not suc


def test_updateRefractionUpdateType_2(function):
    class Test:
        weatherStatus = 3
    function.refractionSource = 'directWeather'
    suc = function.updateRefractionUpdateType(setting=Test())
    assert not suc


def test_updateRefractionUpdateType_3(function):
    class Test:
        weatherStatus = 0
    function.refractionSource = 'directWeather'
    function.ui.checkRefracNone.setChecked(False)
    suc = function.updateRefractionUpdateType(setting=Test())
    assert suc
    assert function.ui.checkRefracNone.isChecked()


def test_updateRefractionUpdateType_4(function):
    class Test:
        weatherStatus = 1
    function.refractionSource = 'directWeather'
    function.ui.checkRefracNoTrack.setChecked(False)
    suc = function.updateRefractionUpdateType(setting=Test())
    assert suc


def test_updateRefractionUpdateType_5(function):
    class Test:
        weatherStatus = 2
    function.refractionSource = 'directWeather'
    function.ui.checkRefracCont.setChecked(False)
    suc = function.updateRefractionUpdateType(setting=Test())
    assert suc


def test_setRefractionUpdateType_1(function):
    function.refractionSource = 'onlineWeather'
    with mock.patch.object(function.app.mount.setting,
                           'setDirectWeatherUpdateType',
                           return_value=True):
        suc = function.setRefractionUpdateType()
        assert suc


def test_setRefractionUpdateType_2(function):
    function.refractionSource = 'directWeather'
    function.ui.checkRefracNone.setChecked(True)
    with mock.patch.object(function.app.mount.setting,
                           'setDirectWeatherUpdateType',
                           return_value=True):
        suc = function.setRefractionUpdateType()
        assert suc


def test_setRefractionUpdateType_3(function):
    function.refractionSource = 'directWeather'
    function.ui.checkRefracNoTrack.setChecked(True)
    with mock.patch.object(function.app.mount.setting,
                           'setDirectWeatherUpdateType',
                           return_value=True):
        suc = function.setRefractionUpdateType()
        assert suc


def test_setRefractionUpdateType_4(function):
    function.refractionSource = 'directWeather'
    function.ui.checkRefracCont.setChecked(True)
    with mock.patch.object(function.app.mount.setting,
                           'setDirectWeatherUpdateType',
                           return_value=True):
        suc = function.setRefractionUpdateType()
        assert suc


def test_setRefractionSourceGui_1(function):
    suc = function.setRefractionSourceGui()
    assert suc


def test_setRefractionSourceGui_2(function):
    function.refractionSource = 'onlineWeather'
    suc = function.setRefractionSourceGui()
    assert suc


def test_selectRefractionSource_1(function):
    def Sender():
        return function.ui.powerPort1

    function.sender = Sender
    suc = function.selectRefractionSource()
    assert suc


def test_selectRefractionSource_2(function):
    def Sender():
        return function.ui.onlineWeatherGroup

    function.ui.onlineWeatherGroup.setChecked(False)
    function.refractionSource = 'onlineWeather'
    function.sender = Sender
    suc = function.selectRefractionSource()
    assert suc


def test_selectRefractionSource_3(function):
    def Sender():
        return function.ui.onlineWeatherGroup

    function.refractionSource = 'directWeather'
    function.ui.onlineWeatherGroup.setChecked(True)
    function.sender = Sender
    suc = function.selectRefractionSource()
    assert suc


def test_updateFilterRefractionParameters_1(function):
    function.refractionSource = 'onlineWeather'
    function.app.onlineWeather.data = {}
    suc = function.updateFilterRefractionParameters()
    assert not suc


def test_updateFilterRefractionParameters_2(function):
    function.refractionSource = 'weather'
    function.app.onlineWeather.data = {'temperature': 10,
                                       'pressure': 1000}
    suc = function.updateFilterRefractionParameters()
    assert not suc


def test_updateFilterRefractionParameters_3(function):
    function.refractionSource = 'onlineWeather'
    function.app.onlineWeather.data = {'temperature': 10,
                                       'pressure': 1000}
    suc = function.updateFilterRefractionParameters()
    assert suc


def test_updateFilterRefractionParameters_4(function):
    function.refractionSource = 'sensorWeather'
    suc = function.updateFilterRefractionParameters()
    assert not suc


def test_updateFilterRefractionParameters_5(function):
    function.refractionSource = 'sensorWeather'
    function.app.sensorWeather.data = {'WEATHER_PARAMETERS.WEATHER_TEMPERATURE': 10,
                                       'WEATHER_PARAMETERS.WEATHER_PRESSURE': 1000}
    suc = function.updateFilterRefractionParameters()
    assert suc


def test_updateFilterRefractionParameters_6(function):
    function.refractionSource = 'sensorWeather'
    function.filteredTemperature = None
    function.app.sensorWeather.data = {'WEATHER_PARAMETERS.WEATHER_TEMPERATURE': 10,
                                       'WEATHER_PARAMETERS.WEATHER_PRESSURE': 1000}
    suc = function.updateFilterRefractionParameters()
    assert suc


def test_updateFilterRefractionParameters_7(function):
    function.refractionSource = 'sensorWeather'
    function.filteredPressure = None
    function.app.sensorWeather.data = {'WEATHER_PARAMETERS.WEATHER_TEMPERATURE': 10,
                                       'WEATHER_PARAMETERS.WEATHER_PRESSURE': 1000}
    suc = function.updateFilterRefractionParameters()
    assert suc


def test_updateFilterRefractionParameters_8(function):
    function.refractionSource = 'sensorWeather'
    function.filteredTemperature = np.full(100, 10)
    function.app.sensorWeather.data = {'WEATHER_PARAMETERS.WEATHER_TEMPERATURE': 10,
                                       'WEATHER_PARAMETERS.WEATHER_PRESSURE': 1000}
    suc = function.updateFilterRefractionParameters()
    assert suc


def test_updateFilterRefractionParameters_9(function):
    function.refractionSource = 'sensorWeather'
    function.filteredPressure = np.full(100, 1000)
    function.app.sensorWeather.data = {'WEATHER_PARAMETERS.WEATHER_TEMPERATURE': 10,
                                       'WEATHER_PARAMETERS.WEATHER_PRESSURE': 1000}
    suc = function.updateFilterRefractionParameters()
    assert suc


def test_movingAverageRefractionParameters_1(function):
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
    function.deviceStat['mount'] = False

    suc = function.updateRefractionParameters()
    assert not suc


def test_updateRefractionParameters_3(function):
    function.refractionSource = 'onlineWeather'
    function.deviceStat['mount'] = True
    with mock.patch.object(function,
                           'movingAverageRefractionParameters',
                           return_value=(None, None)):
        suc = function.updateRefractionParameters()
        assert not suc


def test_updateRefractionParameters_4(function):
    def Sender():
        return function.ui.isOnline

    function.sender = Sender
    function.refractionSource = 'onlineWeather'
    function.deviceStat['mount'] = True
    function.ui.checkRefracNone.setChecked(True)
    with mock.patch.object(function,
                           'movingAverageRefractionParameters',
                           return_value=(10, 10)):
        suc = function.updateRefractionParameters()
        assert not suc


def test_updateRefractionParameters_5(function):
    def Sender():
        return function.ui.isOnline

    function.sender = Sender
    function.refractionSource = 'onlineWeather'
    function.deviceStat['mount'] = True
    function.ui.checkRefracNone.setChecked(False)
    function.ui.checkRefracNoTrack.setChecked(True)
    function.app.mount.obsSite.status = 0
    with mock.patch.object(function,
                           'movingAverageRefractionParameters',
                           return_value=(10, 10)):
        suc = function.updateRefractionParameters()
        assert not suc


def test_updateRefractionParameters_6(function):
    def Sender():
        return function.ui.setRefractionManual

    function.sender = Sender
    function.refractionSource = 'onlineWeather'
    function.deviceStat['mount'] = True
    function.ui.checkRefracNoTrack.setChecked(True)

    with mock.patch.object(function,
                           'movingAverageRefractionParameters',
                           return_value=(10, 10)):
        with mock.patch.object(function.app.mount.setting,
                               'setRefractionParam',
                               return_value=False):
            suc = function.updateRefractionParameters()
            assert not suc


def test_updateRefractionParameters_7(function, qtbot):
    def Sender():
        return function.ui.setRefractionManual

    function.sender = Sender
    function.refractionSource = 'onlineWeather'
    function.deviceStat['mount'] = True

    with mock.patch.object(function,
                           'movingAverageRefractionParameters',
                           return_value=(10, 10)):
        with mock.patch.object(function.app.mount.setting,
                               'setRefractionParam',
                               return_value=True):
            suc = function.updateRefractionParameters()
            assert suc


def test_clearEnvironGui_1(function):
    function.clearSensorWeatherGui('test')
    assert function.ui.sensorWeatherTemp.text() == '-'
    assert function.ui.sensorWeatherPress.text() == '-'
    assert function.ui.sensorWeatherDewPoint.text() == '-'
    assert function.ui.sensorWeatherHumidity.text() == '-'


def test_updateEnvironGui_1(function):
    function.app.sensorWeather.name = 'test'
    function.app.sensorWeather.data['WEATHER_PARAMETERS.WEATHER_TEMPERATURE'] = 10.5
    function.updateSensorWeatherGui()
    assert function.ui.sensorWeatherTemp.text() == '10.5'


def test_updateEnvironGui_2(function):
    function.app.sensorWeather.name = 'test'
    function.app.sensorWeather.data['WEATHER_PARAMETERS.WEATHER_PRESSURE'] = 10.5
    function.updateSensorWeatherGui()
    assert function.ui.sensorWeatherPress.text() == '10.5'


def test_updateEnvironGui_3(function):
    function.app.sensorWeather.name = 'test'
    function.app.sensorWeather.data['WEATHER_PARAMETERS.WEATHER_DEWPOINT'] = 10.5
    function.updateSensorWeatherGui()
    assert function.ui.sensorWeatherDewPoint.text() == '10.5'


def test_updateEnvironGui_4(function):
    function.app.sensorWeather.name = 'test'
    function.app.sensorWeather.data['WEATHER_PARAMETERS.WEATHER_HUMIDITY'] = 10
    function.updateSensorWeatherGui()
    assert function.ui.sensorWeatherHumidity.text() == ' 10'


def test_clearSkymeterGui_1(function):
    function.clearSkymeterGui()
    assert function.ui.skymeterSQR.text() == '-'
    assert function.ui.skymeterTemp.text() == '-'


def test_updateSkymeterGui_1(function):
    function.app.skymeter.name = 'test'
    function.app.skymeter.data['SKY_QUALITY.SKY_BRIGHTNESS'] = 10.5
    function.updateSkymeterGui()
    assert function.ui.skymeterSQR.text() == '10.50'


def test_updateSkymeterGui_2(function):
    function.app.skymeter.name = 'test'
    function.app.skymeter.data['SKY_QUALITY.SKY_TEMPERATURE'] = 10.5
    function.updateSkymeterGui()
    assert function.ui.skymeterTemp.text() == '10.5'


def test_clearPowerWeatherGui_1(function):
    function.clearPowerWeatherGui()
    assert function.ui.powerHumidity.text() == '-'
    assert function.ui.powerTemp.text() == '-'
    assert function.ui.powerDewPoint.text() == '-'


def test_updatePowerWeatherGui_1(function):
    function.app.powerWeather.name = 'test'
    function.app.powerWeather.data['WEATHER_PARAMETERS.WEATHER_TEMPERATURE'] = 10.5
    function.updatePowerWeatherGui()
    assert function.ui.powerTemp.text() == '10.5'


def test_updatePowerWeatherGui_2(function):
    function.app.powerWeather.name = 'test'
    function.app.powerWeather.data['WEATHER_PARAMETERS.WEATHER_HUMIDITY'] = 10
    function.updatePowerWeatherGui()
    assert function.ui.powerHumidity.text() == ' 10'


def test_updatePowerWeatherGui_3(function):
    function.app.powerWeather.name = 'test'
    function.app.powerWeather.data['WEATHER_PARAMETERS.WEATHER_DEWPOINT'] = 10.5
    function.updatePowerWeatherGui()
    assert function.ui.powerDewPoint.text() == '10.5'


def test_updateOnlineWeatherGui_1(function):
    suc = function.updateOnlineWeatherGui()
    assert suc


def test_clearDirectWeatherGui_1(function):
    suc = function.clearDirectWeatherGui()
    assert suc


def test_updateDirectWeatherGui_1(function):
    function.deviceStat['directWeather'] = False
    suc = function.updateDirectWeatherGui()
    assert not suc


def test_updateDirectWeatherGui_2(function):
    function.deviceStat['directWeather'] = True
    suc = function.updateDirectWeatherGui()
    assert not suc


def test_updateDirectWeatherGui_3(function):
    class Test:
        weatherTemperature = 3
        weatherPressure = 1000
        weatherHumidity = 50
        weatherDewPoint = 10

    function.deviceStat['directWeather'] = True
    suc = function.updateDirectWeatherGui(setting=Test())
    assert suc
