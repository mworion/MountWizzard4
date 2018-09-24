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
import PyQt5.QtTest
import PyQt5.QtGui
import PyQt5.QtWidgets
import PyQt5.uic
# local import
import gui.mainW
import mw4_global
import mountcontrol.qtmount


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
        self.mount = mountcontrol.qtmount.Mount()
        self.mainW = gui.mainW.MainWindow(self)

    def tearDown(self):
        pass

    #
    #
    # testing mainW gui fw
    #
    #

    def test_updateFwGui_productName(self):
        value = 'Test1234'
        self.mount.fw.productName = value
        self.mainW.updateFwGui()
        self.assertEqual(value, self.mainW.ui.productName.text())
        value = None
        self.mount.fw.productName = value
        self.mainW.updateFwGui()
        self.assertEqual('-', self.mainW.ui.productName.text())

    def test_updateFwGui_hwVersion(self):
        value = 'Test1234'
        self.mount.fw.hwVersion = value
        self.mainW.updateFwGui()
        self.assertEqual(value, self.mainW.ui.hwVersion.text())
        value = None
        self.mount.fw.hwVersion = value
        self.mainW.updateFwGui()
        self.assertEqual('-', self.mainW.ui.hwVersion.text())

    def test_updateFwGui_numberString(self):
        value = '2.15.18'
        self.mount.fw.numberString = value
        self.mainW.updateFwGui()
        self.assertEqual(value, self.mainW.ui.numberString.text())
        value = None
        self.mount.fw.numberString = value
        self.mainW.updateFwGui()
        self.assertEqual('-', self.mainW.ui.numberString.text())

    def test_updateFwGui_fwdate(self):
        value = 'Test1234'
        self.mount.fw.fwdate = value
        self.mainW.updateFwGui()
        self.assertEqual(value, self.mainW.ui.fwdate.text())
        value = None
        self.mount.fw.fwdate = value
        self.mainW.updateFwGui()
        self.assertEqual('-', self.mainW.ui.fwdate.text())

    def test_updateFwGui_fwtime(self):
        value = 'Test1234'
        self.mount.fw.fwtime = value
        self.mainW.updateFwGui()
        self.assertEqual(value, self.mainW.ui.fwtime.text())
        value = None
        self.mount.fw.fwtime = value
        self.mainW.updateFwGui()
        self.assertEqual('-', self.mainW.ui.fwtime.text())

    #
    #
    # testing mainW gui model name
    #
    #

    def test_setNameList(self):
        value = ['Test1', 'test2', 'test3', 'test4']
        self.mount.model.nameList = value
        self.mainW.setNameList()
        self.assertEqual(4, self.mainW.ui.nameList.count())
        value = None
        self.mount.model.nameList = value
        self.mainW.setNameList()
        self.assertEqual(0, self.mainW.ui.nameList.count())

    #
    #
    # testing mainW gui pointing
    #
    #

    def test_updatePointGui_alt(self):
        value = '45'
        self.mount.obsSite.Alt = value
        self.mainW.updatePointGUI()
        self.assertEqual('45.00', self.mainW.ui.ALT.text())
        value = None
        self.mount.obsSite.Alt = value
        self.mainW.updatePointGUI()
        self.assertEqual('-', self.mainW.ui.ALT.text())

    def test_updatePointGui_az(self):
        value = '45'
        self.mount.obsSite.Az = value
        self.mainW.updatePointGUI()
        self.assertEqual('45.00', self.mainW.ui.AZ.text())
        value = None
        self.mount.obsSite.Az = value
        self.mainW.updatePointGUI()
        self.assertEqual('-', self.mainW.ui.AZ.text())

    def test_updatePointGui_ra(self):
        value = '45'
        self.mount.obsSite.raJNow = value
        self.mainW.updatePointGUI()
        self.assertEqual('45:00:00', self.mainW.ui.RA.text())
        value = None
        self.mount.obsSite.raJNow = value
        self.mainW.updatePointGUI()
        self.assertEqual('-', self.mainW.ui.RA.text())

    def test_updatePointGui_dec(self):
        value = '45'
        self.mount.obsSite.decJNow = value
        self.mainW.updatePointGUI()
        self.assertEqual('+45:00:00', self.mainW.ui.DEC.text())
        value = None
        self.mount.obsSite.decJNow = value
        self.mainW.updatePointGUI()
        self.assertEqual('-', self.mainW.ui.DEC.text())

    def test_updatePointGui_jd(self):
        value = '45'
        self.mount.obsSite.timeJD = value
        self.mainW.updatePointGUI()
        self.assertEqual('11:59:18', self.mainW.ui.timeJD.text())
        value = None
        self.mount.obsSite.timeJD = value
        self.mainW.updatePointGUI()
        self.assertEqual('-', self.mainW.ui.timeJD.text())

    def test_updatePointGui_pierside(self):
        value = 'W'
        self.mount.obsSite.pierside = value
        self.mainW.updatePointGUI()
        self.assertEqual('WEST', self.mainW.ui.pierside.text())
        value = None
        self.mount.obsSite.pierside = value
        self.mainW.updatePointGUI()
        self.assertEqual('-', self.mainW.ui.pierside.text())

    def test_updatePointGui_sidereal(self):
        value = '45'
        self.mount.obsSite.timeSidereal = value
        self.mainW.updatePointGUI()
        self.assertEqual('45', self.mainW.ui.timeSidereal.text())
        value = None
        self.mount.obsSite.timeSidereal = value
        self.mainW.updatePointGUI()
        self.assertEqual('-', self.mainW.ui.timeSidereal.text())

    def test_updatePointGui_statusText(self):
        self.mount.obsSite.status = 6
        self.mainW.updatePointGUI()
        self.assertEqual('Slewing or going to stop', self.mainW.ui.statusText.text())
        self.mount.obsSite.status = None
        self.mainW.updatePointGUI()
        self.assertEqual('-', self.mainW.ui.statusText.text())

    #
    #
    # testing mainW gui setting
    #
    #

    def test_updateSetting_slewRate(self):
        value = '15'
        self.mount.sett.slewRate = value
        self.mainW.updateSettingGUI()
        self.assertEqual('15', self.mainW.ui.slewRate.text())
        value = None
        self.mount.sett.slewRate = value
        self.mainW.updateSettingGUI()
        self.assertEqual('-', self.mainW.ui.slewRate.text())

    def test_updateSetting_timeToFlip(self):
        value = '15'
        self.mount.sett.timeToFlip = value
        self.mainW.updateSettingGUI()
        self.assertEqual(' 15', self.mainW.ui.timeToFlip.text())
        value = None
        self.mount.sett.timeToFlip = value
        self.mainW.updateSettingGUI()
        self.assertEqual('-', self.mainW.ui.timeToFlip.text())

    def test_updateSetting_UTCExpire(self):
        value = '2020-10-05'
        self.mount.sett.UTCExpire = value
        self.mainW.updateSettingGUI()
        self.assertEqual(value, self.mainW.ui.UTCExpire.text())
        value = None
        self.mount.sett.UTCExpire = value
        self.mainW.updateSettingGUI()
        self.assertEqual('-', self.mainW.ui.UTCExpire.text())

    def test_updateSetting_UTCExpire1(self):
        value = '2016-10-05'
        self.mount.sett.UTCExpire = value
        self.mainW.updateSettingGUI()
        self.assertEqual(value, self.mainW.ui.UTCExpire.text())
        value = None
        self.mount.sett.UTCExpire = value
        self.mainW.updateSettingGUI()
        self.assertEqual('-', self.mainW.ui.UTCExpire.text())

    def test_updateSetting_UTCExpire2(self):
        value = '2018-10-05'
        self.mount.sett.UTCExpire = value
        self.mainW.updateSettingGUI()
        self.assertEqual(value, self.mainW.ui.UTCExpire.text())
        value = None
        self.mount.sett.UTCExpire = value
        self.mainW.updateSettingGUI()
        self.assertEqual('-', self.mainW.ui.UTCExpire.text())

    def test_updateSetting_refractionTemp(self):
        value = '15'
        self.mount.sett.refractionTemp = value
        self.mainW.updateSettingGUI()
        self.assertEqual('+15.0', self.mainW.ui.refractionTemp.text())
        self.assertEqual('+15.0', self.mainW.ui.refractionTemp1.text())
        value = None
        self.mount.sett.refractionTemp = value
        self.mainW.updateSettingGUI()
        self.assertEqual('-', self.mainW.ui.refractionTemp.text())
        self.assertEqual('-', self.mainW.ui.refractionTemp1.text())

    def test_updateSetting_refractionPress(self):
        value = '1050.0'
        self.mount.sett.refractionPress = value
        self.mainW.updateSettingGUI()
        self.assertEqual(value, self.mainW.ui.refractionPress.text())
        self.assertEqual(value, self.mainW.ui.refractionPress1.text())
        value = None
        self.mount.sett.refractionPress = value
        self.mainW.updateSettingGUI()
        self.assertEqual('-', self.mainW.ui.refractionPress.text())
        self.assertEqual('-', self.mainW.ui.refractionPress1.text())

    def test_updateSetting_statusUnattendedFlip(self):
        value = '1'
        self.mount.sett.statusUnattendedFlip = value
        self.mainW.updateSettingGUI()
        self.assertEqual('ON', self.mainW.ui.statusUnattendedFlip.text())
        value = None
        self.mount.sett.statusUnattendedFlip = value
        self.mainW.updateSettingGUI()
        self.assertEqual('OFF', self.mainW.ui.statusUnattendedFlip.text())

    def test_updateSetting_statusDualTracking(self):
        value = '1'
        self.mount.sett.statusDualTracking = value
        self.mainW.updateSettingGUI()
        self.assertEqual('ON', self.mainW.ui.statusDualTracking.text())
        value = None
        self.mount.sett.statusDualTracking = value
        self.mainW.updateSettingGUI()
        self.assertEqual('OFF', self.mainW.ui.statusDualTracking.text())

    def test_updateSetting_statusRefraction(self):
        value = '1'
        self.mount.sett.statusRefraction = value
        self.mainW.updateSettingGUI()
        self.assertEqual('ON', self.mainW.ui.statusRefraction.text())
        value = None
        self.mount.sett.statusRefraction = value
        self.mainW.updateSettingGUI()
        self.assertEqual('OFF', self.mainW.ui.statusRefraction.text())

    def test_updateSetting_meridianLimitTrack(self):
        value = '15'
        self.mount.sett.meridianLimitTrack = value
        self.mainW.updateSettingGUI()
        self.assertEqual('15.0', self.mainW.ui.meridianLimitTrack.text())
        value = None
        self.mount.sett.meridianLimitTrack = value
        self.mainW.updateSettingGUI()
        self.assertEqual('-', self.mainW.ui.meridianLimitTrack.text())

    def test_updateSetting_meridianLimitSlew(self):
        value = '15'
        self.mount.sett.meridianLimitSlew = value
        self.mainW.updateSettingGUI()
        self.assertEqual('15.0', self.mainW.ui.meridianLimitSlew.text())
        value = None
        self.mount.sett.meridianLimitSlew = value
        self.mainW.updateSettingGUI()
        self.assertEqual('-', self.mainW.ui.meridianLimitSlew.text())

    def test_updateSetting_horizonLimitLow(self):
        value = '0'
        self.mount.sett.horizonLimitLow = value
        self.mainW.updateSettingGUI()
        self.assertEqual('0.0', self.mainW.ui.horizonLimitLow.text())
        value = None
        self.mount.sett.horizonLimitLow = value
        self.mainW.updateSettingGUI()
        self.assertEqual('-', self.mainW.ui.horizonLimitLow.text())

    def test_updateSetting_horizonLimitHigh(self):
        value = '50'
        self.mount.sett.horizonLimitHigh = value
        self.mainW.updateSettingGUI()
        self.assertEqual('50.0', self.mainW.ui.horizonLimitHigh.text())
        value = None
        self.mount.sett.horizonLimitHigh = value
        self.mainW.updateSettingGUI()
        self.assertEqual('-', self.mainW.ui.horizonLimitHigh.text())

    def test_updateSetting_timeToMeridian(self):
        self.mount.sett.timeToFlip = '100'
        self.mount.sett.meridianLimitTrack = '15'

        self.mainW.updateSettingGUI()
        self.assertEqual(' 40', self.mainW.ui.timeToMeridian.text())
        value = None
        self.mount.sett.timeToFlip = value
        self.mount.sett.meridianLimitTrack = value
        self.mainW.updateSettingGUI()
        self.assertEqual('-', self.mainW.ui.timeToMeridian.text())

    def test_updateSetting_location(self):

        self.mount.obsSite.location = ['49:00:00', '11:00:00', '500']
        self.mainW.updateSettingGUI()
        self.assertEqual('11deg 00\' 00.0\"', self.mainW.ui.siteLongitude.text())
        self.assertEqual('49deg 00\' 00.0\"', self.mainW.ui.siteLatitude.text())
        self.assertEqual('500.0', self.mainW.ui.siteElevation.text())

        self.mount.obsSite.location = None
        self.mainW.updateSettingGUI()
        self.assertEqual('-', self.mainW.ui.siteLongitude.text())
        self.assertEqual('-', self.mainW.ui.siteLatitude.text())
        self.assertEqual('-', self.mainW.ui.siteElevation.text())

    #
    #
    # testing mainW gui AlignGui
    #
    #

    def test_updateAlignGui_numberStars(self):
        with mock.patch.object(self.mainW, 'showModelPolar') as mMock:
            mMock.return_value.showModelPolar.return_value = None

            value = '50'
            self.mount.model.numberStars = value
            self.mainW.updateAlignGui()
            self.assertEqual('50', self.mainW.ui.numberStars.text())
            self.assertEqual('50', self.mainW.ui.numberStars1.text())
            value = None
            self.mount.model.numberStars = value
            self.mainW.updateAlignGui()
            self.assertEqual('-', self.mainW.ui.numberStars.text())
            self.assertEqual('-', self.mainW.ui.numberStars1.text())

    def test_updateAlignGui_altitudeError(self):
        with mock.patch.object(self.mainW, 'showModelPolar') as mMock:
            mMock.return_value.showModelPolar.return_value = None

            value = '50'
            self.mount.model.altitudeError = value
            self.mainW.updateAlignGui()
            self.assertEqual('50deg 00\' 00.0\"', self.mainW.ui.altitudeError.text())
            value = None
            self.mount.model.altitudeError = value
            self.mainW.updateAlignGui()
            self.assertEqual('-', self.mainW.ui.altitudeError.text())

    def test_updateAlignGui_errorRMS(self):
        with mock.patch.object(self.mainW, 'showModelPolar') as mMock:
            mMock.return_value.showModelPolar.return_value = None

            value = '50'
            self.mount.model.errorRMS = value
            self.mainW.updateAlignGui()
            self.assertEqual('50.0', self.mainW.ui.errorRMS.text())
            self.assertEqual('50.0', self.mainW.ui.errorRMS1.text())
            value = None
            self.mount.model.errorRMS = value
            self.mainW.updateAlignGui()
            self.assertEqual('-', self.mainW.ui.errorRMS.text())
            self.assertEqual('-', self.mainW.ui.errorRMS1.text())

    def test_updateAlignGui_azimuthError(self):
        with mock.patch.object(self.mainW, 'showModelPolar') as mMock:
            mMock.return_value.showModelPolar.return_value = None

            value = '50'
            self.mount.model.azimuthError = value
            self.mainW.updateAlignGui()
            self.assertEqual('50deg 00\' 00.0\"', self.mainW.ui.azimuthError.text())
            value = None
            self.mount.model.azimuthError = value
            self.mainW.updateAlignGui()
            self.assertEqual('-', self.mainW.ui.azimuthError.text())

    def test_updateAlignGui_terms(self):
        with mock.patch.object(self.mainW, 'showModelPolar') as mMock:
            mMock.return_value.showModelPolar.return_value = None

            value = '50'
            self.mount.model.terms = value
            self.mainW.updateAlignGui()
            self.assertEqual('50.0', self.mainW.ui.terms.text())
            value = None
            self.mount.model.terms = value
            self.mainW.updateAlignGui()
            self.assertEqual('-', self.mainW.ui.terms.text())

    def test_updateAlignGui_orthoError(self):
        with mock.patch.object(self.mainW, 'showModelPolar') as mMock:
            mMock.return_value.showModelPolar.return_value = None

            value = '50'
            self.mount.model.orthoError = value
            self.mainW.updateAlignGui()
            self.assertEqual('50deg 00\' 00.0\"', self.mainW.ui.orthoError.text())
            value = None
            self.mount.model.orthoError = value
            self.mainW.updateAlignGui()
            self.assertEqual('-', self.mainW.ui.orthoError.text())

    def test_updateAlignGui_positionAngle(self):
        with mock.patch.object(self.mainW, 'showModelPolar') as mMock:
            mMock.return_value.showModelPolar.return_value = None

            value = '50'
            self.mount.model.positionAngle = value
            self.mainW.updateAlignGui()
            self.assertEqual(' 50.0', self.mainW.ui.positionAngle.text())
            value = None
            self.mount.model.positionAngle = value
            self.mainW.updateAlignGui()
            self.assertEqual('-', self.mainW.ui.positionAngle.text())

    def test_updateAlignGui_polarError(self):
        with mock.patch.object(self.mainW, 'showModelPolar') as mMock:
            mMock.return_value.showModelPolar.return_value = None

            value = '50'
            self.mount.model.polarError = value
            self.mainW.updateAlignGui()
            self.assertEqual('50deg 00\' 00.0\"', self.mainW.ui.polarError.text())
            value = None
            self.mount.model.polarError = value
            self.mainW.updateAlignGui()
            self.assertEqual('-', self.mainW.ui.polarError.text())

    #
    #
    # testing mainW gui AlignGui
    #
    #

    def test_closeEvent(self):

        self.mainW.showStatus = True
        self.mainW.closeEvent(1)

        self.assertEqual(False, self.mainW.showStatus)

    #
    #
    # testing mainW gui model polar
    #
    #

    def test_showModelPolar(self):
        self.mount.obsSite.location = ['49:00:00', '11:00:00', '580']
        self.mount.model.starList = ['21:52:58.95,+08*56:10.1,   5.7,201',
                                     '21:06:10.79,+45*20:52.8,  12.1,329',
                                     '23:13:58.02,+38*48:18.8,  31.0,162',
                                     '17:43:41.26,+59*15:30.7,   8.4,005',
                                     ]
        self.mainW.showModelPolar()
