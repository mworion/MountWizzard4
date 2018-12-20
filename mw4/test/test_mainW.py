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
          'build': 'test',
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


def test_updateGuiCyclic():
    suc = app.mainW.updateGUI()
    assert suc

#
#
# testing mainW gui fw
#
#


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
# testing mainW gui pointing
#
#


def test_updatePointGui_alt():
    value = '45'
    app.mount.obsSite.Alt = value
    app.mainW.updatePointGUI()
    assert '45.00' == app.mainW.ui.ALT.text()
    value = None
    app.mount.obsSite.Alt = value
    app.mainW.updatePointGUI()
    assert '-' == app.mainW.ui.ALT.text()


def test_updatePointGui_az():
    value = '45'
    app.mount.obsSite.Az = value
    app.mainW.updatePointGUI()
    assert '45.00' == app.mainW.ui.AZ.text()
    value = None
    app.mount.obsSite.Az = value
    app.mainW.updatePointGUI()
    assert '-' == app.mainW.ui.AZ.text()


def test_updatePointGui_ra():
    value = '45'
    app.mount.obsSite.raJNow = value
    app.mainW.updatePointGUI()
    assert '45:00:00' == app.mainW.ui.RA.text()
    value = None
    app.mount.obsSite.raJNow = value
    app.mainW.updatePointGUI()
    assert '-' == app.mainW.ui.RA.text()


def test_updatePointGui_dec():
    value = '45'
    app.mount.obsSite.decJNow = value
    app.mainW.updatePointGUI()
    assert '+45:00:00' == app.mainW.ui.DEC.text()
    value = None
    app.mount.obsSite.decJNow = value
    app.mainW.updatePointGUI()
    assert '-' == app.mainW.ui.DEC.text()


def test_updatePointGui_jd1():
    value = '2451544.5'
    app.mount.obsSite.utc_ut1 = '0'
    app.mount.obsSite.timeJD = value
    app.mainW.updatePointGUI()
    assert '00:00:00' == app.mainW.ui.timeJD.text()


def test_updatePointGui_jd2():
    value = None
    app.mount.obsSite.timeJD = value
    app.mainW.updatePointGUI()
    assert '-' == app.mainW.ui.timeJD.text()


def test_updatePointGui_pierside():
    value = 'W'
    app.mount.obsSite.pierside = value
    app.mainW.updatePointGUI()
    assert 'WEST' == app.mainW.ui.pierside.text()
    value = None
    app.mount.obsSite.pierside = value
    app.mainW.updatePointGUI()
    assert '-' == app.mainW.ui.pierside.text()


def test_updatePointGui_sidereal():
    value = '45:45:45'
    app.mount.obsSite.timeSidereal = value
    app.mainW.updatePointGUI()
    assert '45:45:45' == app.mainW.ui.timeSidereal.text()
    value = None
    app.mount.obsSite.timeSidereal = value
    app.mainW.updatePointGUI()
    assert '-' == app.mainW.ui.timeSidereal.text()


def test_updatePointGui_statusText():
    app.mount.obsSite.status = 6
    app.mainW.updatePointGUI()
    assert 'Slewing or going to stop' == app.mainW.ui.statusText.text()
    app.mount.obsSite.status = None
    app.mainW.updatePointGUI()
    assert '-' == app.mainW.ui.statusText.text()

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


def test_updateSetting_UTCExpire():
    value = '2020-10-05'
    app.mount.sett.UTCExpire = value
    app.mainW.updateSettingGUI()
    assert value == app.mainW.ui.UTCExpire.text()
    value = None
    app.mount.sett.UTCExpire = value
    app.mainW.updateSettingGUI()
    assert '-' == app.mainW.ui.UTCExpire.text()


def test_updateSetting_UTCExpire1():
    value = '2016-10-05'
    app.mount.sett.UTCExpire = value
    app.mainW.updateSettingGUI()
    assert value == app.mainW.ui.UTCExpire.text()
    value = None
    app.mount.sett.UTCExpire = value
    app.mainW.updateSettingGUI()
    assert '-' == app.mainW.ui.UTCExpire.text()


def test_updateSetting_UTCExpire2():
    value = '2018-10-05'
    app.mount.sett.UTCExpire = value
    app.mainW.updateSettingGUI()
    assert value == app.mainW.ui.UTCExpire.text()
    value = None
    app.mount.sett.UTCExpire = value
    app.mainW.updateSettingGUI()
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
    app.mainW.updateSettingGUI()
    assert 'ON' == app.mainW.ui.statusUnattendedFlip.text()
    value = None
    app.mount.sett.statusUnattendedFlip = value
    app.mainW.updateSettingGUI()
    assert 'OFF' == app.mainW.ui.statusUnattendedFlip.text()


def test_updateSetting_statusDualTracking():
    value = '1'
    app.mount.sett.statusDualTracking = value
    app.mainW.updateSettingGUI()
    assert 'ON' == app.mainW.ui.statusDualTracking.text()
    value = None
    app.mount.sett.statusDualTracking = value
    app.mainW.updateSettingGUI()
    assert 'OFF' == app.mainW.ui.statusDualTracking.text()


def test_updateSetting_statusRefraction():
    value = '1'
    app.mount.sett.statusRefraction = value
    app.mainW.updateSettingGUI()
    assert 'ON' == app.mainW.ui.statusRefraction.text()
    value = None
    app.mount.sett.statusRefraction = value
    app.mainW.updateSettingGUI()
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


def test_updateSetting_location():

    app.mount.obsSite.location = ['49:00:00', '11:00:00', '500']
    app.mainW.updateSettingGUI()
    assert '11deg 00\' 00.0\"' == app.mainW.ui.siteLongitude.text()
    assert '49deg 00\' 00.0\"' == app.mainW.ui.siteLatitude.text()
    assert '500.0' == app.mainW.ui.siteElevation.text()

    app.mount.obsSite.location = None
    app.mainW.updateSettingGUI()
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

#
#
# testing mainW gui AlignGui
#
#


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


def test_setupRelayGui(qtbot):
    suc = app.mainW.setupRelayGui()
    assert suc
    assert 8 == len(app.mainW.relayDropDown)
    assert 8 == len(app.mainW.relayText)
    assert 8 == len(app.mainW.relayButton)
    for dropDown in app.mainW.relayDropDown:
        val = dropDown.count()
        assert 2 == val


def test_updateRelayGui(qtbot):
    app.relay.status = [0, 1, 0, 1, 0, 1, 0, 1]
    suc = app.mainW.updateRelayGui()
    assert suc


def test_toggleRelay1(qtbot):
    app.mainW.ui.checkEnableRelay.setChecked(False)
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.toggleRelay()
        assert not suc
    assert ['Relay box off', 2] == blocker.args


def test_toggleRelay2(qtbot):
    app.mainW.ui.checkEnableRelay.setChecked(True)
    with mock.patch.object(app.relay,
                           'switch',
                           return_value=False):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.toggleRelay()
            assert not suc
        assert ['Relay cannot be switched', 2] == blocker.args


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
