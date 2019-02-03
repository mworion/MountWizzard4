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
import mw4.test.test_setupQt
from mw4.test.test_setupQt import setupQt
app, spy, mwGlob, test = setupQt()


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


def test_updateFwGui_productName():
    value = 'Test1234'
    app.mount.fw.productName = value
    app.mainW.updateFwGui()
    assert value == app.mainW.ui.productName.text()
    value = None
    app.mount.fw.productName = value
    app.mainW.updateFwGui()
    assert '-' == app.mainW.ui.productName.text()


def test_updateFwGui_hwVersion():
    value = 'Test1234'
    app.mount.fw.hwVersion = value
    app.mainW.updateFwGui()
    assert value == app.mainW.ui.hwVersion.text()
    value = None
    app.mount.fw.hwVersion = value
    app.mainW.updateFwGui()
    assert '-' == app.mainW.ui.hwVersion.text()


def test_updateFwGui_numberString():
    value = '2.15.18'
    app.mount.fw.numberString = value
    app.mainW.updateFwGui()
    assert value == app.mainW.ui.numberString.text()
    value = None
    app.mount.fw.numberString = value
    app.mainW.updateFwGui()
    assert '-' == app.mainW.ui.numberString.text()


def test_updateFwGui_fwdate():
    value = 'Test1234'
    app.mount.fw.fwdate = value
    app.mainW.updateFwGui()
    assert value == app.mainW.ui.fwdate.text()
    value = None
    app.mount.fw.fwdate = value
    app.mainW.updateFwGui()
    assert '-' == app.mainW.ui.fwdate.text()


def test_updateFwGui_fwtime():
    value = 'Test1234'
    app.mount.fw.fwtime = value
    app.mainW.updateFwGui()
    assert value == app.mainW.ui.fwtime.text()
    value = None
    app.mount.fw.fwtime = value
    app.mainW.updateFwGui()
    assert '-' == app.mainW.ui.fwtime.text()


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


def test_updateRefractionParameters_1(qtbot):
    app.mount.mountUp = True
    app.mainW.ui.checkRefracNone.setChecked(False)
    app.mainW.ui.checkRefracNoTrack.setChecked(True)
    app.mount.obsSite.status = '0'
    with mock.patch.object(app.environment,
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
    with mock.patch.object(app.environment,
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
    with mock.patch.object(app.environment,
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
    with mock.patch.object(app.environment,
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
    with mock.patch.object(app.environment,
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
    with mock.patch.object(app.environment,
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
    with mock.patch.object(app.environment,
                           'getFilteredRefracParams',
                           return_value=(10, None)):
        with mock.patch.object(app.mount.obsSite,
                               'setRefractionParam',
                               return_value=True):
            suc = app.mainW.updateRefractionParameters()
            assert not suc


def test_updateSetting_refractionTemp():
    value = '15'
    app.mount.sett.refractionTemp = value
    app.mainW.updateSettingGUI()
    assert '+15.0' == app.mainW.ui.refractionTemp.text()
    assert '+15.0' == app.mainW.ui.refractionTemp1.text()
    value = None
    app.mount.sett.refractionTemp = value
    app.mainW.updateSettingGUI()
    assert '-' == app.mainW.ui.refractionTemp.text()
    assert '-' == app.mainW.ui.refractionTemp1.text()


def test_updateSetting_refractionPress():
    value = '1050.0'
    app.mount.sett.refractionPress = value
    app.mainW.updateSettingGUI()
    assert value == app.mainW.ui.refractionPress.text()
    assert value == app.mainW.ui.refractionPress1.text()
    value = None
    app.mount.sett.refractionPress = value
    app.mainW.updateSettingGUI()
    assert '-' == app.mainW.ui.refractionPress.text()
    assert '-' == app.mainW.ui.refractionPress1.text()


def test_updateSetting_meridianLimitTrack():
    value = '15'
    app.mount.sett.meridianLimitTrack = value
    app.mainW.updateSettingGUI()
    assert '15.0' == app.mainW.ui.meridianLimitTrack.text()
    value = None
    app.mount.sett.meridianLimitTrack = value
    app.mainW.updateSettingGUI()
    assert '-' == app.mainW.ui.meridianLimitTrack.text()


def test_updateSetting_meridianLimitSlew():
    value = '15'
    app.mount.sett.meridianLimitSlew = value
    app.mainW.updateSettingGUI()
    assert '15.0' == app.mainW.ui.meridianLimitSlew.text()
    value = None
    app.mount.sett.meridianLimitSlew = value
    app.mainW.updateSettingGUI()
    assert '-' == app.mainW.ui.meridianLimitSlew.text()


def test_updateSetting_horizonLimitLow():
    value = '0'
    app.mount.sett.horizonLimitLow = value
    app.mainW.updateSettingGUI()
    assert '0.0' == app.mainW.ui.horizonLimitLow.text()
    value = None
    app.mount.sett.horizonLimitLow = value
    app.mainW.updateSettingGUI()
    assert '-' == app.mainW.ui.horizonLimitLow.text()


def test_updateSetting_horizonLimitHigh():
    value = '50'
    app.mount.sett.horizonLimitHigh = value
    app.mainW.updateSettingGUI()
    assert '50.0' == app.mainW.ui.horizonLimitHigh.text()
    value = None
    app.mount.sett.horizonLimitHigh = value
    app.mainW.updateSettingGUI()
    assert '-' == app.mainW.ui.horizonLimitHigh.text()


def test_updateSetting_timeToMeridian():
    app.mount.sett.timeToFlip = '100'
    app.mount.sett.meridianLimitTrack = '15'

    app.mainW.updateSettingGUI()
    assert ' 40' == app.mainW.ui.timeToMeridian.text()
    value = None
    app.mount.sett.timeToFlip = value
    app.mount.sett.meridianLimitTrack = value
    app.mainW.updateSettingGUI()
    assert '-' == app.mainW.ui.timeToMeridian.text()


def test_updateSettingExt_location():

    app.mount.obsSite.location = ['49:00:00', '11:00:00', '500']
    app.mainW.updateLocGUI()
    assert '11deg 00\' 00.0\"' == app.mainW.ui.siteLongitude.text()
    assert '49deg 00\' 00.0\"' == app.mainW.ui.siteLatitude.text()
    assert '500.0' == app.mainW.ui.siteElevation.text()

    app.mount.obsSite.location = None
    app.mainW.updateLocGUI()
    assert '-' == app.mainW.ui.siteLongitude.text()
    assert '-' == app.mainW.ui.siteLatitude.text()
    assert '-' == app.mainW.ui.siteElevation.text()
