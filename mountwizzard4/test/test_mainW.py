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
import unittest
import unittest.mock as mock
import os
import time
# external packages
import pytest
import pytestqt
import PyQt5.QtGui
import PyQt5.QtWidgets
import PyQt5.uic
# local import
import mw4_global
import mw4_main


class MainWindowTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = PyQt5.QtWidgets.QApplication([])

    @classmethod
    def tearDownClass(cls):
        pass

    def quit(self):
        pass

    def setUp(self):
        mw4_global.work_dir = '/Users/mw/PycharmProjects/MountWizzard4'
        mw4_global.config_dir = '/Users/mw/PycharmProjects/MountWizzard4/config'
        self.main = mw4_main.MountWizzard4()
        self.spy = PyQt5.QtTest.QSignalSpy(self.main.message)

    def tearDown(self):
        pass

    #
    #
    # testing mainW gui updateMountConnStat
    #
    #

    def test_updateMountConnStat(self):
        suc = self.main.mainW.updateMountConnStat(True)
        self.assertEqual(True, suc)
        self.assertEqual('green', self.main.mainW.ui.mountConnected.property('color'))
        suc = self.main.mainW.updateMountConnStat(False)
        self.assertEqual(True, suc)
        self.assertEqual('red', self.main.mainW.ui.mountConnected.property('color'))

    #
    #
    # testing mainW gui update Gui
    #
    #

    def test_updateGuiCyclic(self):
        suc = self.main.mainW.updateGuiCyclic()
        self.assertEqual(True, suc)

    #
    #
    # testing mainW gui fw
    #
    #

    def test_updateFwGui_productName(self):
        value = 'Test1234'
        self.main.mount.fw.productName = value
        self.main.mainW.updateFwGui()
        self.assertEqual(value, self.main.mainW.ui.productName.text())
        value = None
        self.main.mount.fw.productName = value
        self.main.mainW.updateFwGui()
        self.assertEqual('-', self.main.mainW.ui.productName.text())

    def test_updateFwGui_hwVersion(self):
        value = 'Test1234'
        self.main.mount.fw.hwVersion = value
        self.main.mainW.updateFwGui()
        self.assertEqual(value, self.main.mainW.ui.hwVersion.text())
        value = None
        self.main.mount.fw.hwVersion = value
        self.main.mainW.updateFwGui()
        self.assertEqual('-', self.main.mainW.ui.hwVersion.text())

    def test_updateFwGui_numberString(self):
        value = '2.15.18'
        self.main.mount.fw.numberString = value
        self.main.mainW.updateFwGui()
        self.assertEqual(value, self.main.mainW.ui.numberString.text())
        value = None
        self.main.mount.fw.numberString = value
        self.main.mainW.updateFwGui()
        self.assertEqual('-', self.main.mainW.ui.numberString.text())

    def test_updateFwGui_fwdate(self):
        value = 'Test1234'
        self.main.mount.fw.fwdate = value
        self.main.mainW.updateFwGui()
        self.assertEqual(value, self.main.mainW.ui.fwdate.text())
        value = None
        self.main.mount.fw.fwdate = value
        self.main.mainW.updateFwGui()
        self.assertEqual('-', self.main.mainW.ui.fwdate.text())

    def test_updateFwGui_fwtime(self):
        value = 'Test1234'
        self.main.mount.fw.fwtime = value
        self.main.mainW.updateFwGui()
        self.assertEqual(value, self.main.mainW.ui.fwtime.text())
        value = None
        self.main.mount.fw.fwtime = value
        self.main.mainW.updateFwGui()
        self.assertEqual('-', self.main.mainW.ui.fwtime.text())

    #
    #
    # testing mainW gui model name
    #
    #

    def test_setNameList(self):
        value = ['Test1', 'test2', 'test3', 'test4']
        self.main.mount.model.nameList = value
        self.main.mainW.setNameList()
        self.assertEqual(4, self.main.mainW.ui.nameList.count())
        value = None
        self.main.mount.model.nameList = value
        self.main.mainW.setNameList()
        self.assertEqual(0, self.main.mainW.ui.nameList.count())

    #
    #
    # testing mainW gui pointing
    #
    #

    def test_updatePointGui_alt(self):
        value = '45'
        self.main.mount.obsSite.Alt = value
        self.main.mainW.updatePointGUI()
        self.assertEqual('45.00', self.main.mainW.ui.ALT.text())
        value = None
        self.main.mount.obsSite.Alt = value
        self.main.mainW.updatePointGUI()
        self.assertEqual('-', self.main.mainW.ui.ALT.text())

    def test_updatePointGui_az(self):
        value = '45'
        self.main.mount.obsSite.Az = value
        self.main.mainW.updatePointGUI()
        self.assertEqual('45.00', self.main.mainW.ui.AZ.text())
        value = None
        self.main.mount.obsSite.Az = value
        self.main.mainW.updatePointGUI()
        self.assertEqual('-', self.main.mainW.ui.AZ.text())

    def test_updatePointGui_ra(self):
        value = '45'
        self.main.mount.obsSite.raJNow = value
        self.main.mainW.updatePointGUI()
        self.assertEqual('45:00:00', self.main.mainW.ui.RA.text())
        value = None
        self.main.mount.obsSite.raJNow = value
        self.main.mainW.updatePointGUI()
        self.assertEqual('-', self.main.mainW.ui.RA.text())

    def test_updatePointGui_dec(self):
        value = '45'
        self.main.mount.obsSite.decJNow = value
        self.main.mainW.updatePointGUI()
        self.assertEqual('+45:00:00', self.main.mainW.ui.DEC.text())
        value = None
        self.main.mount.obsSite.decJNow = value
        self.main.mainW.updatePointGUI()
        self.assertEqual('-', self.main.mainW.ui.DEC.text())

    def test_updatePointGui_jd(self):
        value = '45'
        self.main.mount.obsSite.timeJD = value
        self.main.mainW.updatePointGUI()
        self.assertEqual('11:59:18', self.main.mainW.ui.timeJD.text())
        value = None
        self.main.mount.obsSite.timeJD = value
        self.main.mainW.updatePointGUI()
        self.assertEqual('-', self.main.mainW.ui.timeJD.text())

    def test_updatePointGui_pierside(self):
        value = 'W'
        self.main.mount.obsSite.pierside = value
        self.main.mainW.updatePointGUI()
        self.assertEqual('WEST', self.main.mainW.ui.pierside.text())
        value = None
        self.main.mount.obsSite.pierside = value
        self.main.mainW.updatePointGUI()
        self.assertEqual('-', self.main.mainW.ui.pierside.text())

    def test_updatePointGui_sidereal(self):
        value = '45'
        self.main.mount.obsSite.timeSidereal = value
        self.main.mainW.updatePointGUI()
        self.assertEqual('45', self.main.mainW.ui.timeSidereal.text())
        value = None
        self.main.mount.obsSite.timeSidereal = value
        self.main.mainW.updatePointGUI()
        self.assertEqual('-', self.main.mainW.ui.timeSidereal.text())

    def test_updatePointGui_statusText(self):
        self.main.mount.obsSite.status = 6
        self.main.mainW.updatePointGUI()
        self.assertEqual('Slewing or going to stop', self.main.mainW.ui.statusText.text())
        self.main.mount.obsSite.status = None
        self.main.mainW.updatePointGUI()
        self.assertEqual('-', self.main.mainW.ui.statusText.text())

    #
    #
    # testing mainW gui setting
    #
    #

    def test_updateSetting_slewRate(self):
        value = '15'
        self.main.mount.sett.slewRate = value
        self.main.mainW.updateSettingGUI()
        self.assertEqual('15', self.main.mainW.ui.slewRate.text())
        value = None
        self.main.mount.sett.slewRate = value
        self.main.mainW.updateSettingGUI()
        self.assertEqual('-', self.main.mainW.ui.slewRate.text())

    def test_updateSetting_timeToFlip(self):
        value = '15'
        self.main.mount.sett.timeToFlip = value
        self.main.mainW.updateSettingGUI()
        self.assertEqual(' 15', self.main.mainW.ui.timeToFlip.text())
        value = None
        self.main.mount.sett.timeToFlip = value
        self.main.mainW.updateSettingGUI()
        self.assertEqual('-', self.main.mainW.ui.timeToFlip.text())

    def test_updateSetting_UTCExpire(self):
        value = '2020-10-05'
        self.main.mount.sett.UTCExpire = value
        self.main.mainW.updateSettingGUI()
        self.assertEqual(value, self.main.mainW.ui.UTCExpire.text())
        value = None
        self.main.mount.sett.UTCExpire = value
        self.main.mainW.updateSettingGUI()
        self.assertEqual('-', self.main.mainW.ui.UTCExpire.text())

    def test_updateSetting_UTCExpire1(self):
        value = '2016-10-05'
        self.main.mount.sett.UTCExpire = value
        self.main.mainW.updateSettingGUI()
        self.assertEqual(value, self.main.mainW.ui.UTCExpire.text())
        value = None
        self.main.mount.sett.UTCExpire = value
        self.main.mainW.updateSettingGUI()
        self.assertEqual('-', self.main.mainW.ui.UTCExpire.text())

    def test_updateSetting_UTCExpire2(self):
        value = '2018-10-05'
        self.main.mount.sett.UTCExpire = value
        self.main.mainW.updateSettingGUI()
        self.assertEqual(value, self.main.mainW.ui.UTCExpire.text())
        value = None
        self.main.mount.sett.UTCExpire = value
        self.main.mainW.updateSettingGUI()
        self.assertEqual('-', self.main.mainW.ui.UTCExpire.text())

    def test_updateSetting_refractionTemp(self):
        value = '15'
        self.main.mount.sett.refractionTemp = value
        self.main.mainW.updateSettingGUI()
        self.assertEqual('+15.0', self.main.mainW.ui.refractionTemp.text())
        self.assertEqual('+15.0', self.main.mainW.ui.refractionTemp1.text())
        value = None
        self.main.mount.sett.refractionTemp = value
        self.main.mainW.updateSettingGUI()
        self.assertEqual('-', self.main.mainW.ui.refractionTemp.text())
        self.assertEqual('-', self.main.mainW.ui.refractionTemp1.text())

    def test_updateSetting_refractionPress(self):
        value = '1050.0'
        self.main.mount.sett.refractionPress = value
        self.main.mainW.updateSettingGUI()
        self.assertEqual(value, self.main.mainW.ui.refractionPress.text())
        self.assertEqual(value, self.main.mainW.ui.refractionPress1.text())
        value = None
        self.main.mount.sett.refractionPress = value
        self.main.mainW.updateSettingGUI()
        self.assertEqual('-', self.main.mainW.ui.refractionPress.text())
        self.assertEqual('-', self.main.mainW.ui.refractionPress1.text())

    def test_updateSetting_statusUnattendedFlip(self):
        value = '1'
        self.main.mount.sett.statusUnattendedFlip = value
        self.main.mainW.updateSettingGUI()
        self.assertEqual('ON', self.main.mainW.ui.statusUnattendedFlip.text())
        value = None
        self.main.mount.sett.statusUnattendedFlip = value
        self.main.mainW.updateSettingGUI()
        self.assertEqual('OFF', self.main.mainW.ui.statusUnattendedFlip.text())

    def test_updateSetting_statusDualTracking(self):
        value = '1'
        self.main.mount.sett.statusDualTracking = value
        self.main.mainW.updateSettingGUI()
        self.assertEqual('ON', self.main.mainW.ui.statusDualTracking.text())
        value = None
        self.main.mount.sett.statusDualTracking = value
        self.main.mainW.updateSettingGUI()
        self.assertEqual('OFF', self.main.mainW.ui.statusDualTracking.text())

    def test_updateSetting_statusRefraction(self):
        value = '1'
        self.main.mount.sett.statusRefraction = value
        self.main.mainW.updateSettingGUI()
        self.assertEqual('ON', self.main.mainW.ui.statusRefraction.text())
        value = None
        self.main.mount.sett.statusRefraction = value
        self.main.mainW.updateSettingGUI()
        self.assertEqual('OFF', self.main.mainW.ui.statusRefraction.text())

    def test_updateSetting_meridianLimitTrack(self):
        value = '15'
        self.main.mount.sett.meridianLimitTrack = value
        self.main.mainW.updateSettingGUI()
        self.assertEqual('15.0', self.main.mainW.ui.meridianLimitTrack.text())
        value = None
        self.main.mount.sett.meridianLimitTrack = value
        self.main.mainW.updateSettingGUI()
        self.assertEqual('-', self.main.mainW.ui.meridianLimitTrack.text())

    def test_updateSetting_meridianLimitSlew(self):
        value = '15'
        self.main.mount.sett.meridianLimitSlew = value
        self.main.mainW.updateSettingGUI()
        self.assertEqual('15.0', self.main.mainW.ui.meridianLimitSlew.text())
        value = None
        self.main.mount.sett.meridianLimitSlew = value
        self.main.mainW.updateSettingGUI()
        self.assertEqual('-', self.main.mainW.ui.meridianLimitSlew.text())

    def test_updateSetting_horizonLimitLow(self):
        value = '0'
        self.main.mount.sett.horizonLimitLow = value
        self.main.mainW.updateSettingGUI()
        self.assertEqual('0.0', self.main.mainW.ui.horizonLimitLow.text())
        value = None
        self.main.mount.sett.horizonLimitLow = value
        self.main.mainW.updateSettingGUI()
        self.assertEqual('-', self.main.mainW.ui.horizonLimitLow.text())

    def test_updateSetting_horizonLimitHigh(self):
        value = '50'
        self.main.mount.sett.horizonLimitHigh = value
        self.main.mainW.updateSettingGUI()
        self.assertEqual('50.0', self.main.mainW.ui.horizonLimitHigh.text())
        value = None
        self.main.mount.sett.horizonLimitHigh = value
        self.main.mainW.updateSettingGUI()
        self.assertEqual('-', self.main.mainW.ui.horizonLimitHigh.text())

    def test_updateSetting_timeToMeridian(self):
        self.main.mount.sett.timeToFlip = '100'
        self.main.mount.sett.meridianLimitTrack = '15'

        self.main.mainW.updateSettingGUI()
        self.assertEqual(' 40', self.main.mainW.ui.timeToMeridian.text())
        value = None
        self.main.mount.sett.timeToFlip = value
        self.main.mount.sett.meridianLimitTrack = value
        self.main.mainW.updateSettingGUI()
        self.assertEqual('-', self.main.mainW.ui.timeToMeridian.text())

    def test_updateSetting_location(self):

        self.main.mount.obsSite.location = ['49:00:00', '11:00:00', '500']
        self.main.mainW.updateSettingGUI()
        self.assertEqual('11deg 00\' 00.0\"', self.main.mainW.ui.siteLongitude.text())
        self.assertEqual('49deg 00\' 00.0\"', self.main.mainW.ui.siteLatitude.text())
        self.assertEqual('500.0', self.main.mainW.ui.siteElevation.text())

        self.main.mount.obsSite.location = None
        self.main.mainW.updateSettingGUI()
        self.assertEqual('-', self.main.mainW.ui.siteLongitude.text())
        self.assertEqual('-', self.main.mainW.ui.siteLatitude.text())
        self.assertEqual('-', self.main.mainW.ui.siteElevation.text())

    #
    #
    # testing mainW gui AlignGui
    #
    #

    def test_updateAlignGui_numberStars(self):
        with mock.patch.object(self.main.mainW, 'showModelPolar') as mMock:
            mMock.return_value.showModelPolar.return_value = None

            value = '50'
            self.main.mount.model.numberStars = value
            self.main.mainW.updateAlignGui()
            self.assertEqual('50', self.main.mainW.ui.numberStars.text())
            self.assertEqual('50', self.main.mainW.ui.numberStars1.text())
            value = None
            self.main.mount.model.numberStars = value
            self.main.mainW.updateAlignGui()
            self.assertEqual('-', self.main.mainW.ui.numberStars.text())
            self.assertEqual('-', self.main.mainW.ui.numberStars1.text())

    def test_updateAlignGui_altitudeError(self):
        with mock.patch.object(self.main.mainW, 'showModelPolar') as mMock:
            mMock.return_value.showModelPolar.return_value = None

            value = '50'
            self.main.mount.model.altitudeError = value
            self.main.mainW.updateAlignGui()
            self.assertEqual('50deg 00\' 00.0\"', self.main.mainW.ui.altitudeError.text())
            value = None
            self.main.mount.model.altitudeError = value
            self.main.mainW.updateAlignGui()
            self.assertEqual('-', self.main.mainW.ui.altitudeError.text())

    def test_updateAlignGui_errorRMS(self):
        with mock.patch.object(self.main.mainW, 'showModelPolar') as mMock:
            mMock.return_value.showModelPolar.return_value = None

            value = '50'
            self.main.mount.model.errorRMS = value
            self.main.mainW.updateAlignGui()
            self.assertEqual('50.0', self.main.mainW.ui.errorRMS.text())
            self.assertEqual('50.0', self.main.mainW.ui.errorRMS1.text())
            value = None
            self.main.mount.model.errorRMS = value
            self.main.mainW.updateAlignGui()
            self.assertEqual('-', self.main.mainW.ui.errorRMS.text())
            self.assertEqual('-', self.main.mainW.ui.errorRMS1.text())

    def test_updateAlignGui_azimuthError(self):
        with mock.patch.object(self.main.mainW, 'showModelPolar') as mMock:
            mMock.return_value.showModelPolar.return_value = None

            value = '50'
            self.main.mount.model.azimuthError = value
            self.main.mainW.updateAlignGui()
            self.assertEqual('50deg 00\' 00.0\"', self.main.mainW.ui.azimuthError.text())
            value = None
            self.main.mount.model.azimuthError = value
            self.main.mainW.updateAlignGui()
            self.assertEqual('-', self.main.mainW.ui.azimuthError.text())

    def test_updateAlignGui_terms(self):
        with mock.patch.object(self.main.mainW, 'showModelPolar') as mMock:
            mMock.return_value.showModelPolar.return_value = None

            value = '50'
            self.main.mount.model.terms = value
            self.main.mainW.updateAlignGui()
            self.assertEqual('50.0', self.main.mainW.ui.terms.text())
            value = None
            self.main.mount.model.terms = value
            self.main.mainW.updateAlignGui()
            self.assertEqual('-', self.main.mainW.ui.terms.text())

    def test_updateAlignGui_orthoError(self):
        with mock.patch.object(self.main.mainW, 'showModelPolar') as mMock:
            mMock.return_value.showModelPolar.return_value = None

            value = '50'
            self.main.mount.model.orthoError = value
            self.main.mainW.updateAlignGui()
            self.assertEqual('50deg 00\' 00.0\"', self.main.mainW.ui.orthoError.text())
            value = None
            self.main.mount.model.orthoError = value
            self.main.mainW.updateAlignGui()
            self.assertEqual('-', self.main.mainW.ui.orthoError.text())

    def test_updateAlignGui_positionAngle(self):
        with mock.patch.object(self.main.mainW, 'showModelPolar') as mMock:
            mMock.return_value.showModelPolar.return_value = None

            value = '50'
            self.main.mount.model.positionAngle = value
            self.main.mainW.updateAlignGui()
            self.assertEqual(' 50.0', self.main.mainW.ui.positionAngle.text())
            value = None
            self.main.mount.model.positionAngle = value
            self.main.mainW.updateAlignGui()
            self.assertEqual('-', self.main.mainW.ui.positionAngle.text())

    def test_updateAlignGui_polarError(self):
        with mock.patch.object(self.main.mainW, 'showModelPolar') as mMock:
            mMock.return_value.showModelPolar.return_value = None

            value = '50'
            self.main.mount.model.polarError = value
            self.main.mainW.updateAlignGui()
            self.assertEqual('50deg 00\' 00.0\"', self.main.mainW.ui.polarError.text())
            value = None
            self.main.mount.model.polarError = value
            self.main.mainW.updateAlignGui()
            self.assertEqual('-', self.main.mainW.ui.polarError.text())

    #
    #
    # testing mainW gui AlignGui
    #
    #

    def test_closeEvent(self):

        self.main.mainW.showStatus = True
        self.main.mainW.closeEvent(1)

        self.assertEqual(False, self.main.mainW.showStatus)

    #
    #
    # testing mainW gui model polar
    #
    #

    def test_showModelPolar1(self):
        self.main.mount.obsSite.location = ['49:00:00', '11:00:00', '580']
        self.main.mount.model._parseStars(['21:52:58.95,+08*56:10.1,   5.7,201',
                                           '21:06:10.79,+45*20:52.8,  12.1,329',
                                           '23:13:58.02,+38*48:18.8,  31.0,162',
                                           '17:43:41.26,+59*15:30.7,   8.4,005',
                                           ],
                                          4)
        self.main.mainW.ui.checkShowErrorValues.setChecked(True)
        suc = self.main.mainW.showModelPolar()
        self.assertEqual(True, suc)

    def test_showModelPolar2(self):
        self.main.mount.obsSite.location = ['49:00:00', '11:00:00', '580']
        self.main.mainW.ui.checkShowErrorValues.setChecked(True)
        suc = self.main.mainW.showModelPolar()
        self.assertEqual(False, suc)

    def test_showModelPolar3(self):
        self.main.mainW.ui.checkShowErrorValues.setChecked(True)
        suc = self.main.mainW.showModelPolar()
        self.assertEqual(False, suc)

#
#
# testing mainW gui change tracking
#
#


mw4_global.work_dir = '/Users/mw/PycharmProjects/MountWizzard4'
mw4_global.config_dir = '/Users/mw/PycharmProjects/MountWizzard4/config'


def test_changeTracking_ok1(qtbot):
    app = mw4_main.MountWizzard4()
    app.mount.obsSite.status = 0

    with mock.patch.object(app.mount.obsSite,
                           'stopTracking',
                           return_value=False):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.changeTracking()
            assert True == suc
        assert ['Cannot stop tracking', 2] == blocker.args


def test_changeTracking_ok2(qtbot):
    app = mw4_main.MountWizzard4()
    app.mount.obsSite.status = 0

    with mock.patch.object(app.mount.obsSite,
                           'stopTracking',
                           return_value=True):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.changeTracking()
            assert True == suc
        assert ['Stopped tracking', 0] == blocker.args


def test_changeTracking_ok3(qtbot):
    app = mw4_main.MountWizzard4()
    app.mount.obsSite.status = 1

    with mock.patch.object(app.mount.obsSite,
                           'startTracking',
                           return_value=False):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.changeTracking()
            assert True == suc
        assert ['Cannot start tracking', 2] == blocker.args


def test_changeTracking_ok4(qtbot):
    app = mw4_main.MountWizzard4()
    app.mount.obsSite.status = 1

    with mock.patch.object(app.mount.obsSite,
                           'startTracking',
                           return_value=True):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.changeTracking()
            assert True == suc
        assert ['Started tracking', 0] == blocker.args


def test_changePark_ok1(qtbot):
    app = mw4_main.MountWizzard4()
    app.mount.obsSite.status = 5

    with mock.patch.object(app.mount.obsSite,
                           'unpark',
                           return_value=False):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.changePark()
            assert True == suc
        assert ['Cannot unpark mount', 2] == blocker.args


def test_changePark_ok2(qtbot):
    app = mw4_main.MountWizzard4()
    app.mount.obsSite.status = 5

    with mock.patch.object(app.mount.obsSite,
                           'unpark',
                           return_value=True):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.changePark()
            assert True == suc
        assert ['Mount unparked', 0] == blocker.args


def test_changePark_ok3(qtbot):
    app = mw4_main.MountWizzard4()
    app.mount.obsSite.status = 1

    with mock.patch.object(app.mount.obsSite,
                           'park',
                           return_value=False):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.changePark()
            assert True == suc
        assert ['Cannot park mount', 2] == blocker.args


def test_changePark_ok4(qtbot):
    app = mw4_main.MountWizzard4()
    app.mount.obsSite.status = 1

    with mock.patch.object(app.mount.obsSite,
                           'park',
                           return_value=True):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.changePark()
            assert True == suc
        assert ['Mount parked', 0] == blocker.args


def test_setMeridianLimitTrack1(qtbot):
    app = mw4_main.MountWizzard4()
    app.mount.sett.meridianLimitTrack = None

    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'critical',
                           return_value=True):
        suc = app.mainW.setMeridianLimitTrack()
        assert False == suc


def test_setMeridianLimitTrack2(qtbot):
    app = mw4_main.MountWizzard4()
    app.mount.sett.meridianLimitTrack = 10

    suc = app.mainW.setMeridianLimitTrack()
    assert False == suc


def test_setMeridianLimitSlew1(qtbot):
    app = mw4_main.MountWizzard4()
    app.mount.sett.meridianLimitTrack = None

    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'critical',
                           return_value=True):
        suc = app.mainW.setMeridianLimitSlew()
        assert False == suc


def test_setMeridianLimitSlew2(qtbot):
    app = mw4_main.MountWizzard4()
    app.mount.sett.meridianLimitTrack = 10

    suc = app.mainW.setMeridianLimitSlew()
    assert False == suc


def test_setHorizonLimitHigh1(qtbot):
    app = mw4_main.MountWizzard4()
    app.mount.sett.horizonLimitHigh = None

    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'critical',
                           return_value=True):
        suc = app.mainW.setHorizonLimitHigh()
        assert False == suc


def test_setHorizonLimitHigh2(qtbot):
    app = mw4_main.MountWizzard4()
    app.mount.sett.horizonLimitHigh = 10

    suc = app.mainW.setHorizonLimitHigh()
    assert False == suc


def test_setHorizonLimitLow1(qtbot):
    app = mw4_main.MountWizzard4()
    app.mount.sett.horizonLimitLow = None

    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'critical',
                           return_value=True):
        suc = app.mainW.setHorizonLimitLow()
        assert False == suc


def test_setHorizonLimitLow2(qtbot):
    app = mw4_main.MountWizzard4()
    app.mount.sett.horizonLimitLow = 10

    suc = app.mainW.setHorizonLimitLow()
    assert False == suc


def test_setSlewRate1(qtbot):
    app = mw4_main.MountWizzard4()
    app.mount.sett.slewRate = None

    with mock.patch.object(PyQt5.QtWidgets.QMessageBox,
                           'critical',
                           return_value=True):
        suc = app.mainW.setSlewRate()
        assert False == suc


def test_setSlewRate2(qtbot):
    app = mw4_main.MountWizzard4()
    app.mount.sett.slewRate = 10

    suc = app.mainW.setSlewRate()
    assert False == suc