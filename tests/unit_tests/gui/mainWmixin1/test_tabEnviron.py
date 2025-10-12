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
import pytest
from unittest import mock
import shutil
import webbrowser
import platform

# external packages
import numpy as np

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from mw4.gui.mainWmixin.tabEnviron import Environ
from mw4.gui.widgets.main_ui import Ui_MainWindow
from mw4.gui.utilities.toolsQtWidget import MWidget
from mw4.base.loggerMW import setupLogging
setupLogging()


@pytest.fixture(autouse=True, scope='module')
def function(qapp):
    shutil.copy('tests/testData/meteoblue.data',
                'tests/workDir/data/meteoblue.data')
    shutil.copy('tests/testData/openweathermap.data',
                'tests/workDir/data/openweathermap.data')

    class Mixin(MWidget, Environ):
        def __init__(self):
            super().__init__()
            self.app = App()
            self.msg = self.app.msg
            self.deviceStat = {}
            self.threadPool = self.app.threadPool
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)
            Environ.__init__(self)

    window = Mixin()
    yield window
    window.threadPool.waitForDone(1000)


def test_initConfig_1(function):
    suc = function.initConfig()
    assert suc


def test_storeConfig_1(function):
    suc = function.storeConfig()
    assert suc


def test_smartEnvironGui_1(function):
    function.deviceStat['directWeather'] = False
    function.deviceStat['sensorWeather'] = False
    function.deviceStat['onlineWeather'] = False
    function.deviceStat['skymeter'] = False
    function.deviceStat['powerWeather'] = False
    suc = function.smartEnvironGui()
    assert suc
    assert not function.ui.directWeatherGroup.isEnabled()
    assert not function.ui.sensorWeatherGroup.isEnabled()
    assert not function.ui.onlineWeatherGroup.isEnabled()
    assert not function.ui.skymeterGroup.isEnabled()
    assert not function.ui.powerGroup.isEnabled()


def test_smartEnvironGui_2(function):
    function.deviceStat['directWeather'] = True
    function.deviceStat['sensorWeather'] = True
    function.deviceStat['onlineWeather'] = True
    function.deviceStat['skymeter'] = True
    function.deviceStat['powerWeather'] = True
    suc = function.smartEnvironGui()
    assert suc
    assert function.ui.directWeatherGroup.isEnabled()
    assert function.ui.sensorWeatherGroup.isEnabled()
    assert function.ui.onlineWeatherGroup.isEnabled()
    assert function.ui.skymeterGroup.isEnabled()
    assert function.ui.powerGroup.isEnabled()


def test_smartEnvironGui_3(function):
    function.deviceStat['directWeather'] = None
    function.deviceStat['sensorWeather'] = None
    function.deviceStat['onlineWeather'] = None
    function.deviceStat['skymeter'] = None
    function.deviceStat['powerWeather'] = False
    suc = function.smartEnvironGui()
    assert suc
    assert not function.ui.directWeatherGroup.isEnabled()
    assert not function.ui.sensorWeatherGroup.isEnabled()
    assert not function.ui.onlineWeatherGroup.isEnabled()
    assert not function.ui.skymeterGroup.isEnabled()
    assert not function.ui.powerGroup.isEnabled()


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
    with mock.patch.object(function,
                           'setRefractionSourceGui'):
        with mock.patch.object(function,
                               'setRefractionUpdateType'):
            suc = function.selectRefractionSource()
            assert suc


def test_selectRefractionSource_2(function):
    def Sender():
        return function.ui.onlineWeatherGroup

    function.ui.onlineWeatherGroup.setChecked(False)
    function.refractionSource = 'onlineWeather'
    function.sender = Sender
    with mock.patch.object(function,
                           'setRefractionSourceGui'):
        with mock.patch.object(function,
                               'setRefractionUpdateType'):
            suc = function.selectRefractionSource()
            assert suc


def test_selectRefractionSource_3(function):
    def Sender():
        return function.ui.onlineWeatherGroup

    function.refractionSource = 'directWeather'
    function.ui.onlineWeatherGroup.setChecked(True)
    function.sender = Sender
    with mock.patch.object(function,
                           'setRefractionSourceGui'):
        with mock.patch.object(function,
                               'setRefractionUpdateType'):
            suc = function.selectRefractionSource()
            assert suc


def test_updateFilterRefractionParameters_1(function):
    function.refractionSource = 'onlineWeather'
    function.app.onlineWeather.data = {}
    suc = function.updateFilterRefractionParameters()
    assert not suc


def test_updateFilterRefractionParameters_2(function):
    function.refractionSource = 'weather'
    function.app.onlineWeather.data = {'WEATHER_PARAMETERS.WEATHER_TEMPERATURE': 10,
                                       'WEATHER_PARAMETERS.WEATHER_PRESSURE': 1000}
    suc = function.updateFilterRefractionParameters()
    assert not suc


def test_updateFilterRefractionParameters_3(function):
    function.refractionSource = 'onlineWeather'
    function.app.onlineWeather.data = {'WEATHER_PARAMETERS.WEATHER_TEMPERATURE': 10,
                                       'WEATHER_PARAMETERS.WEATHER_PRESSURE': 1000}
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
    function.app.sensorWeather.data = {}
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
    function.refractionSource = 'onlineWeather'
    function.deviceStat['mount'] = True
    function.ui.refracManual.setChecked(True)
    with mock.patch.object(function,
                           'movingAverageRefractionParameters',
                           return_value=(10, 10)):
        suc = function.updateRefractionParameters()
        assert not suc


def test_updateRefractionParameters_5(function):
    function.refractionSource = 'onlineWeather'
    function.deviceStat['mount'] = True
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
    function.deviceStat['mount'] = True
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
    function.deviceStat['mount'] = True
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


def test_clearOnlineWeatherGui_1(function):
    suc = function.clearOnlineWeatherGui()
    assert suc


def test_updateDirectWeatherGui_1(function):
    function.deviceStat['directWeather'] = False
    suc = function.updateDirectWeatherGui()
    assert suc


def test_updateDirectWeatherGui_2(function):
    function.deviceStat['directWeather'] = True
    suc = function.updateDirectWeatherGui()
    assert suc


def test_updateDirectWeatherGui_3(function):

    function.app.directWeather.data = {
        'WEATHER_PARAMETERS.WEATHER_TEMPERATURE': 10,
        'WEATHER_PARAMETERS.WEATHER_PRESSURE': 900,
        'WEATHER_PARAMETERS.WEATHER_DEWPOINT': 5,
        'WEATHER_PARAMETERS.WEATHER_HUMIDITY':50,
    }
    function.deviceStat['directWeather'] = True
    suc = function.updateDirectWeatherGui()
    assert suc


def test_clearSeeingEntries(function):
    suc = function.clearSeeingEntries()
    assert suc


def test_enableSeeingEntries_1(function):
    function.seeingEnabled = False
    suc = function.enableSeeingEntries()
    assert not suc


def test_enableSeeingEntries_1(function):
    function.seeingEnabled = True
    suc = function.enableSeeingEntries()
    assert suc


def test_addSkyfieldTimeObject(function):
    data = {
        'hour': [10, 11],
        'date': ['2022-01-01', '2022-01-01']
    }

    suc = function.addSkyfieldTimeObject(data)
    assert suc
    assert 'time' in data


def test_updateSeeingEntries_1(function):
    function.app.seeingWeather.data = {
        'test': {
            'hour': [10, 11],
            'date': ['2022-01-01', '2022-01-01']
        }
    }
    suc = function.updateSeeingEntries()
    assert not suc


def test_updateSeeingEntries_2(function):
    function.app.seeingWeather.data = {
        'meta': {
            'last_model_update': '2022-01-01',
        },
        'hourly': {
            'hour': [10] * 96,
            'date': ['2022-01-01'] * 96,
            'high_clouds': [1] * 96,
            'mid_clouds': [1] * 96,
            'low_clouds': [1] * 96,
            'seeing_arcsec': [1] * 96,
            'seeing1': [1] * 96,
            'seeing1_color': ['#404040'] * 96,
            'seeing2': [1] * 96,
            'seeing2_color': ['#404040'] * 96,
            'temperature': [1] * 96,
            'relative_humidity': [1] * 96,
            'badlayer_top': ['1'] * 96,
            'badlayer_bottom': ['1'] * 96,
            'badlayer_gradient': ['1'] * 96,
            'jetstream': [1] * 96,
        }
    }
    t = function.app.mount.obsSite.ts.utc(2022, 1, 1, 10, 0, 0)
    with mock.patch.object(function.app.mount.obsSite.ts,
                           'now',
                           return_value=t):
        suc = function.updateSeeingEntries()
        assert suc


def test_updateSeeingEntries_3(function):
    function.app.seeingWeather.data = {
        'meta': {
            'last_model_update': '2022-01-01',
        },
        'hourly': {
            'hour': [10] * 96,
            'date': ['2022-01-01'] * 96,
            'high_clouds': [1] * 96,
            'mid_clouds': [1] * 96,
            'low_clouds': [1] * 96,
            'seeing_arcsec': [1] * 96,
            'seeing1': [1] * 96,
            'seeing1_color': ['#404040'] * 96,
            'seeing2': [1] * 96,
            'seeing2_color': ['#404040'] * 96,
            'temperature': [1] * 96,
            'relative_humidity': [1] * 96,
            'badlayer_top': ['1'] * 96,
            'badlayer_bottom': ['1'] * 96,
            'badlayer_gradient': ['1'] * 96,
            'jetstream': [1] * 96,
        }
    }
    t = function.app.mount.obsSite.ts.utc(2023, 1, 1, 10, 0, 0)
    with mock.patch.object(function.app.mount.obsSite.ts,
                           'now',
                           return_value=t):
        suc = function.updateSeeingEntries()
        assert suc


def test_prepareSeeingTable_1(function):
    with mock.patch.object(platform,
                           'system',
                           return_value='Darwin'):
        suc = function.prepareSeeingTable()
        assert suc


def test_prepareSeeingTable_2(function):
    with mock.patch.object(platform,
                           'system',
                           return_value='Windows'):
        suc = function.prepareSeeingTable()
        assert suc


def test_openMeteoblue_1(function):
    with mock.patch.object(webbrowser,
                           'open',
                           return_value=True):
        suc = function.openMeteoblue()
        assert suc


def test_openMeteoblue_2(function):
    with mock.patch.object(webbrowser,
                           'open',
                           return_value=False):
        suc = function.openMeteoblue()
        assert suc
