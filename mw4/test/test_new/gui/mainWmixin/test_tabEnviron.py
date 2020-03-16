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
import pytest
from unittest import mock
import logging

# external packages
from PyQt5.QtGui import QImage
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import pyqtSignal
from mountcontrol.qtmount import Mount
import requests
from skyfield.toposlib import Topos
import numpy as np

# local import
from mw4.gui.mainWmixin.tabEnviron import EnvironGui
from mw4.gui.widgets.main_ui import Ui_MainWindow
from mw4.gui.widget import MWidget
from mw4.environment.sensorWeather import SensorWeather
from mw4.environment.onlineWeather import OnlineWeather
from mw4.environment.skymeter import Skymeter
from mw4.base.loggerMW import CustomLogger


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown(qtbot):
    global ui, widget, Test, Test1, app

    class Test1(QObject):
        mount = Mount(expire=False, verbose=False, pathToData='mw4/test/data')
        update10s = pyqtSignal()
        threadPool = QThreadPool()

    class Test(QObject):
        config = {'mainW': {}}
        threadPool = QThreadPool()
        update1s = pyqtSignal()
        update30m = pyqtSignal()
        message = pyqtSignal(str, int)
        mount = Mount(expire=False, verbose=False, pathToData='mw4/test/data')
        mount.obsSite.location = Topos(latitude_degrees=20,
                                       longitude_degrees=10,
                                       elevation_m=500)
        sensorWeather = SensorWeather(app=Test1())
        onlineWeather = OnlineWeather(app=Test1())
        skymeter = Skymeter(app=Test1())

    widget = QWidget()
    ui = Ui_MainWindow()
    ui.setupUi(widget)

    app = EnvironGui(app=Test(), ui=ui,
                     clickable=MWidget().clickable)
    app.changeStyleDynamic = MWidget().changeStyleDynamic
    app.close = MWidget().close
    app.deleteLater = MWidget().deleteLater
    app.deviceStat = dict()
    app.log = CustomLogger(logging.getLogger(__name__), {})
    app.threadPool = QThreadPool()

    qtbot.addWidget(app)

    yield
    app.threadPool.waitForDone()
    del widget, ui, Test, Test1, app


def test_initConfig_1():
    suc = app.initConfig()
    assert suc


def test_storeConfig_1():
    suc = app.storeConfig()
    assert suc


def test_updateRefractionUpdateType_1():
    class Test:
        weatherStatus = 3
    app.refractionSource = 'onlineWeather'
    suc = app.updateRefractionUpdateType(setting=Test())
    assert not suc


def test_updateRefractionUpdateType_2():
    class Test:
        weatherStatus = 3
    app.refractionSource = 'directWeather'
    suc = app.updateRefractionUpdateType(setting=Test())
    assert not suc


def test_updateRefractionUpdateType_3():
    class Test:
        weatherStatus = 0
    app.refractionSource = 'directWeather'
    app.ui.checkRefracNone.setChecked(False)
    suc = app.updateRefractionUpdateType(setting=Test())
    assert suc
    assert app.ui.checkRefracNone.isChecked()


def test_updateRefractionUpdateType_4():
    class Test:
        weatherStatus = 1
    app.refractionSource = 'directWeather'
    app.ui.checkRefracNoTrack.setChecked(False)
    suc = app.updateRefractionUpdateType(setting=Test())
    assert suc


def test_updateRefractionUpdateType_5():
    class Test:
        weatherStatus = 2
    app.refractionSource = 'directWeather'
    app.ui.checkRefracCont.setChecked(False)
    suc = app.updateRefractionUpdateType(setting=Test())
    assert suc


def test_setRefractionUpdateType_1():
    app.refractionSource = 'onlineWeather'
    suc = app.setRefractionUpdateType()
    assert not suc


def test_setRefractionUpdateType_2():
    app.refractionSource = 'directWeather'
    app.ui.checkRefracNone.setChecked(True)
    suc = app.setRefractionUpdateType()
    assert not suc


def test_setRefractionUpdateType_3():
    app.refractionSource = 'directWeather'
    app.ui.checkRefracNoTrack.setChecked(True)
    suc = app.setRefractionUpdateType()
    assert not suc


def test_setRefractionUpdateType_4():
    app.refractionSource = 'directWeather'
    app.ui.checkRefracCont.setChecked(True)
    suc = app.setRefractionUpdateType()
    assert not suc


def test_setRefractionSourceGui_1():
    suc = app.setRefractionSourceGui()
    assert suc


def test_setRefractionSourceGui_2():
    app.refractionSource = 'onlineWeather'
    suc = app.setRefractionSourceGui()
    assert suc


def test_selectRefractionSource_1():
    def Sender():
        return ui.powerPort1

    app.sender = Sender
    suc = app.selectRefractionSource()
    assert suc


def test_selectRefractionSource_2():
    def Sender():
        return ui.onlineWeatherGroup

    app.refractionSource = 'onlineWeather'
    app.sender = Sender
    suc = app.selectRefractionSource()
    assert suc


def test_selectRefractionSource_3():
    def Sender():
        return ui.onlineWeatherGroup

    app.refractionSource = 'onlineWeather'
    app.ui.onlineWeatherGroup.setChecked(True)
    app.sender = Sender
    suc = app.selectRefractionSource()
    assert suc


def test_updateFilterRefractionParameters_1():
    app.refractionSource = 'onlineWeather'
    app.app.onlineWeather.data = {}
    suc = app.updateFilterRefractionParameters()
    assert not suc


def test_updateFilterRefractionParameters_2():
    app.refractionSource = 'weather'
    app.app.onlineWeather.data = {'temperature': 10,
                                  'pressure': 1000}
    suc = app.updateFilterRefractionParameters()
    assert not suc


def test_updateFilterRefractionParameters_3():
    app.refractionSource = 'onlineWeather'
    app.app.onlineWeather.data = {'temperature': 10,
                                  'pressure': 1000}
    suc = app.updateFilterRefractionParameters()
    assert suc


def test_updateFilterRefractionParameters_4():
    app.refractionSource = 'sensorWeather'
    suc = app.updateFilterRefractionParameters()
    assert not suc


def test_updateFilterRefractionParameters_5():
    app.refractionSource = 'sensorWeather'
    app.app.sensorWeather.data = {'WEATHER_PARAMETERS.WEATHER_TEMPERATURE': 10,
                                  'WEATHER_PARAMETERS.WEATHER_PRESSURE': 1000}
    suc = app.updateFilterRefractionParameters()
    assert suc


def test_updateFilterRefractionParameters_6():
    app.refractionSource = 'sensorWeather'
    app.filteredTemperature = None
    app.app.sensorWeather.data = {'WEATHER_PARAMETERS.WEATHER_TEMPERATURE': 10,
                                  'WEATHER_PARAMETERS.WEATHER_PRESSURE': 1000}
    suc = app.updateFilterRefractionParameters()
    assert suc


def test_updateFilterRefractionParameters_7():
    app.refractionSource = 'sensorWeather'
    app.filteredPressure = None
    app.app.sensorWeather.data = {'WEATHER_PARAMETERS.WEATHER_TEMPERATURE': 10,
                                  'WEATHER_PARAMETERS.WEATHER_PRESSURE': 1000}
    suc = app.updateFilterRefractionParameters()
    assert suc


def test_updateFilterRefractionParameters_8():
    app.refractionSource = 'sensorWeather'
    app.filteredTemperature = np.full(100, 10)
    app.app.sensorWeather.data = {'WEATHER_PARAMETERS.WEATHER_TEMPERATURE': 10,
                                  'WEATHER_PARAMETERS.WEATHER_PRESSURE': 1000}
    suc = app.updateFilterRefractionParameters()
    assert suc


def test_updateFilterRefractionParameters_9():
    app.refractionSource = 'sensorWeather'
    app.filteredPressure = np.full(100, 1000)
    app.app.sensorWeather.data = {'WEATHER_PARAMETERS.WEATHER_TEMPERATURE': 10,
                                  'WEATHER_PARAMETERS.WEATHER_PRESSURE': 1000}
    suc = app.updateFilterRefractionParameters()
    assert suc


def test_movingAverageRefractionParameters_1():
    v1, v2 = app.movingAverageRefractionParameters()
    assert v1 is None
    assert v2 is None


def test_movingAverageRefractionParameters_2():
    app.filteredTemperature = np.full(100, 10)
    app.filteredPressure = np.full(100, 1000)
    v1, v2 = app.movingAverageRefractionParameters()
    assert v1 == 10.0
    assert v2 == 1000.0


def test_updateRefractionParameters_1(qtbot):
    app.refractionSource = 'directWeather'

    suc = app.updateRefractionParameters()
    assert not suc


def test_updateRefractionParameters_2(qtbot):
    app.refractionSource = 'onlineWeather'
    app.deviceStat['mount'] = False

    suc = app.updateRefractionParameters()
    assert not suc


def test_updateRefractionParameters_3(qtbot):
    app.refractionSource = 'onlineWeather'
    app.deviceStat['mount'] = True

    with mock.patch.object(app,
                           'movingAverageRefractionParameters',
                           return_value=(None, None)):
        suc = app.updateRefractionParameters()
        assert not suc


def test_updateRefractionParameters_4(qtbot):
    def Sender():
        return ui.isOnline

    app.sender = Sender
    app.refractionSource = 'onlineWeather'
    app.deviceStat['mount'] = True
    app.ui.checkRefracNone.setChecked(True)

    suc = app.updateRefractionParameters()
    assert not suc


def test_updateRefractionParameters_5(qtbot):
    def Sender():
        return ui.isOnline

    app.sender = Sender
    app.refractionSource = 'onlineWeather'
    app.deviceStat['mount'] = True
    app.ui.checkRefracNone.setChecked(False)
    app.ui.checkRefracNoTrack.setChecked(True)
    app.app.mount.obsSite.status = '0'

    suc = app.updateRefractionParameters()
    assert not suc


def test_updateRefractionParameters_6(qtbot):
    def Sender():
        return ui.setRefractionManual
    app.sender = Sender
    app.refractionSource = 'onlineWeather'
    app.deviceStat['mount'] = True

    with mock.patch.object(app,
                           'movingAverageRefractionParameters',
                           return_value=(10, 10)):
        with mock.patch.object(app.app.mount.setting,
                               'setRefractionParam',
                               return_value=False):
            suc = app.updateRefractionParameters()
            assert not suc


def test_updateRefractionParameters_7(qtbot):
    def Sender():
        return ui.setRefractionManual
    app.sender = Sender
    app.refractionSource = 'onlineWeather'
    app.deviceStat['mount'] = True

    with mock.patch.object(app,
                           'movingAverageRefractionParameters',
                           return_value=(10, 10)):
        with mock.patch.object(app.app.mount.setting,
                               'setRefractionParam',
                               return_value=True):
            suc = app.updateRefractionParameters()
            assert suc


def test_clearEnvironGUI_1():
    app.clearSensorWeatherGui('test')
    assert app.ui.sensorWeatherTemp.text() == '-'
    assert app.ui.sensorWeatherPress.text() == '-'
    assert app.ui.sensorWeatherDewPoint.text() == '-'
    assert app.ui.sensorWeatherHumidity.text() == '-'


def test_updateEnvironGUI_1():
    app.app.sensorWeather.name = 'test'
    app.app.sensorWeather.data['WEATHER_PARAMETERS.WEATHER_TEMPERATURE'] = 10.5
    app.updateSensorWeatherGui()
    assert app.ui.sensorWeatherTemp.text() == '10.5'


def test_updateEnvironGUI_2():
    app.app.sensorWeather.name = 'test'
    app.app.sensorWeather.data['WEATHER_PARAMETERS.WEATHER_PRESSURE'] = 10.5
    app.updateSensorWeatherGui()
    assert app.ui.sensorWeatherPress.text() == ' 10.5'


def test_updateEnvironGUI_3():
    app.app.sensorWeather.name = 'test'
    app.app.sensorWeather.data['WEATHER_PARAMETERS.WEATHER_DEWPOINT'] = 10.5
    app.updateSensorWeatherGui()
    assert app.ui.sensorWeatherDewPoint.text() == '10.5'


def test_updateEnvironGUI_4():
    app.app.sensorWeather.name = 'test'
    app.app.sensorWeather.data['WEATHER_PARAMETERS.WEATHER_HUMIDITY'] = 10
    app.updateSensorWeatherGui()
    assert app.ui.sensorWeatherHumidity.text() == ' 10'


def test_clearSkymeterGUI_1():
    app.clearSkymeterGUI()
    assert app.ui.skymeterSQR.text() == '-'
    assert app.ui.skymeterTemp.text() == '-'


def test_updateSkymeterGUI_1():
    app.app.skymeter.name = 'test'
    app.app.skymeter.data['SKY_QUALITY.SKY_BRIGHTNESS'] = 10.5
    app.updateSkymeterGUI()
    assert app.ui.skymeterSQR.text() == '10.50'


def test_updateSkymeterGUI_2():
    app.app.skymeter.name = 'test'
    app.app.skymeter.data['SKY_QUALITY.SKY_TEMPERATURE'] = 10.5
    app.updateSkymeterGUI()
    assert app.ui.skymeterTemp.text() == '10.5'


def test_getWebDataRunner_1():
    suc = app.getWebDataWorker()
    assert not suc


def test_getWebDataRunner_2():
    suc = app.getWebDataWorker(url='http://test')
    assert not suc


def test_getWebDataRunner_3():
    class Test:
        status_code = 300
    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        suc = app.getWebDataWorker(url='http://test')
        assert not suc


def test_getWebDataRunner_4():
    class Test:
        status_code = 200
    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        suc = app.getWebDataWorker(url='http://test')
        assert suc


def test_updateClearOutsideImages_1():
    suc = app.updateClearOutsideImages()
    assert not suc


def test_updateClearOutsideImages_2():
    image = QImage('mw4/test/testData/forecast.png')
    suc = app.updateClearOutsideImages(image=image)
    assert suc


def test_updateClearOutsideGui_1():
    suc = app.updateClearOutsideGui()
    assert not suc


def test_updateClearOutsideGui_2():
    class Test:
        content = 'test'
    with mock.patch.object(QImage,
                           'loadFromData',
                           return_value='test'):
        with mock.patch.object(app,
                               'updateClearOutsideImages',
                               return_value=False):
            suc = app.updateClearOutsideGui(Test())
            assert not suc


def test_updateClearOutsideGui_3():
    class Test:
        content = 'test'
    with mock.patch.object(QImage,
                           'loadFromData',
                           return_value='test'):
        with mock.patch.object(app,
                               'updateClearOutsideImages',
                               return_value=True):
            suc = app.updateClearOutsideGui(Test())
            assert suc


def test_updateClearOutside_1():
    app.ui.isOnline.setChecked(False)
    suc = app.updateClearOutside()
    assert not suc


def test_updateClearOutside_2():
    app.ui.isOnline.setChecked(True)
    suc = app.updateClearOutside()
    assert suc


def test_clearOnlineWeatherGui_1():
    app.clearOnlineWeatherGui()
    assert app.ui.onlineWeatherTemp.text() == '-'
    assert app.ui.onlineWeatherPress.text() == '-'
    assert app.ui.onlineWeatherHumidity.text() == '-'
    assert app.ui.onlineWeatherCloudCover.text() == '-'
    assert app.ui.onlineWeatherWindSpeed.text() == '-'
    assert app.ui.onlineWeatherWindDir.text() == '-'
    assert app.ui.onlineWeatherRainVol.text() == '-'


def test_updateOnlineWeatherGui_1():
    suc = app.updateOnlineWeatherGui()
    assert not suc


def test_updateOnlineWeatherGui_2():
    suc = app.updateOnlineWeatherGui(data={'temperature': 10,
                                           'pressure': 1000,
                                           'humidity': 50,
                                           'dewPoint': 10,
                                           'cloudCover': 50,
                                           'windSpeed': 10,
                                           'winDir': 120,
                                           'rain': 5})
    assert suc


def test_clearDirectWeatherGui_1():
    suc = app.clearDirectWeatherGui()
    assert suc


def test_updateDirectWeatherGui_1():
    app.deviceStat['directWeather'] = False
    suc = app.updateDirectWeatherGui()
    assert not suc


def test_updateDirectWeatherGui_2():
    app.deviceStat['directWeather'] = True
    suc = app.updateDirectWeatherGui()
    assert not suc


def test_updateDirectWeatherGui_3():
    class Test:
        weatherTemperature = 3
        weatherPressure = 1000
        weatherHumidity = 50
        weatherDewPoint = 10

    app.deviceStat['directWeather'] = True
    suc = app.updateDirectWeatherGui(setting=Test())
    assert suc
