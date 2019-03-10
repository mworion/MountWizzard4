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


def test_clearGUI():
    suc = app.mainW.clearGUI()
    assert suc


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


def test_updateSetting_slewRate():
    value = '5'
    app.mount.sett.slewRate = value
    app.mainW.updateSettingGUI()
    assert app.mainW.ui.slewRate.text() == ' 5'
    value = None
    app.mount.sett.slewRate = value
    app.mainW.updateSettingGUI()
    assert '-' == app.mainW.ui.slewRate.text()


def test_updateSetting_timeToFlip():
    value = '5'
    app.mount.sett.timeToFlip = value
    app.mainW.updateSettingGUI()
    assert app.mainW.ui.timeToFlip.text() == '  5'
    value = None
    app.mount.sett.timeToFlip = value
    app.mainW.updateSettingGUI()
    assert '-' == app.mainW.ui.timeToFlip.text()


def test_updateSetting_timeToMeridian():
    value = '5'
    app.mount.sett.timeToMeridian = value
    app.mainW.updateSettingGUI()
    assert app.mainW.ui.timeToMeridian.text() == '  5'
    value = None
    app.mount.sett.timeToMeridian = value
    app.mainW.updateSettingGUI()
    assert '-' == app.mainW.ui.timeToMeridian.text()


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


def test_updateFwGui_productName():
    app.mount.fw.productName = 'test'
    app.mainW.updateFwGui()
    assert app.mainW.ui.productName.text() == 'test'
    app.mount.fw.productName = None
    app.mainW.updateFwGui()
    assert app.mainW.ui.productName.text() == '-'


def test_updateFwGui_numberString():
    app.mount.fw.numberString = '1.2.34'
    app.mainW.updateFwGui()
    assert app.mainW.ui.numberString.text() == '1.2.34'
    app.mount.fw.numberString = None
    app.mainW.updateFwGui()
    assert app.mainW.ui.numberString.text() == '-'


def test_updateFwGui_fwdate():
    app.mount.fw.fwdate = 'test'
    app.mainW.updateFwGui()
    assert app.mainW.ui.fwdate.text() == 'test'
    app.mount.fw.fwdate = None
    app.mainW.updateFwGui()
    assert app.mainW.ui.fwdate.text() == '-'


def test_updateFwGui_fwtime():
    app.mount.fw.fwtime = 'test'
    app.mainW.updateFwGui()
    assert app.mainW.ui.fwtime.text() == 'test'
    app.mount.fw.fwtime = None
    app.mainW.updateFwGui()
    assert app.mainW.ui.fwtime.text() == '-'


def test_updateFwGui_hwVersion():
    app.mount.fw.hwVersion = 'test'
    app.mainW.updateFwGui()
    assert app.mainW.ui.hwVersion.text() == 'test'
    app.mount.fw.hwVersion = None
    app.mainW.updateFwGui()
    assert app.mainW.ui.hwVersion.text() == '-'


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
