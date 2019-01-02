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


#
#
# testing mainW gui booting shutdown
#
#

def test_initConfig_1():
    app.config['mainW'] = {}
    suc = app.mainW.initConfig()
    assert suc


def test_initConfig_2():
    del app.config['mainW']
    suc = app.mainW.initConfig()
    assert not suc


def test_initConfig_3():
    app.config['mainW'] = {}
    app.config['mainW']['winPosX'] = 10000
    app.config['mainW']['winPosY'] = 10000
    suc = app.mainW.initConfig()
    assert suc


def test_mountBoot1(qtbot):
    with mock.patch.object(app.mount,
                           'bootMount',
                           return_value=True):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.mountBoot()
            assert suc
        assert ['Mount booted', 0] == blocker.args


def test_mountBoot2(qtbot):
    with mock.patch.object(app.mount,
                           'bootMount',
                           return_value=False):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.mountBoot()
            assert not suc
        assert ['Mount cannot be booted', 2] == blocker.args


def test_mountShutdown1(qtbot):
    with mock.patch.object(app.mount.obsSite,
                           'shutdown',
                           return_value=True):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.mountShutdown()
            assert suc
        assert ['Shutting mount down', 0] == blocker.args


def test_mountShutdown2(qtbot):
    with mock.patch.object(app.mount.obsSite,
                           'shutdown',
                           return_value=False):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.mountShutdown()
            assert not suc
        assert ['Mount cannot be shutdown', 2] == blocker.args


#
#
# testing mainW gui updateMountConnStat
#
#


def test_updateMountConnStat():
    suc = app.mainW.updateMountConnStat(True)
    assert suc
    assert 'green' == app.mainW.ui.mountConnected.property('color')
    suc = app.mainW.updateMountConnStat(False)
    assert suc
    assert 'red' == app.mainW.ui.mountConnected.property('color')

#
#
# testing mainW gui update Gui
#
#


def test_clearMountGUI():
    suc = app.mainW.clearMountGUI()
    assert suc


def test_updateGui():
    suc = app.mainW.updateGUI()
    assert suc


def test_updateTask():
    suc = app.mainW.updateTask()
    assert suc


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
            assert suc


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
            assert not suc


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

#
#
# testing mainW gui model name
#
#


def test_setNameList():
    value = ['Test1', 'test2', 'test3', 'test4']
    app.mount.model.nameList = value
    app.mainW.setNameList()
    assert 4 == app.mainW.ui.nameList.count()
    value = None
    app.mount.model.nameList = value
    app.mainW.setNameList()
    assert 0 == app.mainW.ui.nameList.count()

#
#
# testing mainW gui setting
#
#


def test_updateSetting_slewRate():
    value = '15'
    app.mount.sett.slewRate = value
    app.mainW.updateSettingGUI()
    assert '15' == app.mainW.ui.slewRate.text()
    value = None
    app.mount.sett.slewRate = value
    app.mainW.updateSettingGUI()
    assert '-' == app.mainW.ui.slewRate.text()


def test_updateSetting_timeToFlip():
    value = '15'
    app.mount.sett.timeToFlip = value
    app.mainW.updateSettingGUI()
    assert ' 15' == app.mainW.ui.timeToFlip.text()
    value = None
    app.mount.sett.timeToFlip = value
    app.mainW.updateSettingGUI()
    assert '-' == app.mainW.ui.timeToFlip.text()


def test_updateSettingExt_UTCExpire():
    value = '2020-10-05'
    app.mount.sett.UTCExpire = value
    app.mainW.updateSetStatGUI()
    assert value == app.mainW.ui.UTCExpire.text()
    value = None
    app.mount.sett.UTCExpire = value
    app.mainW.updateSetStatGUI()
    assert '-' == app.mainW.ui.UTCExpire.text()


def test_updateSettingExt_UTCExpire1():
    value = '2016-10-05'
    app.mount.sett.UTCExpire = value
    app.mainW.updateSetStatGUI()
    assert value == app.mainW.ui.UTCExpire.text()
    value = None
    app.mount.sett.UTCExpire = value
    app.mainW.updateSetStatGUI()
    assert '-' == app.mainW.ui.UTCExpire.text()


def test_updateSettingExt_UTCExpire2():
    value = '2018-10-05'
    app.mount.sett.UTCExpire = value
    app.mainW.updateSetStatGUI()
    assert value == app.mainW.ui.UTCExpire.text()
    value = None
    app.mount.sett.UTCExpire = value
    app.mainW.updateSetStatGUI()
    assert '-' == app.mainW.ui.UTCExpire.text()


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


def test_updateSetting_statusUnattendedFlip():
    value = '1'
    app.mount.sett.statusUnattendedFlip = value
    app.mainW.updateSetStatGUI()
    assert 'ON' == app.mainW.ui.statusUnattendedFlip.text()
    value = None
    app.mount.sett.statusUnattendedFlip = value
    app.mainW.updateSetStatGUI()
    assert 'OFF' == app.mainW.ui.statusUnattendedFlip.text()


def test_updateSetting_statusDualTracking():
    value = '1'
    app.mount.sett.statusDualTracking = value
    app.mainW.updateSetStatGUI()
    assert 'ON' == app.mainW.ui.statusDualTracking.text()
    value = None
    app.mount.sett.statusDualTracking = value
    app.mainW.updateSetStatGUI()
    assert 'OFF' == app.mainW.ui.statusDualTracking.text()


def test_updateSetting_statusRefraction():
    value = '1'
    app.mount.sett.statusRefraction = value
    app.mainW.updateSetStatGUI()
    assert 'ON' == app.mainW.ui.statusRefraction.text()
    value = None
    app.mount.sett.statusRefraction = value
    app.mainW.updateSetStatGUI()
    assert 'OFF' == app.mainW.ui.statusRefraction.text()


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


def test_tracking_speed1():
    with mock.patch.object(app.mount.sett,
                           'checkRateLunar',
                           return_value=True):
        suc = app.mainW.updateSettingGUI()
        assert suc


def test_tracking_speed2():
    with mock.patch.object(app.mount.sett,
                           'checkRateSidereal',
                           return_value=True):
        suc = app.mainW.updateSettingGUI()
        assert suc


def test_tracking_speed3():
    with mock.patch.object(app.mount.sett,
                           'checkRateSolar',
                           return_value=True):
        suc = app.mainW.updateSettingGUI()
        assert suc


#
#
# testing mainW gui AlignGui
#
#


def test_updateAlignGui_numberStars():
    with mock.patch.object(app.mainW, 'showModelPolar') as mMock:
        mMock.return_value.showModelPolar.return_value = None

        value = '50'
        app.mount.model.numberStars = value
        app.mainW.updateAlignGUI()
        assert '50' == app.mainW.ui.numberStars.text()
        assert '50' == app.mainW.ui.numberStars1.text()
        value = None
        app.mount.model.numberStars = value
        app.mainW.updateAlignGUI()
        assert '-' == app.mainW.ui.numberStars.text()
        assert '-' == app.mainW.ui.numberStars1.text()


def test_updateAlignGui_altitudeError():
    with mock.patch.object(app.mainW, 'showModelPolar') as mMock:
        mMock.return_value.showModelPolar.return_value = None

        value = '50'
        app.mount.model.altitudeError = value
        app.mainW.updateAlignGUI()
        assert '50deg 00\' 00.0\"' == app.mainW.ui.altitudeError.text()
        value = None
        app.mount.model.altitudeError = value
        app.mainW.updateAlignGUI()
        assert '-' == app.mainW.ui.altitudeError.text()


def test_updateAlignGui_errorRMS():
    with mock.patch.object(app.mainW, 'showModelPolar') as mMock:
        mMock.return_value.showModelPolar.return_value = None

        value = '50'
        app.mount.model.errorRMS = value
        app.mainW.updateAlignGUI()
        assert '50.0' == app.mainW.ui.errorRMS.text()
        assert '50.0' == app.mainW.ui.errorRMS1.text()
        value = None
        app.mount.model.errorRMS = value
        app.mainW.updateAlignGUI()
        assert '-' == app.mainW.ui.errorRMS.text()
        assert '-' == app.mainW.ui.errorRMS1.text()


def test_updateAlignGui_azimuthError():
    with mock.patch.object(app.mainW, 'showModelPolar') as mMock:
        mMock.return_value.showModelPolar.return_value = None

        value = '50'
        app.mount.model.azimuthError = value
        app.mainW.updateAlignGUI()
        assert '50deg 00\' 00.0\"' == app.mainW.ui.azimuthError.text()
        value = None
        app.mount.model.azimuthError = value
        app.mainW.updateAlignGUI()
        assert '-' == app.mainW.ui.azimuthError.text()


def test_updateAlignGui_terms():
    with mock.patch.object(app.mainW, 'showModelPolar') as mMock:
        mMock.return_value.showModelPolar.return_value = None

        value = '50'
        app.mount.model.terms = value
        app.mainW.updateAlignGUI()
        assert '50.0' == app.mainW.ui.terms.text()
        value = None
        app.mount.model.terms = value
        app.mainW.updateAlignGUI()
        assert '-' == app.mainW.ui.terms.text()


def test_updateAlignGui_orthoError():
    with mock.patch.object(app.mainW, 'showModelPolar') as mMock:
        mMock.return_value.showModelPolar.return_value = None

        value = '50'
        app.mount.model.orthoError = value
        app.mainW.updateAlignGUI()
        assert '50deg 00\' 00.0\"' == app.mainW.ui.orthoError.text()
        value = None
        app.mount.model.orthoError = value
        app.mainW.updateAlignGUI()
        assert '-' == app.mainW.ui.orthoError.text()


def test_updateAlignGui_positionAngle():
    with mock.patch.object(app.mainW, 'showModelPolar') as mMock:
        mMock.return_value.showModelPolar.return_value = None

        value = '50'
        app.mount.model.positionAngle = value
        app.mainW.updateAlignGUI()
        assert ' 50.0' == app.mainW.ui.positionAngle.text()
        value = None
        app.mount.model.positionAngle = value
        app.mainW.updateAlignGUI()
        assert '-' == app.mainW.ui.positionAngle.text()


def test_updateAlignGui_polarError():
    with mock.patch.object(app.mainW, 'showModelPolar') as mMock:
        mMock.return_value.showModelPolar.return_value = None

        value = '50'
        app.mount.model.polarError = value
        app.mainW.updateAlignGUI()
        assert '50deg 00\' 00.0\"' == app.mainW.ui.polarError.text()
        value = None
        app.mount.model.polarError = value
        app.mainW.updateAlignGUI()
        assert '-' == app.mainW.ui.polarError.text()


def test_updateAlignGui_altitudeTurns_1():
    value = 1.5
    app.mount.model.altitudeTurns = value
    app.mainW.updateAlignGUI()
    assert '1.5 revs down' == app.mainW.ui.altitudeTurns.text()
    value = None
    app.mount.model.altitudeTurns = value
    app.mainW.updateAlignGUI()
    assert '-' == app.mainW.ui.altitudeTurns.text()


def test_updateAlignGui_altitudeTurns_2():
    value = -1.5
    app.mount.model.altitudeTurns = value
    app.mainW.updateAlignGUI()
    assert '1.5 revs up' == app.mainW.ui.altitudeTurns.text()
    value = None
    app.mount.model.altitudeTurns = value
    app.mainW.updateAlignGUI()
    assert '-' == app.mainW.ui.altitudeTurns.text()


def test_updateAlignGui_azimuthTurns_1():
    value = 1.5
    app.mount.model.azimuthTurns = value
    app.mainW.updateAlignGUI()
    assert '1.5 revs left' == app.mainW.ui.azimuthTurns.text()
    value = None
    app.mount.model.azimuthTurns = value
    app.mainW.updateAlignGUI()
    assert '-' == app.mainW.ui.azimuthTurns.text()


def test_updateAlignGui_azimuthTurns_2():
    value = -1.5
    app.mount.model.azimuthTurns = value
    app.mainW.updateAlignGUI()
    assert '1.5 revs right' == app.mainW.ui.azimuthTurns.text()
    value = None
    app.mount.model.azimuthTurns = value
    app.mainW.updateAlignGUI()
    assert '-' == app.mainW.ui.azimuthTurns.text()


def test_closeEvent():

    app.mainW.showStatus = True
    app.mainW.closeEvent(1)

    assert not app.mainW.showStatus

#
#
# testing mainW gui model polar
#
#


def test_showModelPolar1():
    app.mount.obsSite.location = ['49:00:00', '11:00:00', '580']
    app.mount.model._parseStars(['21:52:58.95,+08*56:10.1,   5.7,201',
                                 '21:06:10.79,+45*20:52.8,  12.1,329',
                                 '23:13:58.02,+38*48:18.8,  31.0,162',
                                 '17:43:41.26,+59*15:30.7,   8.4,005',
                                 ],
                                4)
    app.mainW.ui.checkShowErrorValues.setChecked(True)
    suc = app.mainW.showModelPolar()
    assert suc


def test_showModelPolar2():
    app = mainApp.MountWizzard4(mwGlob=mwGlob)
    app.mount.obsSite.location = ['49:00:00', '11:00:00', '580']
    app.mainW.ui.checkShowErrorValues.setChecked(True)
    suc = app.mainW.showModelPolar()
    assert not suc


def test_showModelPolar3():
    app = mainApp.MountWizzard4(mwGlob=mwGlob)
    app.mainW.ui.checkShowErrorValues.setChecked(True)
    suc = app.mainW.showModelPolar()
    assert not suc

#
#
# testing mainW gui change tracking
#
#


def test_changeTracking_ok1(qtbot):
    app.mount.obsSite.status = 0
    with mock.patch.object(app.mount.obsSite,
                           'stopTracking',
                           return_value=False):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.changeTracking()
            assert suc
        assert ['Cannot stop tracking', 2] == blocker.args


def test_changeTracking_ok2(qtbot):
    app.mount.obsSite.status = 0
    with mock.patch.object(app.mount.obsSite,
                           'stopTracking',
                           return_value=True):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.changeTracking()
            assert suc
        assert ['Stopped tracking', 0] == blocker.args


def test_changeTracking_ok3(qtbot):
    app.mount.obsSite.status = 1
    with mock.patch.object(app.mount.obsSite,
                           'startTracking',
                           return_value=False):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.changeTracking()
            assert suc
        assert ['Cannot start tracking', 2] == blocker.args


def test_changeTracking_ok4(qtbot):
    app.mount.obsSite.status = 1
    with mock.patch.object(app.mount.obsSite,
                           'startTracking',
                           return_value=True):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.changeTracking()
            assert suc
        assert ['Started tracking', 0] == blocker.args


def test_changePark_ok1(qtbot):
    app.mount.obsSite.status = 5
    with mock.patch.object(app.mount.obsSite,
                           'unpark',
                           return_value=False):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.changePark()
            assert suc
        assert ['Cannot unpark mount', 2] == blocker.args


def test_changePark_ok2(qtbot):
    app.mount.obsSite.status = 5
    with mock.patch.object(app.mount.obsSite,
                           'unpark',
                           return_value=True):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.changePark()
            assert suc
        assert ['Mount unparked', 0] == blocker.args


def test_changePark_ok3(qtbot):
    app.mount.obsSite.status = 1
    with mock.patch.object(app.mount.obsSite,
                           'park',
                           return_value=False):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.changePark()
            assert suc
        assert ['Cannot park mount', 2] == blocker.args


def test_changePark_ok4(qtbot):
    app.mount.obsSite.status = 1
    with mock.patch.object(app.mount.obsSite,
                           'park',
                           return_value=True):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.changePark()
            assert suc
        assert ['Mount parked', 0] == blocker.args


def test_saveProfile1(qtbot):
    with mock.patch.object(app,
                           'saveConfig',
                           return_value=True):
        with qtbot.waitSignal(app.message) as blocker:
            app.mainW.saveProfile()
        assert ['Actual profile saved', 0] == blocker.args


def test_loadProfile1(qtbot):
    with mock.patch.object(app.mainW,
                           'openFile',
                           return_value=('config', 'test', 'cfg')):
        with mock.patch.object(app,
                               'loadConfig',
                               return_value=True):
            with qtbot.waitSignal(app.message) as blocker:
                suc = app.mainW.loadProfile()
                assert suc
            assert ['Profile: [test] loaded', 0] == blocker.args


def test_loadProfile2(qtbot):
    with mock.patch.object(app.mainW,
                           'openFile',
                           return_value=('config', 'test', 'cfg')):
        with mock.patch.object(app,
                               'loadConfig',
                               return_value=False):
            with qtbot.waitSignal(app.message) as blocker:
                suc = app.mainW.loadProfile()
                assert suc
            assert ['Profile: [test] cannot no be loaded', 2] == blocker.args


def test_loadProfile3(qtbot):
    with mock.patch.object(app.mainW,
                           'openFile',
                           return_value=(None, 'test', 'cfg')):
        suc = app.mainW.loadProfile()
        assert not suc


def test_saveProfileAs1(qtbot):
    with mock.patch.object(app.mainW,
                           'saveFile',
                           return_value=('config', 'test', 'cfg')):
        with mock.patch.object(app,
                               'saveConfig',
                               return_value=True):
            with qtbot.waitSignal(app.message) as blocker:
                suc = app.mainW.saveProfileAs()
                assert suc
            assert ['Profile: [test] saved', 0] == blocker.args


def test_saveProfileAs2(qtbot):
    with mock.patch.object(app.mainW,
                           'saveFile',
                           return_value=('config', 'test', 'cfg')):
        with mock.patch.object(app,
                               'saveConfig',
                               return_value=False):
            with qtbot.waitSignal(app.message) as blocker:
                suc = app.mainW.saveProfileAs()
                assert suc
            assert ['Profile: [test] cannot no be saved', 2] == blocker.args


def test_saveProfileAs3(qtbot):
    with mock.patch.object(app.mainW,
                           'saveFile',
                           return_value=(None, 'test', 'cfg')):
        suc = app.mainW.saveProfileAs()
        assert not suc


def test_saveProfile2(qtbot):
    with mock.patch.object(app,
                           'saveConfig',
                           return_value=False):
        with qtbot.waitSignal(app.message) as blocker:
            app.mainW.saveProfile()
        assert ['Actual profile cannot not be saved', 2] == blocker.args


def test_setLoggingLevel1(qtbot):
    app.mainW.ui.loglevelDebug.setChecked(True)
    app.mainW.setLoggingLevel()
    val = logging.getLogger().getEffectiveLevel()
    assert val == 10


def test_setLoggingLevel2(qtbot):
    app.mainW.ui.loglevelInfo.setChecked(True)
    app.mainW.setLoggingLevel()
    val = logging.getLogger().getEffectiveLevel()
    assert val == 20


def test_setLoggingLevel3(qtbot):
    app.mainW.ui.loglevelWarning.setChecked(True)
    app.mainW.setLoggingLevel()
    val = logging.getLogger().getEffectiveLevel()
    assert val == 30


def test_setLoggingLevel4(qtbot):
    app.mainW.ui.loglevelError.setChecked(True)
    app.mainW.setLoggingLevel()
    val = logging.getLogger().getEffectiveLevel()
    assert val == 40


def test_setLunarTracking1(qtbot):
    with mock.patch.object(app.mount.obsSite,
                           'setLunarTracking',
                           return_value=True):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.setLunarTracking()
            assert suc
        assert ['Tracking set to Lunar', 0] == blocker.args


def test_setLunarTracking2(qtbot):
    with mock.patch.object(app.mount.obsSite,
                           'setLunarTracking',
                           return_value=False):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.setLunarTracking()
            assert not suc
        assert ['Cannot set tracking to Lunar', 2] == blocker.args


def test_setSiderealTracking1(qtbot):
    with mock.patch.object(app.mount.obsSite,
                           'setSiderealTracking',
                           return_value=True):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.setSiderealTracking()
            assert suc
        assert ['Tracking set to Sidereal', 0] == blocker.args


def test_setSiderealTracking2(qtbot):
    with mock.patch.object(app.mount.obsSite,
                           'setSiderealTracking',
                           return_value=False):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.setSiderealTracking()
            assert not suc
        assert ['Cannot set tracking to Sidereal', 2] == blocker.args


def test_setSolarTracking1(qtbot):
    with mock.patch.object(app.mount.obsSite,
                           'setSolarTracking',
                           return_value=True):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.setSolarTracking()
            assert suc
        assert ['Tracking set to Solar', 0] == blocker.args


def test_setSolarTracking2(qtbot):
    with mock.patch.object(app.mount.obsSite,
                           'setSolarTracking',
                           return_value=False):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.setSolarTracking()
            assert not suc
        assert ['Cannot set tracking to Solar', 2] == blocker.args


def test_enableRelay1(qtbot):
    app.mainW.ui.checkEnableRelay.setChecked(True)
    with mock.patch.object(app.relay,
                           'startTimers',
                           return_value=None):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.enableRelay()
            assert suc
        assert ['Relay enabled', 0] == blocker.args


def test_enableRelay2(qtbot):
    app.mainW.ui.checkEnableRelay.setChecked(False)
    with mock.patch.object(app.relay,
                           'startTimers',
                           return_value=None):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.enableRelay()
            assert suc
        assert ['Relay disabled', 0] == blocker.args


def test_relayHost():
    app.mainW.ui.relayHost.setText('test')
    app.mainW.relayHost()

    assert app.relay.host == ('test', 80)


def test_relayUser():
    app.mainW.ui.relayUser.setText('test')
    app.mainW.relayUser()

    assert app.relay.user == 'test'


def test_relayPassword():
    app.mainW.ui.relayPassword.setText('test')
    app.mainW.relayPassword()

    assert app.relay.password == 'test'


def test_mountHost():
    app.mainW.ui.mountHost.setText('test')
    app.mainW.mountHost()

    assert app.mount.host == ('test', 3492)


def test_mountMAC():
    app.mainW.ui.mountMAC.setText('00:00:00:00:00:00')
    app.mainW.mountMAC()

    assert app.mount.MAC == '00:00:00:00:00:00'


def test_indiHost():
    app.mainW.ui.indiHost.setText('TEST')
    app.mainW.indiHost()
    assert app.environment.client.host == ('TEST', 7624)


def test_localWeatherName():
    app.mainW.ui.localWeatherName.setText('TEST')
    app.mainW.localWeatherName()
    assert 'TEST' == app.environment.wDevice['local']['name']


def test_globalWeatherName():
    app.mainW.ui.globalWeatherName.setText('TEST')
    app.mainW.globalWeatherName()
    assert 'TEST' == app.environment.wDevice['global']['name']


def test_sqmWeatherName():
    app.mainW.ui.sqmName.setText('TEST')
    app.mainW.sqmName()
    assert 'TEST' == app.environment.wDevice['sqm']['name']


def test_config():
    app.config = {
        'profileName': 'config',
        'version': '4.0',
        'filePath': None,
        'mainW': {},
    }
    app.saveConfig()
    app.mainW.initConfig()
    app.mainW.storeConfig()
