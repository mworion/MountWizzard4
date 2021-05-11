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
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
from unittest import mock
from pathlib import Path

# external packages
from PyQt5.QtGui import QImage
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QObject
from PyQt5.QtCore import QThreadPool
from PyQt5.QtCore import pyqtSignal
from mountcontrol.qtmount import Mount
import requests
from skyfield.api import wgs84
from skyfield.api import Loader
import numpy as np

# local import
from gui.mainWmixin.tabEnviron import Environ
from gui.widgets.main_ui import Ui_MainWindow
from gui.utilities.toolsQtWidget import MWidget
from logic.environment.sensorWeather import SensorWeather
from logic.environment.onlineWeather import OnlineWeather
from logic.environment.weatherUPB import WeatherUPB
from logic.environment.skymeter import Skymeter
from base.loggerMW import setupLogging
setupLogging()


@pytest.fixture(autouse=True, scope='module')
def module(qapp):
    yield


@pytest.fixture(autouse=True, scope='function')
def function(module):

    class Test1(QObject):
        mount = Mount(host='localhost', MAC='00:00:00:00:00:00', verbose=False,
                      pathToData=Path('tests/data'))
        update10s = pyqtSignal()
        threadPool = QThreadPool()

    class Test(QObject):
        config = {'mainW': {}}
        threadPool = QThreadPool()
        update1s = pyqtSignal()
        update30m = pyqtSignal()
        message = pyqtSignal(str, int)
        mount = Mount(host='localhost', MAC='00:00:00:00:00:00', verbose=False,
                      pathToData=Path('tests/data'))
        mount.obsSite.location = wgs84.latlon(latitude_degrees=20,
                                       longitude_degrees=10,
                                       elevation_m=500)
        loader = Loader('tests/testData', verbose=False)
        planets = loader('de421_23.bsp')
        sensorWeather = SensorWeather(app=Test1())
        onlineWeather = OnlineWeather(app=Test1())
        powerWeather = WeatherUPB(app=Test1())
        skymeter = Skymeter(app=Test1())

    class Mixin(MWidget, Environ):
        def __init__(self):
            super().__init__()
            self.app = Test()
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
    suc = function.setRefractionUpdateType()
    assert not suc


def test_setRefractionUpdateType_2(function):
    function.refractionSource = 'directWeather'
    function.ui.checkRefracNone.setChecked(True)
    suc = function.setRefractionUpdateType()
    assert not suc


def test_setRefractionUpdateType_3(function):
    function.refractionSource = 'directWeather'
    function.ui.checkRefracNoTrack.setChecked(True)
    suc = function.setRefractionUpdateType()
    assert not suc


def test_setRefractionUpdateType_4(function):
    function.refractionSource = 'directWeather'
    function.ui.checkRefracCont.setChecked(True)
    suc = function.setRefractionUpdateType()
    assert not suc


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

    function.refractionSource = 'onlineWeather'
    function.sender = Sender
    suc = function.selectRefractionSource()
    assert suc


def test_selectRefractionSource_3(function):
    def Sender():
        return function.ui.onlineWeatherGroup

    function.refractionSource = 'onlineWeather'
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


def test_updateRefractionParameters_1(function, qtbot):
    function.refractionSource = 'directWeather'

    suc = function.updateRefractionParameters()
    assert not suc


def test_updateRefractionParameters_2(function, qtbot):
    function.refractionSource = 'onlineWeather'
    function.deviceStat['mount'] = False

    suc = function.updateRefractionParameters()
    assert not suc


def test_updateRefractionParameters_3(function, qtbot):
    function.refractionSource = 'onlineWeather'
    function.deviceStat['mount'] = True

    with mock.patch.object(function,
                           'movingAverageRefractionParameters',
                           return_value=(None, None)):
        suc = function.updateRefractionParameters()
        assert not suc


def test_updateRefractionParameters_4(function, qtbot):
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


def test_updateRefractionParameters_5(function, qtbot):
    def Sender():
        return function.ui.isOnline

    function.sender = Sender
    function.refractionSource = 'onlineWeather'
    function.deviceStat['mount'] = True
    function.ui.checkRefracNone.setChecked(False)
    function.ui.checkRefracNoTrack.setChecked(True)
    function.app.mount.obsSite.status = '0'
    with mock.patch.object(function,
                           'movingAverageRefractionParameters',
                           return_value=(10, 10)):
        suc = function.updateRefractionParameters()
        assert not suc


def test_updateRefractionParameters_6(function, qtbot):
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


def test_getWebDataWorker_1(function):
    suc = function.getWebDataWorker()
    assert not suc


def test_getWebDataWorker_2(function):
    suc = function.getWebDataWorker(url='http://test')
    assert not suc


def test_getWebDataWorker_3(function):
    class Test:
        status_code = 300
    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        suc = function.getWebDataWorker(url='http://test')
        assert not suc


def test_getWebDataWorker_4(function):
    class Test:
        status_code = 200
    with mock.patch.object(requests,
                           'get',
                           return_value=Test()):
        suc = function.getWebDataWorker(url='http://test')
        assert suc


def test_getWebDataWorker_5(function):
    class Test:
        status_code = 200
    with mock.patch.object(requests,
                           'get',
                           return_value=Test(),
                           side_effect=Exception):
        suc = function.getWebDataWorker(url='http://test')
        assert not suc


def test_processClearOutsideImage_1(function):
    image = QImage('tests/testData/forecast.png')
    suc = function.processClearOutsideImage(image=image)
    assert suc


def test_updateClearOutsideImage_1(function):
    suc = function.updateClearOutsideImage()
    assert not suc


def test_updateClearOutsideImage_2(function):
    class Test:
        content = 'test'

    suc = function.updateClearOutsideImage(Test())
    assert not suc


def test_updateClearOutsideImage_3(function):
    image = QImage('tests/testData/forecast.png')
    pixmapBase = QPixmap().fromImage(image)

    with open(Path('tests/testData/forecast.png'), 'rb') as image:
        f = image.read()
        b = bytes(f)

    class Test:
        content = b

    with mock.patch.object(function,
                           'processClearOutsideImage',
                           return_value=pixmapBase):
        suc = function.updateClearOutsideImage(Test())
        assert suc


def test_updateClearOutsideImage_4(function):
    class Test:
        pass

    suc = function.updateClearOutsideImage(Test())
    assert not suc


def test_updateClearOutside_1(function):
    function.ui.isOnline.setChecked(False)
    suc = function.updateClearOutside()
    assert not suc


def test_updateClearOutside_2(function):
    function.ui.isOnline.setChecked(True)
    suc = function.updateClearOutside()
    assert suc


def test_clearOnlineWeatherGui_1(function):
    function.clearOnlineWeatherGui()
    assert function.ui.onlineWeatherTemp.text() == '-'
    assert function.ui.onlineWeatherPress.text() == '-'
    assert function.ui.onlineWeatherHumidity.text() == '-'
    assert function.ui.onlineWeatherCloudCover.text() == '-'
    assert function.ui.onlineWeatherWindSpeed.text() == '-'
    assert function.ui.onlineWeatherWindDir.text() == '-'
    assert function.ui.onlineWeatherRainVol.text() == '-'


def test_updateOnlineWeatherGui_1(function):
    suc = function.updateOnlineWeatherGui()
    assert not suc


def test_updateOnlineWeatherGui_2(function):
    suc = function.updateOnlineWeatherGui(data={'temperature': 10,
                                                'pressure': 1000,
                                                'humidity': 50,
                                                'dewPoint': 10,
                                                'cloudCover': 50,
                                                'windSpeed': 10,
                                                'windDir': 120,
                                                'rain': 5})
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
