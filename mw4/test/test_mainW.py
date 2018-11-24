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
# Python  v3.6.5
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
          'configDir': './mw4/test/config/',
          'build': 'test',
          }
test_app = mainApp.MountWizzard4(mwGlob=mwGlob)
spy = PyQt5.QtTest.QSignalSpy(test_app.message)


#
#
# testing mainW gui booting shutdown
#
#


def test_mountBoot1(qtbot):
    with mock.patch.object(test_app.mount,
                           'bootMount',
                           return_value=True):
        with qtbot.waitSignal(test_app.message) as blocker:
            suc = test_app.mainW.mountBoot()
            assert suc
        assert ['Mount booted', 0] == blocker.args


def test_mountBoot2(qtbot):
    with mock.patch.object(test_app.mount,
                           'bootMount',
                           return_value=False):
        with qtbot.waitSignal(test_app.message) as blocker:
            suc = test_app.mainW.mountBoot()
            assert not suc
        assert ['Mount cannot be booted', 2] == blocker.args


def test_mountShutdown1(qtbot):
    with mock.patch.object(test_app.mount.obsSite,
                           'shutdown',
                           return_value=True):
        with qtbot.waitSignal(test_app.message) as blocker:
            suc = test_app.mainW.mountShutdown()
            assert suc
        assert ['Shutting mount down', 0] == blocker.args


def test_mountShutdown2(qtbot):
    with mock.patch.object(test_app.mount.obsSite,
                           'shutdown',
                           return_value=False):
        with qtbot.waitSignal(test_app.message) as blocker:
            suc = test_app.mainW.mountShutdown()
            assert not suc
        assert ['Mount cannot be shutdown', 2] == blocker.args


#
#
# testing mainW gui updateMountConnStat
#
#


def test_updateMountConnStat():
    suc = test_app.mainW.updateMountConnStat(True)
    assert suc
    assert 'green' == test_app.mainW.ui.mountConnected.property('color')
    suc = test_app.mainW.updateMountConnStat(False)
    assert suc
    assert 'red' == test_app.mainW.ui.mountConnected.property('color')

#
#
# testing mainW gui update Gui
#
#


def test_updateGuiCyclic():
    suc = test_app.mainW.updateGUICyclic()
    assert suc

#
#
# testing mainW gui fw
#
#


def test_updateFwGui_productName():
    value = 'Test1234'
    test_app.mount.fw.productName = value
    test_app.mainW.updateFwGui()
    assert value == test_app.mainW.ui.productName.text()
    value = None
    test_app.mount.fw.productName = value
    test_app.mainW.updateFwGui()
    assert '-' == test_app.mainW.ui.productName.text()


def test_updateFwGui_hwVersion():
    value = 'Test1234'
    test_app.mount.fw.hwVersion = value
    test_app.mainW.updateFwGui()
    assert value == test_app.mainW.ui.hwVersion.text()
    value = None
    test_app.mount.fw.hwVersion = value
    test_app.mainW.updateFwGui()
    assert '-' == test_app.mainW.ui.hwVersion.text()


def test_updateFwGui_numberString():
    value = '2.15.18'
    test_app.mount.fw.numberString = value
    test_app.mainW.updateFwGui()
    assert value == test_app.mainW.ui.numberString.text()
    value = None
    test_app.mount.fw.numberString = value
    test_app.mainW.updateFwGui()
    assert '-' == test_app.mainW.ui.numberString.text()


def test_updateFwGui_fwdate():
    value = 'Test1234'
    test_app.mount.fw.fwdate = value
    test_app.mainW.updateFwGui()
    assert value == test_app.mainW.ui.fwdate.text()
    value = None
    test_app.mount.fw.fwdate = value
    test_app.mainW.updateFwGui()
    assert '-' == test_app.mainW.ui.fwdate.text()


def test_updateFwGui_fwtime():
    value = 'Test1234'
    test_app.mount.fw.fwtime = value
    test_app.mainW.updateFwGui()
    assert value == test_app.mainW.ui.fwtime.text()
    value = None
    test_app.mount.fw.fwtime = value
    test_app.mainW.updateFwGui()
    assert '-' == test_app.mainW.ui.fwtime.text()

#
#
# testing mainW gui model name
#
#


def test_setNameList():
    value = ['Test1', 'test2', 'test3', 'test4']
    test_app.mount.model.nameList = value
    test_app.mainW.setNameList()
    assert 4 == test_app.mainW.ui.nameList.count()
    value = None
    test_app.mount.model.nameList = value
    test_app.mainW.setNameList()
    assert 0 == test_app.mainW.ui.nameList.count()

#
#
# testing mainW gui pointing
#
#


def test_updatePointGui_alt():
    value = '45'
    test_app.mount.obsSite.Alt = value
    test_app.mainW.updatePointGUI()
    assert '45.00' == test_app.mainW.ui.ALT.text()
    value = None
    test_app.mount.obsSite.Alt = value
    test_app.mainW.updatePointGUI()
    assert '-' == test_app.mainW.ui.ALT.text()


def test_updatePointGui_az():
    value = '45'
    test_app.mount.obsSite.Az = value
    test_app.mainW.updatePointGUI()
    assert '45.00' == test_app.mainW.ui.AZ.text()
    value = None
    test_app.mount.obsSite.Az = value
    test_app.mainW.updatePointGUI()
    assert '-' == test_app.mainW.ui.AZ.text()


def test_updatePointGui_ra():
    value = '45'
    test_app.mount.obsSite.raJNow = value
    test_app.mainW.updatePointGUI()
    assert '45:00:00' == test_app.mainW.ui.RA.text()
    value = None
    test_app.mount.obsSite.raJNow = value
    test_app.mainW.updatePointGUI()
    assert '-' == test_app.mainW.ui.RA.text()


def test_updatePointGui_dec():
    value = '45'
    test_app.mount.obsSite.decJNow = value
    test_app.mainW.updatePointGUI()
    assert '+45:00:00' == test_app.mainW.ui.DEC.text()
    value = None
    test_app.mount.obsSite.decJNow = value
    test_app.mainW.updatePointGUI()
    assert '-' == test_app.mainW.ui.DEC.text()


def test_updatePointGui_jd():
    value = '45'
    test_app.mount.obsSite.timeJD = value
    test_app.mainW.updatePointGUI()
    assert '11:59:18' == test_app.mainW.ui.timeJD.text()
    value = None
    test_app.mount.obsSite.timeJD = value
    test_app.mainW.updatePointGUI()
    assert '-' == test_app.mainW.ui.timeJD.text()


def test_updatePointGui_pierside():
    value = 'W'
    test_app.mount.obsSite.pierside = value
    test_app.mainW.updatePointGUI()
    assert 'WEST' == test_app.mainW.ui.pierside.text()
    value = None
    test_app.mount.obsSite.pierside = value
    test_app.mainW.updatePointGUI()
    assert '-' == test_app.mainW.ui.pierside.text()


def test_updatePointGui_sidereal():
    value = '45:45:45'
    test_app.mount.obsSite.timeSidereal = value
    test_app.mainW.updatePointGUI()
    assert '45:45:45' == test_app.mainW.ui.timeSidereal.text()
    value = None
    test_app.mount.obsSite.timeSidereal = value
    test_app.mainW.updatePointGUI()
    assert '-' == test_app.mainW.ui.timeSidereal.text()


def test_updatePointGui_statusText():
    test_app.mount.obsSite.status = 6
    test_app.mainW.updatePointGUI()
    assert 'Slewing or going to stop' == test_app.mainW.ui.statusText.text()
    test_app.mount.obsSite.status = None
    test_app.mainW.updatePointGUI()
    assert '-' == test_app.mainW.ui.statusText.text()

#
#
# testing mainW gui setting
#
#


def test_updateSetting_slewRate():
    value = '15'
    test_app.mount.sett.slewRate = value
    test_app.mainW.updateSettingGUI()
    assert '15' == test_app.mainW.ui.slewRate.text()
    value = None
    test_app.mount.sett.slewRate = value
    test_app.mainW.updateSettingGUI()
    assert '-' == test_app.mainW.ui.slewRate.text()


def test_updateSetting_timeToFlip():
    value = '15'
    test_app.mount.sett.timeToFlip = value
    test_app.mainW.updateSettingGUI()
    assert ' 15' == test_app.mainW.ui.timeToFlip.text()
    value = None
    test_app.mount.sett.timeToFlip = value
    test_app.mainW.updateSettingGUI()
    assert '-' == test_app.mainW.ui.timeToFlip.text()


def test_updateSetting_UTCExpire():
    value = '2020-10-05'
    test_app.mount.sett.UTCExpire = value
    test_app.mainW.updateSettingGUI()
    assert value == test_app.mainW.ui.UTCExpire.text()
    value = None
    test_app.mount.sett.UTCExpire = value
    test_app.mainW.updateSettingGUI()
    assert '-' == test_app.mainW.ui.UTCExpire.text()


def test_updateSetting_UTCExpire1():
    value = '2016-10-05'
    test_app.mount.sett.UTCExpire = value
    test_app.mainW.updateSettingGUI()
    assert value == test_app.mainW.ui.UTCExpire.text()
    value = None
    test_app.mount.sett.UTCExpire = value
    test_app.mainW.updateSettingGUI()
    assert '-' == test_app.mainW.ui.UTCExpire.text()


def test_updateSetting_UTCExpire2():
    value = '2018-10-05'
    test_app.mount.sett.UTCExpire = value
    test_app.mainW.updateSettingGUI()
    assert value == test_app.mainW.ui.UTCExpire.text()
    value = None
    test_app.mount.sett.UTCExpire = value
    test_app.mainW.updateSettingGUI()
    assert '-' == test_app.mainW.ui.UTCExpire.text()


def test_updateSetting_refractionTemp():
    value = '15'
    test_app.mount.sett.refractionTemp = value
    test_app.mainW.updateSettingGUI()
    assert '+15.0' == test_app.mainW.ui.refractionTemp.text()
    assert '+15.0' == test_app.mainW.ui.refractionTemp1.text()
    value = None
    test_app.mount.sett.refractionTemp = value
    test_app.mainW.updateSettingGUI()
    assert '-' == test_app.mainW.ui.refractionTemp.text()
    assert '-' == test_app.mainW.ui.refractionTemp1.text()


def test_updateSetting_refractionPress():
    value = '1050.0'
    test_app.mount.sett.refractionPress = value
    test_app.mainW.updateSettingGUI()
    assert value == test_app.mainW.ui.refractionPress.text()
    assert value == test_app.mainW.ui.refractionPress1.text()
    value = None
    test_app.mount.sett.refractionPress = value
    test_app.mainW.updateSettingGUI()
    assert '-' == test_app.mainW.ui.refractionPress.text()
    assert '-' == test_app.mainW.ui.refractionPress1.text()


def test_updateSetting_statusUnattendedFlip():
    value = '1'
    test_app.mount.sett.statusUnattendedFlip = value
    test_app.mainW.updateSettingGUI()
    assert 'ON' == test_app.mainW.ui.statusUnattendedFlip.text()
    value = None
    test_app.mount.sett.statusUnattendedFlip = value
    test_app.mainW.updateSettingGUI()
    assert 'OFF' == test_app.mainW.ui.statusUnattendedFlip.text()


def test_updateSetting_statusDualTracking():
    value = '1'
    test_app.mount.sett.statusDualTracking = value
    test_app.mainW.updateSettingGUI()
    assert 'ON' == test_app.mainW.ui.statusDualTracking.text()
    value = None
    test_app.mount.sett.statusDualTracking = value
    test_app.mainW.updateSettingGUI()
    assert 'OFF' == test_app.mainW.ui.statusDualTracking.text()


def test_updateSetting_statusRefraction():
    value = '1'
    test_app.mount.sett.statusRefraction = value
    test_app.mainW.updateSettingGUI()
    assert 'ON' == test_app.mainW.ui.statusRefraction.text()
    value = None
    test_app.mount.sett.statusRefraction = value
    test_app.mainW.updateSettingGUI()
    assert 'OFF' == test_app.mainW.ui.statusRefraction.text()


def test_updateSetting_meridianLimitTrack():
    value = '15'
    test_app.mount.sett.meridianLimitTrack = value
    test_app.mainW.updateSettingGUI()
    assert '15.0' == test_app.mainW.ui.meridianLimitTrack.text()
    value = None
    test_app.mount.sett.meridianLimitTrack = value
    test_app.mainW.updateSettingGUI()
    assert '-' == test_app.mainW.ui.meridianLimitTrack.text()


def test_updateSetting_meridianLimitSlew():
    value = '15'
    test_app.mount.sett.meridianLimitSlew = value
    test_app.mainW.updateSettingGUI()
    assert '15.0' == test_app.mainW.ui.meridianLimitSlew.text()
    value = None
    test_app.mount.sett.meridianLimitSlew = value
    test_app.mainW.updateSettingGUI()
    assert '-' == test_app.mainW.ui.meridianLimitSlew.text()


def test_updateSetting_horizonLimitLow():
    value = '0'
    test_app.mount.sett.horizonLimitLow = value
    test_app.mainW.updateSettingGUI()
    assert '0.0' == test_app.mainW.ui.horizonLimitLow.text()
    value = None
    test_app.mount.sett.horizonLimitLow = value
    test_app.mainW.updateSettingGUI()
    assert '-' == test_app.mainW.ui.horizonLimitLow.text()


def test_updateSetting_horizonLimitHigh():
    value = '50'
    test_app.mount.sett.horizonLimitHigh = value
    test_app.mainW.updateSettingGUI()
    assert '50.0' == test_app.mainW.ui.horizonLimitHigh.text()
    value = None
    test_app.mount.sett.horizonLimitHigh = value
    test_app.mainW.updateSettingGUI()
    assert '-' == test_app.mainW.ui.horizonLimitHigh.text()


def test_updateSetting_timeToMeridian():
    test_app.mount.sett.timeToFlip = '100'
    test_app.mount.sett.meridianLimitTrack = '15'

    test_app.mainW.updateSettingGUI()
    assert ' 40' == test_app.mainW.ui.timeToMeridian.text()
    value = None
    test_app.mount.sett.timeToFlip = value
    test_app.mount.sett.meridianLimitTrack = value
    test_app.mainW.updateSettingGUI()
    assert '-' == test_app.mainW.ui.timeToMeridian.text()


def test_updateSetting_location():

    test_app.mount.obsSite.location = ['49:00:00', '11:00:00', '500']
    test_app.mainW.updateSettingGUI()
    assert '11deg 00\' 00.0\"' == test_app.mainW.ui.siteLongitude.text()
    assert '49deg 00\' 00.0\"' == test_app.mainW.ui.siteLatitude.text()
    assert '500.0' == test_app.mainW.ui.siteElevation.text()

    test_app.mount.obsSite.location = None
    test_app.mainW.updateSettingGUI()
    assert '-' == test_app.mainW.ui.siteLongitude.text()
    assert '-' == test_app.mainW.ui.siteLatitude.text()
    assert '-' == test_app.mainW.ui.siteElevation.text()


def test_tracking_speed1():
    with mock.patch.object(test_app.mount.sett,
                           'checkRateLunar',
                           return_value=True):
        suc = test_app.mainW.updateSettingGUI()
        assert suc


def test_tracking_speed2():
    with mock.patch.object(test_app.mount.sett,
                           'checkRateSidereal',
                           return_value=True):
        suc = test_app.mainW.updateSettingGUI()
        assert suc


def test_tracking_speed3():
    with mock.patch.object(test_app.mount.sett,
                           'checkRateSolar',
                           return_value=True):
        suc = test_app.mainW.updateSettingGUI()
        assert suc


#
#
# testing mainW gui AlignGui
#
#


def test_updateAlignGui_numberStars():
    with mock.patch.object(test_app.mainW, 'showModelPolar') as mMock:
        mMock.return_value.showModelPolar.return_value = None

        value = '50'
        test_app.mount.model.numberStars = value
        test_app.mainW.updateAlignGUI()
        assert '50' == test_app.mainW.ui.numberStars.text()
        assert '50' == test_app.mainW.ui.numberStars1.text()
        value = None
        test_app.mount.model.numberStars = value
        test_app.mainW.updateAlignGUI()
        assert '-' == test_app.mainW.ui.numberStars.text()
        assert '-' == test_app.mainW.ui.numberStars1.text()


def test_updateAlignGui_altitudeError():
    with mock.patch.object(test_app.mainW, 'showModelPolar') as mMock:
        mMock.return_value.showModelPolar.return_value = None

        value = '50'
        test_app.mount.model.altitudeError = value
        test_app.mainW.updateAlignGUI()
        assert '50deg 00\' 00.0\"' == test_app.mainW.ui.altitudeError.text()
        value = None
        test_app.mount.model.altitudeError = value
        test_app.mainW.updateAlignGUI()
        assert '-' == test_app.mainW.ui.altitudeError.text()


def test_updateAlignGui_errorRMS():
    with mock.patch.object(test_app.mainW, 'showModelPolar') as mMock:
        mMock.return_value.showModelPolar.return_value = None

        value = '50'
        test_app.mount.model.errorRMS = value
        test_app.mainW.updateAlignGUI()
        assert '50.0' == test_app.mainW.ui.errorRMS.text()
        assert '50.0' == test_app.mainW.ui.errorRMS1.text()
        value = None
        test_app.mount.model.errorRMS = value
        test_app.mainW.updateAlignGUI()
        assert '-' == test_app.mainW.ui.errorRMS.text()
        assert '-' == test_app.mainW.ui.errorRMS1.text()


def test_updateAlignGui_azimuthError():
    with mock.patch.object(test_app.mainW, 'showModelPolar') as mMock:
        mMock.return_value.showModelPolar.return_value = None

        value = '50'
        test_app.mount.model.azimuthError = value
        test_app.mainW.updateAlignGUI()
        assert '50deg 00\' 00.0\"' == test_app.mainW.ui.azimuthError.text()
        value = None
        test_app.mount.model.azimuthError = value
        test_app.mainW.updateAlignGUI()
        assert '-' == test_app.mainW.ui.azimuthError.text()


def test_updateAlignGui_terms():
    with mock.patch.object(test_app.mainW, 'showModelPolar') as mMock:
        mMock.return_value.showModelPolar.return_value = None

        value = '50'
        test_app.mount.model.terms = value
        test_app.mainW.updateAlignGUI()
        assert '50.0' == test_app.mainW.ui.terms.text()
        value = None
        test_app.mount.model.terms = value
        test_app.mainW.updateAlignGUI()
        assert '-' == test_app.mainW.ui.terms.text()


def test_updateAlignGui_orthoError():
    with mock.patch.object(test_app.mainW, 'showModelPolar') as mMock:
        mMock.return_value.showModelPolar.return_value = None

        value = '50'
        test_app.mount.model.orthoError = value
        test_app.mainW.updateAlignGUI()
        assert '50deg 00\' 00.0\"' == test_app.mainW.ui.orthoError.text()
        value = None
        test_app.mount.model.orthoError = value
        test_app.mainW.updateAlignGUI()
        assert '-' == test_app.mainW.ui.orthoError.text()


def test_updateAlignGui_positionAngle():
    with mock.patch.object(test_app.mainW, 'showModelPolar') as mMock:
        mMock.return_value.showModelPolar.return_value = None

        value = '50'
        test_app.mount.model.positionAngle = value
        test_app.mainW.updateAlignGUI()
        assert ' 50.0' == test_app.mainW.ui.positionAngle.text()
        value = None
        test_app.mount.model.positionAngle = value
        test_app.mainW.updateAlignGUI()
        assert '-' == test_app.mainW.ui.positionAngle.text()


def test_updateAlignGui_polarError():
    with mock.patch.object(test_app.mainW, 'showModelPolar') as mMock:
        mMock.return_value.showModelPolar.return_value = None

        value = '50'
        test_app.mount.model.polarError = value
        test_app.mainW.updateAlignGUI()
        assert '50deg 00\' 00.0\"' == test_app.mainW.ui.polarError.text()
        value = None
        test_app.mount.model.polarError = value
        test_app.mainW.updateAlignGUI()
        assert '-' == test_app.mainW.ui.polarError.text()

#
#
# testing mainW gui AlignGui
#
#


def test_closeEvent():

    test_app.mainW.showStatus = True
    test_app.mainW.closeEvent(1)

    assert not test_app.mainW.showStatus

#
#
# testing mainW gui model polar
#
#


def test_showModelPolar1():
    test_app.mount.obsSite.location = ['49:00:00', '11:00:00', '580']
    test_app.mount.model._parseStars(['21:52:58.95,+08*56:10.1,   5.7,201',
                                      '21:06:10.79,+45*20:52.8,  12.1,329',
                                      '23:13:58.02,+38*48:18.8,  31.0,162',
                                      '17:43:41.26,+59*15:30.7,   8.4,005',
                                      ],
                                     4)
    test_app.mainW.ui.checkShowErrorValues.setChecked(True)
    suc = test_app.mainW.showModelPolar()
    assert suc


def test_showModelPolar2():
    test_app.mount.obsSite.location = ['49:00:00', '11:00:00', '580']
    test_app.mainW.ui.checkShowErrorValues.setChecked(True)
    suc = test_app.mainW.showModelPolar()
    assert suc


def test_showModelPolar3():
    test_app.mainW.ui.checkShowErrorValues.setChecked(True)
    suc = test_app.mainW.showModelPolar()
    assert suc

#
#
# testing mainW gui change tracking
#
#


def test_changeTracking_ok1(qtbot):
    test_app.mount.obsSite.status = 0
    with mock.patch.object(test_app.mount.obsSite,
                           'stopTracking',
                           return_value=False):
        with qtbot.waitSignal(test_app.message) as blocker:
            suc = test_app.mainW.changeTracking()
            assert suc
        assert ['Cannot stop tracking', 2] == blocker.args


def test_changeTracking_ok2(qtbot):
    test_app.mount.obsSite.status = 0
    with mock.patch.object(test_app.mount.obsSite,
                           'stopTracking',
                           return_value=True):
        with qtbot.waitSignal(test_app.message) as blocker:
            suc = test_app.mainW.changeTracking()
            assert suc
        assert ['Stopped tracking', 0] == blocker.args


def test_changeTracking_ok3(qtbot):
    test_app.mount.obsSite.status = 1
    with mock.patch.object(test_app.mount.obsSite,
                           'startTracking',
                           return_value=False):
        with qtbot.waitSignal(test_app.message) as blocker:
            suc = test_app.mainW.changeTracking()
            assert suc
        assert ['Cannot start tracking', 2] == blocker.args


def test_changeTracking_ok4(qtbot):
    test_app.mount.obsSite.status = 1
    with mock.patch.object(test_app.mount.obsSite,
                           'startTracking',
                           return_value=True):
        with qtbot.waitSignal(test_app.message) as blocker:
            suc = test_app.mainW.changeTracking()
            assert suc
        assert ['Started tracking', 0] == blocker.args


def test_changePark_ok1(qtbot):
    test_app.mount.obsSite.status = 5
    with mock.patch.object(test_app.mount.obsSite,
                           'unpark',
                           return_value=False):
        with qtbot.waitSignal(test_app.message) as blocker:
            suc = test_app.mainW.changePark()
            assert suc
        assert ['Cannot unpark mount', 2] == blocker.args


def test_changePark_ok2(qtbot):
    test_app.mount.obsSite.status = 5
    with mock.patch.object(test_app.mount.obsSite,
                           'unpark',
                           return_value=True):
        with qtbot.waitSignal(test_app.message) as blocker:
            suc = test_app.mainW.changePark()
            assert suc
        assert ['Mount unparked', 0] == blocker.args


def test_changePark_ok3(qtbot):
    test_app.mount.obsSite.status = 1
    with mock.patch.object(test_app.mount.obsSite,
                           'park',
                           return_value=False):
        with qtbot.waitSignal(test_app.message) as blocker:
            suc = test_app.mainW.changePark()
            assert suc
        assert ['Cannot park mount', 2] == blocker.args


def test_changePark_ok4(qtbot):
    test_app.mount.obsSite.status = 1
    with mock.patch.object(test_app.mount.obsSite,
                           'park',
                           return_value=True):
        with qtbot.waitSignal(test_app.message) as blocker:
            suc = test_app.mainW.changePark()
            assert suc
        assert ['Mount parked', 0] == blocker.args


def test_saveProfile1(qtbot):
    with mock.patch.object(test_app,
                           'saveConfig',
                           return_value=True):
        with qtbot.waitSignal(test_app.message) as blocker:
            test_app.mainW.saveProfile()
        assert ['Actual profile saved', 0] == blocker.args


def test_loadProfile1(qtbot):
    with mock.patch.object(test_app.mainW,
                           'openFile',
                           return_value=('config', 'test', 'cfg')):
        with mock.patch.object(test_app,
                               'loadConfig',
                               return_value=True):
            with qtbot.waitSignal(test_app.message) as blocker:
                suc = test_app.mainW.loadProfile()
                assert suc
            assert ['Profile: [test] loaded', 0] == blocker.args


def test_loadProfile2(qtbot):
    with mock.patch.object(test_app.mainW,
                           'openFile',
                           return_value=('config', 'test', 'cfg')):
        with mock.patch.object(test_app,
                               'loadConfig',
                               return_value=False):
            with qtbot.waitSignal(test_app.message) as blocker:
                suc = test_app.mainW.loadProfile()
                assert suc
            assert ['Profile: [test] cannot no be loaded', 2] == blocker.args


def test_loadProfile3(qtbot):
    with mock.patch.object(test_app.mainW,
                           'openFile',
                           return_value=(None, 'test', 'cfg')):
        suc = test_app.mainW.loadProfile()
        assert not suc


def test_saveProfileAs1(qtbot):
    with mock.patch.object(test_app.mainW,
                           'saveFile',
                           return_value=('config', 'test', 'cfg')):
        with mock.patch.object(test_app,
                               'saveConfig',
                               return_value=True):
            with qtbot.waitSignal(test_app.message) as blocker:
                suc = test_app.mainW.saveProfileAs()
                assert suc
            assert ['Profile: [test] saved', 0] == blocker.args


def test_saveProfileAs2(qtbot):
    with mock.patch.object(test_app.mainW,
                           'saveFile',
                           return_value=('config', 'test', 'cfg')):
        with mock.patch.object(test_app,
                               'saveConfig',
                               return_value=False):
            with qtbot.waitSignal(test_app.message) as blocker:
                suc = test_app.mainW.saveProfileAs()
                assert suc
            assert ['Profile: [test] cannot no be saved', 2] == blocker.args


def test_saveProfileAs3(qtbot):
    with mock.patch.object(test_app.mainW,
                           'saveFile',
                           return_value=(None, 'test', 'cfg')):
        suc = test_app.mainW.saveProfileAs()
        assert not suc


def test_saveProfile2(qtbot):
    with mock.patch.object(test_app,
                           'saveConfig',
                           return_value=False):
        with qtbot.waitSignal(test_app.message) as blocker:
            test_app.mainW.saveProfile()
        assert ['Actual profile cannot not be saved', 2] == blocker.args


def test_setLoggingLevel1(qtbot):
    test_app.mainW.ui.loglevelDebug.setChecked(True)
    test_app.mainW.setLoggingLevel()
    val = logging.getLogger().getEffectiveLevel()
    assert val == 10


def test_setLoggingLevel2(qtbot):
    test_app.mainW.ui.loglevelInfo.setChecked(True)
    test_app.mainW.setLoggingLevel()
    val = logging.getLogger().getEffectiveLevel()
    assert val == 20


def test_setLoggingLevel3(qtbot):
    test_app.mainW.ui.loglevelWarning.setChecked(True)
    test_app.mainW.setLoggingLevel()
    val = logging.getLogger().getEffectiveLevel()
    assert val == 30


def test_setLoggingLevel4(qtbot):
    test_app.mainW.ui.loglevelError.setChecked(True)
    test_app.mainW.setLoggingLevel()
    val = logging.getLogger().getEffectiveLevel()
    assert val == 40


def test_setLunarTracking1(qtbot):
    with mock.patch.object(test_app.mount.obsSite,
                           'setLunarTracking',
                           return_value=True):
        with qtbot.waitSignal(test_app.message) as blocker:
            suc = test_app.mainW.setLunarTracking()
            assert suc
        assert ['Tracking set to Lunar', 0] == blocker.args


def test_setLunarTracking2(qtbot):
    with mock.patch.object(test_app.mount.obsSite,
                           'setLunarTracking',
                           return_value=False):
        with qtbot.waitSignal(test_app.message) as blocker:
            suc = test_app.mainW.setLunarTracking()
            assert not suc
        assert ['Cannot set tracking to Lunar', 2] == blocker.args


def test_setSiderealTracking1(qtbot):
    with mock.patch.object(test_app.mount.obsSite,
                           'setSiderealTracking',
                           return_value=True):
        with qtbot.waitSignal(test_app.message) as blocker:
            suc = test_app.mainW.setSiderealTracking()
            assert suc
        assert ['Tracking set to Sidereal', 0] == blocker.args


def test_setSiderealTracking2(qtbot):
    with mock.patch.object(test_app.mount.obsSite,
                           'setSiderealTracking',
                           return_value=False):
        with qtbot.waitSignal(test_app.message) as blocker:
            suc = test_app.mainW.setSiderealTracking()
            assert not suc
        assert ['Cannot set tracking to Sidereal', 2] == blocker.args


def test_setSolarTracking1(qtbot):
    with mock.patch.object(test_app.mount.obsSite,
                           'setSolarTracking',
                           return_value=True):
        with qtbot.waitSignal(test_app.message) as blocker:
            suc = test_app.mainW.setSolarTracking()
            assert suc
        assert ['Tracking set to Solar', 0] == blocker.args


def test_setSolarTracking2(qtbot):
    with mock.patch.object(test_app.mount.obsSite,
                           'setSolarTracking',
                           return_value=False):
        with qtbot.waitSignal(test_app.message) as blocker:
            suc = test_app.mainW.setSolarTracking()
            assert not suc
        assert ['Cannot set tracking to Solar', 2] == blocker.args


def test_setMeridianLimitTrack1(qtbot):
    test_app.mount.sett.meridianLimitTrack = None
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'critical',
                           return_value=True):
        suc = test_app.mainW.setMeridianLimitTrack()
        assert not suc


def test_setMeridianLimitTrack2(qtbot):
    test_app.mount.sett.meridianLimitTrack = 10
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, True)):
        suc = test_app.mainW.setMeridianLimitTrack()
        assert not suc


def test_setMeridianLimitTrack3(qtbot):
    test_app.mount.sett.meridianLimitTrack = 10
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, False)):
        suc = test_app.mainW.setMeridianLimitTrack()
        assert not suc


def test_setMeridianLimitTrack4(qtbot):
    test_app.mount.sett.meridianLimitTrack = 10
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, True)):
        with mock.patch.object(test_app.mount.obsSite,
                               'setMeridianLimitTrack',
                               return_value=True):
            suc = test_app.mainW.setMeridianLimitTrack()
            assert suc


def test_setMeridianLimitSlew1(qtbot):
    test_app.mount.sett.meridianLimitSlew = None
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'critical',
                           return_value=True):
        suc = test_app.mainW.setMeridianLimitSlew()
        assert not suc


def test_setMeridianLimitSlew2(qtbot):
    test_app.mount.sett.meridianLimitSlew = 10
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, True)):
        suc = test_app.mainW.setMeridianLimitSlew()
        assert not suc


def test_setMeridianLimitSlew3(qtbot):
    test_app.mount.sett.meridianLimitSlew = 10
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, False)):
        suc = test_app.mainW.setMeridianLimitSlew()
        assert not suc


def test_setMeridianLimitSlew4(qtbot):
    test_app.mount.sett.meridianLimitSlew = 10
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, True)):
        with mock.patch.object(test_app.mount.obsSite,
                               'setMeridianLimitSlew',
                               return_value=True):
            suc = test_app.mainW.setMeridianLimitSlew()
            assert suc


def test_setHorizonLimitHigh1(qtbot):
    test_app.mount.sett.horizonLimitHigh = None
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'critical',
                           return_value=True):
        suc = test_app.mainW.setHorizonLimitHigh()
        assert not suc


def test_setHorizonLimitHigh2(qtbot):

    test_app.mount.sett.horizonLimitHigh = 10

    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, True)):
        suc = test_app.mainW.setHorizonLimitHigh()
        assert not suc


def test_setHorizonLimitHigh3(qtbot):
    test_app.mount.sett.horizonLimitHigh = 10
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, False)):
        suc = test_app.mainW.setHorizonLimitHigh()
        assert not suc


def test_setHorizonLimitHigh4(qtbot):
    test_app.mount.sett.horizonLimitHigh = 10
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, True)):
        with mock.patch.object(test_app.mount.obsSite,
                               'setHorizonLimitHigh',
                               return_value=True):
            suc = test_app.mainW.setHorizonLimitHigh()
            assert suc


def test_setHorizonLimitLow1(qtbot):
    test_app.mount.sett.horizonLimitLow = None
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'critical',
                           return_value=True):
        suc = test_app.mainW.setHorizonLimitLow()
        assert not suc


def test_setHorizonLimitLow2(qtbot):
    test_app.mount.sett.horizonLimitLow = 10
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, True)):
        suc = test_app.mainW.setHorizonLimitLow()
        assert not suc


def test_setHorizonLimitLow3(qtbot):
    test_app.mount.sett.horizonLimitLow = 10
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, False)):
        suc = test_app.mainW.setHorizonLimitLow()
        assert not suc


def test_setHorizonLimitLow4(qtbot):
    test_app.mount.sett.horizonLimitLow = 10
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, True)):
        with mock.patch.object(test_app.mount.obsSite,
                               'setHorizonLimitLow',
                               return_value=True):
            suc = test_app.mainW.setHorizonLimitLow()
            assert suc


def test_setSlewRate1(qtbot):
    test_app.mount.sett.slewRate = None
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'critical',
                           return_value=True):
        suc = test_app.mainW.setSlewRate()
        assert not suc


def test_setSlewRate2(qtbot):
    test_app.mount.sett.slewRate = 10
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, True)):
        suc = test_app.mainW.setSlewRate()
        assert not suc


def test_setSlewRate3(qtbot):
    test_app.mount.sett.slewRate = 10
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, False)):
        suc = test_app.mainW.setSlewRate()
        assert not suc


def test_setSlewRate4(qtbot):
    test_app.mount.sett.slewRate = 10
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getInt',
                           return_value=(10, True)):
        with mock.patch.object(test_app.mount.obsSite,
                               'setSlewRate',
                               return_value=True):
            suc = test_app.mainW.setSlewRate()
            assert suc


def test_setLongitude1(qtbot):
    test_app.mount.obsSite.location = None
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'critical',
                           return_value=True):
        suc = test_app.mainW.setLongitude()
        assert not suc


def test_setLongitude2(qtbot):
    elev = '999.9'
    lon = '+160*30:45.5'
    lat = '+45*30:45.5'
    test_app.mount.obsSite.location = lat, lon, elev
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getText',
                           return_value=(10, True)):
        suc = test_app.mainW.setLongitude()
        assert not suc


def test_setLongitude3(qtbot):
    elev = '999.9'
    lon = '+160*30:45.5'
    lat = '+45*30:45.5'
    test_app.mount.obsSite.location = lat, lon, elev
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getText',
                           return_value=(10, False)):
        suc = test_app.mainW.setLongitude()
        assert not suc


def test_setLongitude4(qtbot):
    elev = '999.9'
    lon = '+160*30:45.5'
    lat = '+45*30:45.5'
    test_app.mount.obsSite.location = lat, lon, elev
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getText',
                           return_value=(10, True)):
        with mock.patch.object(test_app.mount.obsSite,
                               'setLongitude',
                               return_value=True):
            suc = test_app.mainW.setLongitude()
            assert suc


def test_setLatitude1(qtbot):
    test_app.mount.obsSite.location = None
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'critical',
                           return_value=True):
        suc = test_app.mainW.setLatitude()
        assert not suc


def test_setLatitude2(qtbot):
    elev = '999.9'
    lon = '+160*30:45.5'
    lat = '+45*30:45.5'
    test_app.mount.obsSite.location = lat, lon, elev
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getText',
                           return_value=(10, True)):
        suc = test_app.mainW.setLatitude()
        assert not suc


def test_setLatitude3(qtbot):
    elev = '999.9'
    lon = '+160*30:45.5'
    lat = '+45*30:45.5'
    test_app.mount.obsSite.location = lat, lon, elev
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getText',
                           return_value=(10, False)):
        suc = test_app.mainW.setLatitude()
        assert not suc


def test_setLatitude4(qtbot):
    elev = '999.9'
    lon = '+160*30:45.5'
    lat = '+45*30:45.5'
    test_app.mount.obsSite.location = lat, lon, elev
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getText',
                           return_value=(10, True)):
        with mock.patch.object(test_app.mount.obsSite,
                               'setLatitude',
                               return_value=True):
            suc = test_app.mainW.setLatitude()
            assert suc


def test_setElevation1(qtbot):
    test_app.mount.obsSite.location = None
    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'critical',
                           return_value=True):
        suc = test_app.mainW.setElevation()
        assert not suc


def test_setElevation2(qtbot):
    elev = '999.9'
    lon = '+160*30:45.5'
    lat = '+45*30:45.5'
    test_app.mount.obsSite.location = lat, lon, elev
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getDouble',
                           return_value=(10, True)):
        suc = test_app.mainW.setElevation()
        assert not suc


def test_setElevation3(qtbot):
    elev = '999.9'
    lon = '+160*30:45.5'
    lat = '+45*30:45.5'
    test_app.mount.obsSite.location = lat, lon, elev
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getDouble',
                           return_value=(10, False)):
        suc = test_app.mainW.setElevation()
        assert not suc


def test_setElevation4(qtbot):
    elev = '999.9'
    lon = '+160*30:45.5'
    lat = '+45*30:45.5'
    test_app.mount.obsSite.location = lat, lon, elev
    with mock.patch.object(PyQt5.QtWidgets.QInputDialog,
                           'getDouble',
                           return_value=(10, True)):
        with mock.patch.object(test_app.mount.obsSite,
                               'setElevation',
                               return_value=True):
            suc = test_app.mainW.setElevation()
            assert suc


def test_setupRelayGui(qtbot):
    suc = test_app.mainW.setupRelayGui()
    assert suc
    assert 8 == len(test_app.mainW.relayDropDown)
    assert 8 == len(test_app.mainW.relayText)
    assert 8 == len(test_app.mainW.relayButton)
    for dropDown in test_app.mainW.relayDropDown:
        val = dropDown.count()
        assert 2 == val


def test_updateRelayGui(qtbot):
    test_app.relay.status = [0, 1, 0, 1, 0, 1, 0, 1]
    suc = test_app.mainW.updateRelayGui()
    assert suc


def test_toggleRelay1(qtbot):
    test_app.mainW.ui.checkEnableRelay.setChecked(False)
    with qtbot.waitSignal(test_app.message) as blocker:
        suc = test_app.mainW.toggleRelay()
        assert not suc
    assert ['Relay box off', 2] == blocker.args


def test_toggleRelay2(qtbot):
    test_app.mainW.ui.checkEnableRelay.setChecked(True)
    with mock.patch.object(test_app.relay,
                           'switch',
                           return_value=False):
        with qtbot.waitSignal(test_app.message) as blocker:
            suc = test_app.mainW.toggleRelay()
            assert not suc
        assert ['Relay cannot be switched', 2] == blocker.args


def test_enableRelay1(qtbot):
    test_app.mainW.ui.checkEnableRelay.setChecked(True)
    with mock.patch.object(test_app.relay,
                           'startTimers',
                           return_value=None):
        with qtbot.waitSignal(test_app.message) as blocker:
            suc = test_app.mainW.enableRelay()
            assert suc
        assert ['Relay enabled', 0] == blocker.args


def test_enableRelay2(qtbot):
    test_app.mainW.ui.checkEnableRelay.setChecked(False)
    with mock.patch.object(test_app.relay,
                           'startTimers',
                           return_value=None):
        with qtbot.waitSignal(test_app.message) as blocker:
            suc = test_app.mainW.enableRelay()
            assert suc
        assert ['Relay disabled', 0] == blocker.args


def test_relayHost():
    test_app.mainW.ui.relayHost.setText('test')
    test_app.mainW.relayHost()

    assert test_app.relay.host == ('test', 80)


def test_relayUser():
    test_app.mainW.ui.relayUser.setText('test')
    test_app.mainW.relayUser()

    assert test_app.relay.user == 'test'


def test_relayPassword():
    test_app.mainW.ui.relayPassword.setText('test')
    test_app.mainW.relayPassword()

    assert test_app.relay.password == 'test'


def test_mountHost():
    test_app.mainW.ui.mountHost.setText('test')
    test_app.mainW.mountHost()

    assert test_app.mount.host == ('test', 3492)


def test_mountMAC():
    test_app.mainW.ui.mountMAC.setText('00:00:00:00:00:00')
    test_app.mainW.mountMAC()

    assert test_app.mount.MAC == '00:00:00:00:00:00'
