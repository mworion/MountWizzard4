############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# Licence APL2.0
#
###########################################################

import numpy as np
import pytest
from mw4.base.loggerMW import setupLogging
from mw4.gui.mainWaddon.tabEnviron_Weather import EnvironWeather
from mw4.gui.utilities.toolsQtWidget import MWidget
from mw4.gui.widgets.main_ui import Ui_MainWindow
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock

setupLogging()


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    mainW = MWidget()
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
    function.app.deviceStat["sensor1Weather"] = False
    function.app.deviceStat["sensor2Weather"] = False
    function.app.deviceStat["sensor3Weather"] = False
    function.app.deviceStat["sensor4Weather"] = False
    function.app.deviceStat["directWeather"] = False
    function.smartEnvironGui()
    assert not function.ui.sensor1Group.isEnabled()
    assert not function.ui.sensor2Group.isEnabled()
    assert not function.ui.sensor3Group.isEnabled()
    assert not function.ui.sensor4Group.isEnabled()
    assert not function.ui.directGroup.isEnabled()


def test_smartEnvironGui_2(function):
    function.app.deviceStat["sensor1Weather"] = True
    function.app.deviceStat["sensor2Weather"] = True
    function.app.deviceStat["sensor3Weather"] = True
    function.app.deviceStat["sensor4Weather"] = True
    function.app.deviceStat["directWeather"] = True
    function.smartEnvironGui()
    assert function.ui.sensor1Group.isEnabled()
    assert function.ui.sensor2Group.isEnabled()
    assert function.ui.sensor3Group.isEnabled()
    assert function.ui.sensor4Group.isEnabled()
    assert function.ui.directGroup.isEnabled()


def test_smartEnvironGui_3(function):
    function.app.deviceStat["sensor1Weather"] = None
    function.app.deviceStat["sensor2Weather"] = None
    function.app.deviceStat["sensor3Weather"] = None
    function.app.deviceStat["sensor4Weather"] = None
    function.app.deviceStat["directWeather"] = False
    function.smartEnvironGui()
    assert not function.ui.sensor1Group.isEnabled()
    assert not function.ui.sensor2Group.isEnabled()
    assert not function.ui.sensor3Group.isEnabled()
    assert not function.ui.sensor4Group.isEnabled()
    assert not function.ui.directGroup.isEnabled()


def test_updateRefractionUpdateType_1(function):
    function.app.mount.setting.weatherStatus = 3
    function.refractionSource = "sensor4Weather"
    function.updateRefractionUpdateType()


def test_updateRefractionUpdateType_2(function):
    function.app.mount.setting.weatherStatus = 3
    function.refractionSource = "directWeather"
    function.updateRefractionUpdateType()


def test_updateRefractionUpdateType_3(function):
    function.app.mount.setting.weatherStatus = 0
    function.refractionSource = "directWeather"
    function.ui.refracManual.setChecked(False)
    function.updateRefractionUpdateType()
    assert function.ui.refracManual.isChecked()


def test_updateRefractionUpdateType_4(function):
    function.app.mount.setting.weatherStatus = 1
    function.refractionSource = "directWeather"
    function.ui.refracNoTrack.setChecked(False)
    function.updateRefractionUpdateType()


def test_updateRefractionUpdateType_5(function):
    function.app.mount.setting.weatherStatus = 2
    function.refractionSource = "directWeather"
    function.ui.refracCont.setChecked(False)
    function.updateRefractionUpdateType()


def test_setRefractionUpdateType_0(function):
    function.ui.showTabEnviron.setChecked(False)
    function.setRefractionUpdateType()


def test_setRefractionUpdateType_1(function):
    function.ui.showTabEnviron.setChecked(True)
    function.refractionSource = "onlineWeather"
    with mock.patch.object(
        function.app.mount.setting, "setDirectWeatherUpdateType", return_value=True
    ):
        function.setRefractionUpdateType()


def test_setRefractionUpdateType_2(function):
    function.ui.showTabEnviron.setChecked(True)
    function.app.mount.setting.weatherStatus = 1
    function.refractionSource = "directWeather"
    function.ui.refracManual.setChecked(True)
    with mock.patch.object(
        function.app.mount.setting, "setDirectWeatherUpdateType", return_value=True
    ):
        function.setRefractionUpdateType()


def test_setRefractionUpdateType_3(function):
    function.ui.showTabEnviron.setChecked(True)
    function.refractionSource = "directWeather"
    function.app.mount.setting.weatherStatus = 1
    function.ui.refracNoTrack.setChecked(True)
    with mock.patch.object(
        function.app.mount.setting, "setDirectWeatherUpdateType", return_value=True
    ):
        function.setRefractionUpdateType()


def test_setRefractionUpdateType_4(function):
    function.ui.showTabEnviron.setChecked(True)
    function.refractionSource = "directWeather"
    function.app.mount.setting.weatherStatus = 0
    function.ui.refracCont.setChecked(True)
    with mock.patch.object(
        function.app.mount.setting, "setDirectWeatherUpdateType", return_value=True
    ):
        function.setRefractionUpdateType()


def test_setRefractionSourceGui_1(function):
    function.setRefractionSourceGui()


def test_setRefractionSourceGui_2(function):
    function.setRefractionSourceGui()
    function.refractionSource = "sensor1Weather"
    function.setRefractionSourceGui()


def test_selectRefractionSource_1(function):
    function.ui.sensor1Group.setChecked(False)
    function.refractionSource = "sensor1Weather"
    with mock.patch.object(function, "setRefractionSourceGui"):
        with mock.patch.object(function, "setRefractionUpdateType"):
            function.selectRefractionSource("sensor2Weather")


def test_selectRefractionSource_2(function):
    function.ui.sensor1Group.setChecked(True)
    function.refractionSource = "directWeather"
    with mock.patch.object(function, "setRefractionSourceGui"):
        with mock.patch.object(function, "setRefractionUpdateType"):
            function.selectRefractionSource("sensor1Weather")


def test_isValidRefractionSource_1(function):
    function.refractionSource = "sensor1Weather"
    assert function.isValidRefractionSource()


def test_isValidRefractionSource_2(function):
    function.refractionSource = "test"
    assert not function.isValidRefractionSource()


def test_updateFilterRefractionParameters_1(function):
    function.refractionSource = "weather"
    function.updateFilterRefractionParameters()


def test_updateFilterRefractionParameters_2(function):
    function.refractionSource = "sensor1Weather"
    function.app.sensor1Weather.data["WEATHER_PARAMETERS.WEATHER_TEMPERATURE"] = 10
    function.app.sensor1Weather.data["WEATHER_PARAMETERS.WEATHER_PRESSURE"] = 1000
    function.updateFilterRefractionParameters()


def test_updateFilterRefractionParameters_3(function):
    function.refractionSource = "sensor1Weather"
    function.app.sensor1Weather.data.clear()
    function.updateFilterRefractionParameters()


def test_updateFilterRefractionParameters_4(function):
    function.refractionSource = "sensor1Weather"
    function.app.sensor1Weather.data["WEATHER_PARAMETERS.WEATHER_TEMPERATURE"] = 10
    function.app.sensor1Weather.data["WEATHER_PARAMETERS.WEATHER_PRESSURE"] = 1000
    function.updateFilterRefractionParameters()


def test_updateFilterRefractionParameters_5(function):
    function.refractionSource = "sensor1Weather"
    function.filteredPressure = np.full(100, 1000)
    function.app.sensor1Weather.data["WEATHER_PARAMETERS.WEATHER_TEMPERATURE"] = 10
    function.app.sensor1Weather.data["WEATHER_PARAMETERS.WEATHER_PRESSURE"] = 1000
    function.updateFilterRefractionParameters()


def test_movingAverageRefractionParameters_2(function):
    function.filteredTemperature = np.full(100, 10)
    function.filteredPressure = np.full(100, 1000)
    v1, v2 = function.movingAverageRefractionParameters()
    assert v1 == 10.0
    assert v2 == 1000.0


def test_updateRefractionParameters_1(function):
    function.refractionSource = "sensor1Weather"
    function.app.deviceStat["mount"] = False
    with mock.patch.object(function, "isValidRefractionSource", return_value=False):
        function.updateRefractionParameters()


def test_updateRefractionParameters_2(function):
    function.refractionSource = "directWeather"
    function.app.deviceStat["mount"] = True
    with mock.patch.object(function, "isValidRefractionSource", return_value=True):
        function.updateRefractionParameters()


def test_updateRefractionParameters_3(function):
    function.refractionSource = "sensor1Weather"
    function.app.deviceStat["mount"] = False
    with mock.patch.object(function, "isValidRefractionSource", return_value=True):
        with mock.patch.object(
            function, "movingAverageRefractionParameters", return_value=(0, 950)
        ):
            function.updateRefractionParameters()


def test_updateRefractionParameters_4(function):
    function.refractionSource = "sensor1Weather"
    function.app.deviceStat["mount"] = True
    with mock.patch.object(function, "isValidRefractionSource", return_value=True):
        with mock.patch.object(
            function, "movingAverageRefractionParameters", return_value=(0, 950)
        ):
            function.updateRefractionParameters()


def test_updateRefractionParameters_5(function):
    function.refractionSource = "onlineWeather"
    function.app.deviceStat["mount"] = True
    function.ui.refracManual.setChecked(True)
    function.app.mount.obsSite.status = 0
    with mock.patch.object(function, "isValidRefractionSource", return_value=True):
        with mock.patch.object(
            function, "movingAverageRefractionParameters", return_value=(10, 10)
        ):
            function.updateRefractionParameters()


def test_updateRefractionParameters_6(function):
    function.refractionSource = "onlineWeather"
    function.app.deviceStat["mount"] = True
    function.ui.refracNoTrack.setChecked(True)
    function.app.mount.obsSite.status = 0
    with mock.patch.object(function, "isValidRefractionSource", return_value=True):
        with mock.patch.object(
            function, "movingAverageRefractionParameters", return_value=(10, 10)
        ):
            function.updateRefractionParameters()


def test_updateRefractionParameters_7(function):
    function.refractionSource = "onlineWeather"
    function.app.deviceStat["mount"] = True
    function.ui.refracNoTrack.setChecked(True)
    function.app.mount.obsSite.status = 1

    with mock.patch.object(function, "isValidRefractionSource", return_value=True):
        with mock.patch.object(
            function, "movingAverageRefractionParameters", return_value=(10, 10)
        ):
            with mock.patch.object(
                function.app.mount.setting, "setRefractionTemp", return_value=False
            ):
                with mock.patch.object(
                    function.app.mount.setting, "setRefractionPress", return_value=False
                ):
                    function.updateRefractionParameters()


def test_updateRefractionParameters_8(function):
    function.refractionSource = "onlineWeather"
    function.app.deviceStat["mount"] = True
    function.ui.refracNoTrack.setChecked(True)
    function.app.mount.obsSite.status = 1

    with mock.patch.object(function, "isValidRefractionSource", return_value=True):
        with mock.patch.object(
            function, "movingAverageRefractionParameters", return_value=(10, 10)
        ):
            with mock.patch.object(
                function.app.mount.setting, "setRefractionTemp", return_value=True
            ):
                with mock.patch.object(
                    function.app.mount.setting, "setRefractionPress", return_value=True
                ):
                    function.updateRefractionParameters()


def test_updateSourceGui_1(function):
    function.app.sensor1Weather.data["WEATHER_PARAMETERS.WEATHER_TEMPERATURE"] = 10.5
    function.app.sensor1Weather.data["WEATHER_PARAMETERS.WEATHER_PRESSURE"] = 1000
    function.app.sensor1Weather.data["WEATHER_PARAMETERS.WEATHER_DEWPOINT"] = 10.5
    function.app.sensor1Weather.data["WEATHER_PARAMETERS.WEATHER_HUMIDITY"] = 10
    function.updateSourceGui()
    assert function.ui.temperature1.text() == "10.5"
    assert function.ui.pressure1.text() == "1000"
    assert function.ui.dewPoint1.text() == "10.5"
    assert function.ui.humidity1.text() == " 10"


def test_clearSourceGui_1(function):
    function.clearSourceGui("sensor1Weather", 1)
    assert function.ui.temperature1.text() == ""
    assert function.ui.pressure1.text() == ""
    assert function.ui.dewPoint1.text() == ""
    assert function.ui.humidity1.text() == ""
