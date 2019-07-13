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
# Python  v3.7.3
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import pytest
# external packages
# local import
from mw4.test.test_units.setupQt import setupQt


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app, spy, mwGlob, test
    app, spy, mwGlob, test = setupQt()
    yield


def test_initConfig_1():
    app.config['mainW'] = {}
    suc = app.mainW.initConfig()
    assert suc


def test_initConfig_2():
    del app.config['mainW']
    suc = app.mainW.initConfig()
    assert suc


def test_storeConfig_1():
    suc = app.storeConfig()
    assert suc


def test_setupIcons():
    suc = app.mainW.setupIcons()
    assert suc


def test_updateRefractionParameters_1(qtbot):
    app.mount.mountUp = True
    app.mainW.ui.checkRefracNone.setChecked(False)
    app.mainW.ui.checkRefracNoTrack.setChecked(True)
    app.mount.obsSite.status = '0'
    with mock.patch.object(app.environ,
                           'getFilteredRefracParams',
                           return_value=(10, 10)):
        with mock.patch.object(app.mount.obsSite,
                               'setRefractionParam',
                               return_value=True):
            suc = app.mainW.updateRefractionParameters()
            assert not suc


def test_updateRefractionParameters_2(qtbot):
    app.mount.mountUp = False
    app.mainW.ui.checkRefracNone.setChecked(False)
    app.mainW.ui.checkRefracNoTrack.setChecked(True)
    app.mount.obsSite.status = '0'
    with mock.patch.object(app.environ,
                           'getFilteredRefracParams',
                           return_value=(10, 10)):
        with mock.patch.object(app.mount.obsSite,
                               'setRefractionParam',
                               return_value=True):
            suc = app.mainW.updateRefractionParameters()
            assert not suc


def test_updateRefractionParameters_3(qtbot):
    app.mount.mountUp = True
    app.mainW.ui.checkRefracNone.setChecked(True)
    app.mainW.ui.checkRefracNoTrack.setChecked(False)
    app.mount.obsSite.status = '0'
    with mock.patch.object(app.environ,
                           'getFilteredRefracParams',
                           return_value=(10, 10)):
        with mock.patch.object(app.mount.obsSite,
                               'setRefractionParam',
                               return_value=True):
            suc = app.mainW.updateRefractionParameters()
            assert not suc


def test_updateRefractionParameters_4(qtbot):
    app.mount.mountUp = True
    app.mainW.ui.checkRefracNone.setChecked(False)
    app.mainW.ui.checkRefracNoTrack.setChecked(True)
    app.mount.obsSite.status = '1'
    with mock.patch.object(app.environ,
                           'getFilteredRefracParams',
                           return_value=(10, 10)):
        with mock.patch.object(app.mount.obsSite,
                               'setRefractionParam',
                               return_value=True):
            suc = app.mainW.updateRefractionParameters()
            assert suc


def test_updateRefractionParameters_5(qtbot):
    app.mount.mountUp = True
    app.mainW.ui.checkRefracNone.setChecked(False)
    app.mainW.ui.checkRefracNoTrack.setChecked(True)
    app.mount.obsSite.status = '0'
    with mock.patch.object(app.environ,
                           'getFilteredRefracParams',
                           return_value=(10, 10)):
        with mock.patch.object(app.mount.obsSite,
                               'setRefractionParam',
                               return_value=False):
            suc = app.mainW.updateRefractionParameters()
            assert not suc


def test_updateRefractionParameters_6(qtbot):
    app.mount.mountUp = True
    app.mainW.ui.checkRefracNone.setChecked(False)
    app.mainW.ui.checkRefracNoTrack.setChecked(True)
    app.mount.obsSite.status = '0'
    with mock.patch.object(app.environ,
                           'getFilteredRefracParams',
                           return_value=(None, 10)):
        with mock.patch.object(app.mount.obsSite,
                               'setRefractionParam',
                               return_value=True):
            suc = app.mainW.updateRefractionParameters()
            assert not suc


def test_updateRefractionParameters_7(qtbot):
    app.mount.mountUp = True
    app.mainW.ui.checkRefracNone.setChecked(False)
    app.mainW.ui.checkRefracNoTrack.setChecked(True)
    app.mount.obsSite.status = '0'
    with mock.patch.object(app.environ,
                           'getFilteredRefracParams',
                           return_value=(10, None)):
        with mock.patch.object(app.mount.obsSite,
                               'setRefractionParam',
                               return_value=True):
            suc = app.mainW.updateRefractionParameters()
            assert not suc
    app.mainW.ui.checkRefracNone.setChecked(True)


def test_updateRefractionParameters_8(qtbot):
    app.mount.mountUp = True
    app.mainW.ui.checkRefracNone.setChecked(False)
    app.mainW.ui.checkRefracNoTrack.setChecked(True)
    app.mount.obsSite.status = '1'
    with mock.patch.object(app.environ,
                           'getFilteredRefracParams',
                           return_value=(10, 10)):
        with mock.patch.object(app.mount.obsSite,
                               'setRefractionParam',
                               return_value=False):
            with qtbot.waitSignal(app.message) as blocker:
                suc = app.mainW.updateRefractionParameters()
                assert not suc
            assert ['Cannot perform refraction update', 2] == blocker.args
    app.mainW.ui.checkRefracNone.setChecked(True)


def test_clearEnvironGUI_1():
    app.mainW.clearEnvironGUI('test')
    assert app.mainW.ui.environTemp.text() == '-'
    assert app.mainW.ui.environPress.text() == '-'
    assert app.mainW.ui.environDewPoint.text() == '-'
    assert app.mainW.ui.environHumidity.text() == '-'


def test_updateEnvironGUI_1():
    app.environ.name = 'test'
    app.environ.data['WEATHER_TEMPERATURE'] = 10.5
    app.mainW.updateEnvironGUI('test')
    assert app.mainW.ui.environTemp.text() == '10.5'


def test_updateEnvironGUI_2():
    app.environ.name = 'test'
    app.environ.data['WEATHER_PRESSURE'] = 10.5
    app.mainW.updateEnvironGUI('test')
    assert app.mainW.ui.environPress.text() == ' 10.5'


def test_updateEnvironGUI_3():
    app.environ.name = 'test'
    app.environ.data['WEATHER_DEWPOINT'] = 10.5
    app.mainW.updateEnvironGUI('test')
    assert app.mainW.ui.environDewPoint.text() == '10.5'


def test_updateEnvironGUI_4():
    app.environ.name = 'test'
    app.environ.data['WEATHER_HUMIDITY'] = 10
    app.mainW.updateEnvironGUI('test')
    assert app.mainW.ui.environHumidity.text() == ' 10'


def test_clearSkymeterGUI_1():
    app.mainW.clearSkymeterGUI('test')
    assert app.mainW.ui.skymeterSQR.text() == '-'
    assert app.mainW.ui.skymeterTemp.text() == '-'


def test_updateSkymeterGUI_1():
    app.skymeter.name = 'test'
    app.skymeter.data['SKY_BRIGHTNESS'] = 10.5
    app.mainW.updateSkymeterGUI('test')
    assert app.mainW.ui.skymeterSQR.text() == '10.5'


def test_updateSkymeterGUI_2():
    app.skymeter.name = 'test'
    app.skymeter.data['SKY_TEMPERATURE'] = 10.5
    app.mainW.updateSkymeterGUI('test')
    assert app.mainW.ui.skymeterTemp.text() == '10.5'


def test_clearWeatherGUI_1():
    app.mainW.clearWeatherGUI('test')
    assert app.mainW.ui.weatherTemp.text() == '-'
    assert app.mainW.ui.weatherPress.text() == '-'
    assert app.mainW.ui.weatherDewPoint.text() == '-'
    assert app.mainW.ui.weatherHumidity.text() == '-'
    assert app.mainW.ui.weatherCloudCover.text() == '-'
    assert app.mainW.ui.weatherWindSpeed.text() == '-'
    assert app.mainW.ui.weatherRainVol.text() == '-'
    assert app.mainW.ui.weatherSnowVol.text() == '-'


def test_updateWeatherGUI_1():
    app.weather.name = 'test'
    app.weather.data['WEATHER_TEMPERATURE'] = 10.5
    app.mainW.updateWeatherGUI('test')
    assert app.mainW.ui.weatherTemp.text() == '10.5'


def test_updateWeatherGUI_2():
    app.weather.name = 'test'
    app.weather.data['WEATHER_PRESSURE'] = 10.5
    app.mainW.updateWeatherGUI('test')
    assert app.mainW.ui.weatherPress.text() == ' 10.5'


def test_updateWeatherGUI_3():
    app.weather.name = 'test'
    app.weather.data['WEATHER_DEWPOINT'] = 10.5
    app.mainW.updateWeatherGUI('test')
    assert app.mainW.ui.weatherDewPoint.text() == '10.5'


def test_updateWeatherGUI_4():
    app.weather.name = 'test'
    app.weather.data['WEATHER_HUMIDITY'] = 10
    app.mainW.updateWeatherGUI('test')
    assert app.mainW.ui.weatherHumidity.text() == ' 10'


def test_updateWeatherGUI_5():
    app.weather.name = 'test'
    app.weather.data['WEATHER_CLOUD_COVER'] = 10
    app.mainW.updateWeatherGUI('test')
    assert app.mainW.ui.weatherCloudCover.text() == ' 10'


def test_updateWeatherGUI_6():
    app.weather.name = 'test'
    app.weather.data['WEATHER_WIND_SPEED'] = 10
    app.mainW.updateWeatherGUI('test')
    assert app.mainW.ui.weatherWindSpeed.text() == ' 10'


def test_updateWeatherGUI_7():
    app.weather.name = 'test'
    app.weather.data['WEATHER_RAIN_HOUR'] = 10
    app.mainW.updateWeatherGUI('test')
    assert app.mainW.ui.weatherRainVol.text() == ' 10'


def test_updateWeatherGUI_8():
    app.weather.name = 'test'
    app.weather.data['WEATHER_SNOW_HOUR'] = 10
    app.mainW.updateWeatherGUI('test')
    assert app.mainW.ui.weatherSnowVol.text() == ' 10'
