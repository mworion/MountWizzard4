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
# Python  v3.7.5
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
from io import BytesIO
# external packages
import PyQt5
import requests
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
    app.mainW.deviceStat['mount'] = True
    app.mainW.ui.checkRefracNone.setChecked(False)
    app.mainW.ui.checkRefracNoTrack.setChecked(True)
    app.mount.obsSite.status = '0'
    with mock.patch.object(app.mainW,
                           'movingAverageRefractionParameters',
                           return_value=(10, 10)):
        with mock.patch.object(app.mount.setting,
                               'setRefractionParam',
                               return_value=True):
            suc = app.mainW.updateRefractionParameters()
            assert not suc


def test_updateRefractionParameters_2(qtbot):
    app.mainW.deviceStat['mount'] = False
    app.mainW.ui.checkRefracNone.setChecked(False)
    app.mainW.ui.checkRefracNoTrack.setChecked(True)
    app.mount.obsSite.status = '0'
    with mock.patch.object(app.mainW,
                           'movingAverageRefractionParameters',
                           return_value=(10, 10)):
        with mock.patch.object(app.mount.setting,
                               'setRefractionParam',
                               return_value=True):
            suc = app.mainW.updateRefractionParameters()
            assert not suc


def test_updateRefractionParameters_3(qtbot):
    app.mainW.deviceStat['mount'] = True
    app.mainW.ui.checkRefracNone.setChecked(True)
    app.mainW.ui.checkRefracNoTrack.setChecked(False)
    app.mount.obsSite.status = '0'
    with mock.patch.object(app.mainW,
                           'movingAverageRefractionParameters',
                           return_value=(10, 10)):
        with mock.patch.object(app.mount.setting,
                               'setRefractionParam',
                               return_value=True):
            suc = app.mainW.updateRefractionParameters()
            assert not suc


def test_updateRefractionParameters_4(qtbot):
    app.mainW.ui.checkRefracNone.setChecked(False)
    app.mainW.ui.checkRefracNoTrack.setChecked(True)
    app.mount.obsSite.status = '1'
    app.mainW.deviceStat['mount'] = True
    app.mainW.refractionSource = 'sensorWeather'
    with mock.patch.object(app.mainW,
                           'movingAverageRefractionParameters',
                           return_value=(10, 10)):
        with mock.patch.object(app.mount.setting,
                               'setRefractionParam',
                               return_value=True):
            suc = app.mainW.updateRefractionParameters()
            assert suc


def test_updateRefractionParameters_5(qtbot):
    app.mainW.deviceStat['mount'] = True
    app.mainW.ui.checkRefracNone.setChecked(False)
    app.mainW.ui.checkRefracNoTrack.setChecked(True)
    app.mount.obsSite.status = '0'
    with mock.patch.object(app.mainW,
                           'movingAverageRefractionParameters',
                           return_value=(10, 10)):
        with mock.patch.object(app.mount.setting,
                               'setRefractionParam',
                               return_value=False):
            suc = app.mainW.updateRefractionParameters()
            assert not suc


def test_updateRefractionParameters_6(qtbot):
    app.mainW.deviceStat['mount'] = True
    app.mainW.ui.checkRefracNone.setChecked(False)
    app.mainW.ui.checkRefracNoTrack.setChecked(True)
    app.mount.obsSite.status = '0'
    with mock.patch.object(app.mainW,
                           'movingAverageRefractionParameters',
                           return_value=(None, 10)):
        with mock.patch.object(app.mount.setting,
                               'setRefractionParam',
                               return_value=True):
            suc = app.mainW.updateRefractionParameters()
            assert not suc


def test_updateRefractionParameters_7(qtbot):
    app.mainW.deviceStat['mount'] = True
    app.mainW.ui.checkRefracNone.setChecked(False)
    app.mainW.ui.checkRefracNoTrack.setChecked(True)
    app.mount.obsSite.status = '0'
    with mock.patch.object(app.mainW,
                           'movingAverageRefractionParameters',
                           return_value=(10, None)):
        with mock.patch.object(app.mount.setting,
                               'setRefractionParam',
                               return_value=True):
            suc = app.mainW.updateRefractionParameters()
            assert not suc
    app.mainW.ui.checkRefracNone.setChecked(True)


def test_updateRefractionParameters_8(qtbot):
    app.mainW.deviceStat['mount'] = True
    app.mainW.ui.checkRefracNone.setChecked(False)
    app.mainW.ui.checkRefracNoTrack.setChecked(True)
    app.mount.obsSite.status = '1'
    with mock.patch.object(app.mainW,
                           'movingAverageRefractionParameters',
                           return_value=(10, 10)):
        with mock.patch.object(app.mount.setting,
                               'setRefractionParam',
                               return_value=False):
            with qtbot.waitSignal(app.message) as blocker:
                suc = app.mainW.updateRefractionParameters()
                assert not suc
            assert ['Cannot perform refraction update', 2] == blocker.args
    app.mainW.ui.checkRefracNone.setChecked(True)


def test_clearEnvironGUI_1():
    app.mainW.clearSensorWeatherGui('test')
    assert app.mainW.ui.sensorWeatherTemp.text() == '-'
    assert app.mainW.ui.sensorWeatherPress.text() == '-'
    assert app.mainW.ui.sensorWeatherDewPoint.text() == '-'
    assert app.mainW.ui.sensorWeatherHumidity.text() == '-'


def test_updateEnvironGUI_1():
    app.sensorWeather.name = 'test'
    app.sensorWeather.data['WEATHER_TEMPERATURE'] = 10.5
    app.mainW.updateSensorWeatherGui('test')
    assert app.mainW.ui.sensorWeatherTemp.text() == '10.5'


def test_updateEnvironGUI_2():
    app.sensorWeather.name = 'test'
    app.sensorWeather.data['WEATHER_PRESSURE'] = 10.5
    app.mainW.updateSensorWeatherGui('test')
    assert app.mainW.ui.sensorWeatherPress.text() == ' 10.5'


def test_updateEnvironGUI_3():
    app.sensorWeather.name = 'test'
    app.sensorWeather.data['WEATHER_DEWPOINT'] = 10.5
    app.mainW.updateSensorWeatherGui('test')
    assert app.mainW.ui.sensorWeatherDewPoint.text() == '10.5'


def test_updateEnvironGUI_4():
    app.sensorWeather.name = 'test'
    app.sensorWeather.data['WEATHER_HUMIDITY'] = 10
    app.mainW.updateSensorWeatherGui('test')
    assert app.mainW.ui.sensorWeatherHumidity.text() == ' 10'


def test_clearSkymeterGUI_1():
    app.mainW.clearSkymeterGUI('test')
    assert app.mainW.ui.skymeterSQR.text() == '-'
    assert app.mainW.ui.skymeterTemp.text() == '-'


def test_updateSkymeterGUI_1():
    app.skymeter.name = 'test'
    app.skymeter.data['SKY_BRIGHTNESS'] = 10.5
    app.mainW.updateSkymeterGUI('test')
    assert app.mainW.ui.skymeterSQR.text() == '10.50'


def test_updateSkymeterGUI_2():
    app.skymeter.name = 'test'
    app.skymeter.data['SKY_TEMPERATURE'] = 10.5
    app.mainW.updateSkymeterGUI('test')
    assert app.mainW.ui.skymeterTemp.text() == '10.5'


def test_getWebDataRunner_1():
    suc = app.mainW.getWebDataWorker()
    assert not suc


def test_getWebDataRunner_2():
    suc = app.mainW.getWebDataWorker(url='http://test')
    assert not suc


def test_getWebDataRunner_3():
    class Test:
        status_code = 300
    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        suc = app.mainW.getWebDataWorker(url='http://test')
        assert not suc


def test_getWebDataRunner_4():
    class Test:
        status_code = 200
    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        suc = app.mainW.getWebDataWorker(url='http://test')
        assert suc


def test_updateClearOutsideImages_1():
    suc = app.mainW.updateClearOutsideImages()
    assert not suc


def test_updateClearOutsideImages_2():
    image = PyQt5.QtGui.QImage(mwGlob['imageDir'] + '/forecast.png')
    suc = app.mainW.updateClearOutsideImages(image=image)
    assert suc


def test_updateClearOutsideGui_1():
    suc = app.mainW.updateClearOutsideGui()
    assert not suc


def test_updateClearOutsideGui_2():
    class Test:
        content = 'test'
    with mock.patch.object(PyQt5.QtGui.QImage,
                           'loadFromData',
                           return_value='test'):
        with mock.patch.object(app.mainW,
                               'updateClearOutsideImages',
                               return_value=False):
            suc = app.mainW.updateClearOutsideGui(Test())
            assert not suc


def test_updateClearOutsideGui_3():
    class Test:
        content = 'test'
    with mock.patch.object(PyQt5.QtGui.QImage,
                           'loadFromData',
                           return_value='test'):
        with mock.patch.object(app.mainW,
                               'updateClearOutsideImages',
                               return_value=True):
            suc = app.mainW.updateClearOutsideGui(Test())
            assert suc


def test_updateClearOutside_1():
    app.mainW.ui.isOnline.setChecked(False)
    suc = app.mainW.updateClearOutside()
    assert not suc


def test_updateClearOutside_2():
    app.mainW.ui.isOnline.setChecked(True)
    suc = app.mainW.updateClearOutside()
    assert suc


def test_clearOpenWeatherMapGui_1():
    app.mainW.clearOnlineWeatherGui()
    assert app.mainW.ui.onlineWeatherTemp.text() == '-'
    assert app.mainW.ui.onlineWeatherPress.text() == '-'
    assert app.mainW.ui.onlineWeatherHumidity.text() == '-'
    assert app.mainW.ui.onlineWeatherCloudCover.text() == '-'
    assert app.mainW.ui.onlineWeatherWindSpeed.text() == '-'
    assert app.mainW.ui.onlineWeatherWindDir.text() == '-'
    assert app.mainW.ui.onlineWeatherRainVol.text() == '-'


def test_updateOpenWeatherMapGui_1():
    suc = app.mainW.updateOnlineWeatherGui()
    assert not suc
