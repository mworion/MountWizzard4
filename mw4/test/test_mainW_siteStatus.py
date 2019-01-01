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
# Python  v3.6.7
#
# Michael Würtenberger
# (c) 2018
#
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import logging
import pytest
# external packages
import PyQt5.QtGui
import PyQt5.QtWidgets
import PyQt5.uic
import PyQt5.QtTest
import PyQt5.QtCore
# local import
from mw4 import mainApp

test = PyQt5.QtWidgets.QApplication([])
mwGlob = {'workDir': '.',
          'configDir': './mw4/test/config',
          'dataDir': './mw4/test/config',
          'modeldata': 'test',
          }

'''
@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global spy
    global app

    app = mainApp.MountWizzard4(mwGlob=mwGlob)
    spy = PyQt5.QtTest.QSignalSpy(app.message)
    yield
    spy = None
    app = None
'''
app = mainApp.MountWizzard4(mwGlob=mwGlob)
spy = PyQt5.QtTest.QSignalSpy(app.message)


def test_setMeridianLimitTrack1(qtbot):
    app.mount.sett.meridianLimitTrack = None
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'critical',
                           return_value=True):
        suc = app.mainW.setMeridianLimitTrack()
        assert not suc


def test_setMeridianLimitTrack3(qtbot):
    app.mount.sett.meridianLimitTrack = 10
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, False)):
        suc = app.mainW.setMeridianLimitTrack()
        assert not suc


def test_setMeridianLimitTrack4(qtbot):
    app.mount.sett.meridianLimitTrack = 10
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, True)):
        with mock.patch.object(app.mount.obsSite,
                               'setMeridianLimitTrack',
                               return_value=True):
            suc = app.mainW.setMeridianLimitTrack()
            assert suc


def test_setMeridianLimitSlew1(qtbot):
    app.mount.sett.meridianLimitSlew = None
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'critical',
                           return_value=True):
        suc = app.mainW.setMeridianLimitSlew()
        assert not suc


def test_setMeridianLimitSlew3(qtbot):
    app.mount.sett.meridianLimitSlew = 10
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, False)):
        suc = app.mainW.setMeridianLimitSlew()
        assert not suc


def test_setMeridianLimitSlew4(qtbot):
    app.mount.sett.meridianLimitSlew = 10
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, True)):
        with mock.patch.object(app.mount.obsSite,
                               'setMeridianLimitSlew',
                               return_value=True):
            suc = app.mainW.setMeridianLimitSlew()
            assert suc


def test_setHorizonLimitHigh1(qtbot):
    app.mount.sett.horizonLimitHigh = None
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'critical',
                           return_value=True):
        suc = app.mainW.setHorizonLimitHigh()
        assert not suc


def test_setHorizonLimitHigh3(qtbot):
    app.mount.sett.horizonLimitHigh = 10
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, False)):
        suc = app.mainW.setHorizonLimitHigh()
        assert not suc


def test_setHorizonLimitHigh4(qtbot):
    app.mount.sett.horizonLimitHigh = 10
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, True)):
        with mock.patch.object(app.mount.obsSite,
                               'setHorizonLimitHigh',
                               return_value=True):
            suc = app.mainW.setHorizonLimitHigh()
            assert suc


def test_setHorizonLimitLow1(qtbot):
    app.mount.sett.horizonLimitLow = None
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'critical',
                           return_value=True):
        suc = app.mainW.setHorizonLimitLow()
        assert not suc


def test_setHorizonLimitLow3(qtbot):
    app.mount.sett.horizonLimitLow = 10
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, False)):
        suc = app.mainW.setHorizonLimitLow()
        assert not suc


def test_setHorizonLimitLow4(qtbot):
    app.mount.sett.horizonLimitLow = 10
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, True)):
        with mock.patch.object(app.mount.obsSite,
                               'setHorizonLimitLow',
                               return_value=True):
            suc = app.mainW.setHorizonLimitLow()
            assert suc


def test_setSlewRate1(qtbot):
    app.mount.sett.slewRate = None
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'critical',
                           return_value=True):
        suc = app.mainW.setSlewRate()
        assert not suc


def test_setSlewRate3(qtbot):
    app.mount.sett.slewRate = 10
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, False)):
        suc = app.mainW.setSlewRate()
        assert not suc


def test_setSlewRate4(qtbot):
    app.mount.sett.slewRate = 10
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, True)):
        with mock.patch.object(app.mount.obsSite,
                               'setSlewRate',
                               return_value=True):
            suc = app.mainW.setSlewRate()
            assert suc


def test_setLongitude1(qtbot):
    app.mount.obsSite.location = None
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'critical',
                           return_value=True):
        suc = app.mainW.setLongitude()
        assert not suc


def test_setLongitude2(qtbot):
    elev = '999.9'
    lon = '+160*30:45.5'
    lat = '+45*30:45.5'
    app.mount.obsSite.location = lat, lon, elev
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getText',
                           return_value=(10, True)):
        suc = app.mainW.setLongitude()
        assert not suc


def test_setLongitude3(qtbot):
    elev = '999.9'
    lon = '+160*30:45.5'
    lat = '+45*30:45.5'
    app.mount.obsSite.location = lat, lon, elev
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getText',
                           return_value=(10, False)):
        suc = app.mainW.setLongitude()
        assert not suc


def test_setLongitude4(qtbot):
    elev = '999.9'
    lon = '+160*30:45.5'
    lat = '+45*30:45.5'
    app.mount.obsSite.location = lat, lon, elev
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getText',
                           return_value=(10, True)):
        with mock.patch.object(app.mount.obsSite,
                               'setLongitude',
                               return_value=True):
            suc = app.mainW.setLongitude()
            assert suc


def test_setLatitude1(qtbot):
    app.mount.obsSite.location = None
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'critical',
                           return_value=True):
        suc = app.mainW.setLatitude()
        assert not suc


def test_setLatitude2(qtbot):
    elev = '999.9'
    lon = '+160*30:45.5'
    lat = '+45*30:45.5'
    app.mount.obsSite.location = lat, lon, elev
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getText',
                           return_value=(10, True)):
        suc = app.mainW.setLatitude()
        assert not suc


def test_setLatitude3(qtbot):
    elev = '999.9'
    lon = '+160*30:45.5'
    lat = '+45*30:45.5'
    app.mount.obsSite.location = lat, lon, elev
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getText',
                           return_value=(10, False)):
        suc = app.mainW.setLatitude()
        assert not suc


def test_setLatitude4(qtbot):
    elev = '999.9'
    lon = '+160*30:45.5'
    lat = '+45*30:45.5'
    app.mount.obsSite.location = lat, lon, elev
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getText',
                           return_value=(10, True)):
        with mock.patch.object(app.mount.obsSite,
                               'setLatitude',
                               return_value=True):
            suc = app.mainW.setLatitude()
            assert suc


def test_setElevation1(qtbot):
    app.mount.obsSite.location = None
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'critical',
                           return_value=True):
        suc = app.mainW.setElevation()
        assert not suc


def test_setElevation3(qtbot):
    elev = '999.9'
    lon = '+160*30:45.5'
    lat = '+45*30:45.5'
    app.mount.obsSite.location = lat, lon, elev
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getDouble',
                           return_value=(10, False)):
        suc = app.mainW.setElevation()
        assert not suc


def test_setElevation4(qtbot):
    elev = '999.9'
    lon = '+160*30:45.5'
    lat = '+45*30:45.5'
    app.mount.obsSite.location = lat, lon, elev
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getDouble',
                           return_value=(10, True)):
        with mock.patch.object(app.mount.obsSite,
                               'setElevation',
                               return_value=True):
            suc = app.mainW.setElevation()
            assert suc


def test_newEnvironConnected(qtbot):
    with qtbot.waitSignal(app.message) as blocker:
        app.mainW.newEnvironDevice('test')
    assert ['INDI device [test] found', 0] == blocker.args


def test_indiEnvironConnected(qtbot):
    with qtbot.waitSignal(app.message) as blocker:
        app.mainW.indiEnvironConnected()
    assert ['INDI server environment connected', 0] == blocker.args


def test_indiEnvironDisconnected(qtbot):
    with qtbot.waitSignal(app.message) as blocker:
        app.mainW.indiEnvironDisconnected()
    assert ['INDI server environment disconnected', 0] == blocker.args


def test_updateEnvironGUI_1():
    app.environment.wDevice['sqm']['name'] = 'test'
    app.environment.wDevice['sqm']['data']['SKY_BRIGHTNESS'] = 10.5
    app.mainW.updateEnvironGUI('test')
    assert app.mainW.ui.SQR.text() == '10.50'


def test_updateEnvironGUI_2():
    app.environment.wDevice['local']['name'] = 'test'
    app.environment.wDevice['local']['data']['WEATHER_TEMPERATURE'] = 10.5
    app.mainW.updateEnvironGUI('test')
    assert app.mainW.ui.localTemp.text() == '10.5'


def test_updateEnvironGUI_3():
    app.environment.wDevice['local']['name'] = 'test'
    app.environment.wDevice['local']['data']['WEATHER_BAROMETER'] = 10.5
    app.mainW.updateEnvironGUI('test')
    assert app.mainW.ui.localPress.text() == ' 10.5'


def test_updateEnvironGUI_4():
    app.environment.wDevice['local']['name'] = 'test'
    app.environment.wDevice['local']['data']['WEATHER_DEWPOINT'] = 10.5
    app.mainW.updateEnvironGUI('test')
    assert app.mainW.ui.localDewPoint.text() == '10.5'


def test_updateEnvironGUI_5():
    app.environment.wDevice['local']['name'] = 'test'
    app.environment.wDevice['local']['data']['WEATHER_HUMIDITY'] = 10
    app.mainW.updateEnvironGUI('test')
    assert app.mainW.ui.localHumidity.text() == ' 10'


def test_updateEnvironGUI_6():
    app.environment.wDevice['global']['name'] = 'test'
    app.environment.wDevice['global']['data']['WEATHER_TEMPERATURE'] = 10.5
    app.mainW.updateEnvironGUI('test')
    assert app.mainW.ui.globalTemp.text() == '10.5'


def test_updateEnvironGUI_7():
    app.environment.wDevice['global']['name'] = 'test'
    app.environment.wDevice['global']['data']['WEATHER_PRESSURE'] = 10
    app.mainW.updateEnvironGUI('test')
    assert app.mainW.ui.globalPress.text() == ' 10.0'


def test_updateEnvironGUI_8():
    app.environment.wDevice['global']['name'] = 'test'
    app.environment.wDevice['global']['data']['WEATHER_HUMIDITY'] = 10
    app.mainW.updateEnvironGUI('test')
    assert app.mainW.ui.globalHumidity.text() == '10.0'


def test_updateEnvironGUI_9():
    app.environment.wDevice['global']['name'] = 'test'
    app.environment.wDevice['global']['data']['WEATHER_CLOUD_COVER'] = 10
    app.mainW.updateEnvironGUI('test')
    assert app.mainW.ui.cloudCover.text() == ' 10'


def test_updateEnvironGUI_10():
    app.environment.wDevice['global']['name'] = 'test'
    app.environment.wDevice['global']['data']['WEATHER_WIND_SPEED'] = 10
    app.mainW.updateEnvironGUI('test')
    assert app.mainW.ui.windSpeed.text() == ' 10'


def test_updateEnvironGUI_11():
    app.environment.wDevice['global']['name'] = 'test'
    app.environment.wDevice['global']['data']['WEATHER_RAIN_HOUR'] = 10
    app.mainW.updateEnvironGUI('test')
    assert app.mainW.ui.rainVol.text() == ' 10'


def test_updateEnvironGUI_12():
    app.environment.wDevice['global']['name'] = 'test'
    app.environment.wDevice['global']['data']['WEATHER_SNOW_HOUR'] = 10
    app.mainW.updateEnvironGUI('test')
    assert app.mainW.ui.snowVol.text() == ' 10'


def test_updateEnvironGUI_13():
    app.environment.wDevice['global']['name'] = 'OpenWeatherMap'
    app.environment.wDevice['global']['data']['WEATHER_SNOW_HOUR'] = 10
    app.mainW.updateEnvironGUI('OpenWeatherMap')
    assert app.mainW.ui.snowVol.text() == ' 10'


def test_updateEnvironMainStat1():
    uiList = [app.mainW.ui.localWeatherName,
              app.mainW.ui.globalWeatherName,
              app.mainW.ui.sqmName]
    value = app.mainW.updateEnvironMainStat(uiList)
    assert value == 3


def test_updateEnvironMainStat2():
    uiList = [app.mainW.ui.localWeatherName,
              app.mainW.ui.globalWeatherName,
              app.mainW.ui.sqmName]
    uiList[0].setProperty('color', 'red')
    value = app.mainW.updateEnvironMainStat(uiList)
    assert value == 2


def test_updateEnvironMainStat3():
    uiList = [app.mainW.ui.localWeatherName,
              app.mainW.ui.globalWeatherName,
              app.mainW.ui.sqmName]
    uiList[0].setProperty('color', 'red')
    uiList[1].setProperty('color', 'green')
    value = app.mainW.updateEnvironMainStat(uiList)
    assert value == 1


def test_updateEnvironMainStat4():
    uiList = [app.mainW.ui.localWeatherName,
              app.mainW.ui.globalWeatherName,
              app.mainW.ui.sqmName]
    uiList[0].setProperty('color', 'green')
    uiList[1].setProperty('color', 'green')
    value = app.mainW.updateEnvironMainStat(uiList)
    assert value == 0


def test_deviceEnvironConnected1():
    app.environment.wDevice['sqm']['name'] = 'test'
    app.mainW.deviceEnvironConnected('')
    color = app.mainW.ui.sqmName.property('color')
    assert color is None


def test_deviceEnvironConnected2():
    app.environment.wDevice['global']['name'] = 'test'
    app.mainW.deviceEnvironConnected('test')
    color = app.mainW.ui.globalWeatherName.property('color')
    assert color == 'green'


def test_deviceEnvironDisconnected1():
    app.environment.wDevice['sqm']['name'] = 'test'
    app.mainW.ui.sqmName.setProperty('color', None)
    app.mainW.deviceEnvironDisconnected('')
    color = app.mainW.ui.sqmName.property('color')
    assert color is None


def test_deviceEnvironDisconnected2():
    app.environment.wDevice['global']['name'] = 'test'
    app.mainW.deviceEnvironDisconnected('test')
    color = app.mainW.ui.globalWeatherName.property('color')
    assert color == 'red'


def test_removeEnvironDevice_1(qtbot):
    app.environment.wDevice['global']['name'] = 'test'
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.removeEnvironDevice('test')
        assert suc
    assert ['INDI device [test] removed', 0] == blocker.args