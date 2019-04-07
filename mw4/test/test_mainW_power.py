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
    assert '-' != app.mainW.ui.timeJD.text()


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


def test_updateStatusGui_statusText():
    app.mount.obsSite.status = 6
    app.mainW.updateStatusGUI()
    assert 'Slewing or going to stop' == app.mainW.ui.statusText.text()
    app.mount.obsSite.status = None
    app.mainW.updateStatusGUI()
    assert '-' == app.mainW.ui.statusText.text()


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


def test_updateSetting_statusGPSSynced_1():
    value = True
    app.mount.sett.gpsSynced = value
    app.mainW.updateSetStatGUI()
    assert app.mainW.ui.statusGPSSynced.text() == 'YES'


def test_updateSetting_statusGPSSynced_2():
    value = None
    app.mount.sett.gpsSynced = value
    app.mainW.updateSetStatGUI()
    assert app.mainW.ui.statusGPSSynced.text() == 'NO'


def test_updateSetting_statusGPSSynced_3():
    value = False
    app.mount.sett.gpsSynced = value
    app.mainW.updateSetStatGUI()
    assert app.mainW.ui.statusGPSSynced.text() == 'NO'


def test_tracking_speed1():
    with mock.patch.object(app.mount.sett,
                           'checkRateLunar',
                           return_value=True):
        suc = app.mainW.updateTrackingGui()
        assert suc


def test_tracking_speed2():
    with mock.patch.object(app.mount.sett,
                           'checkRateSidereal',
                           return_value=True):
        suc = app.mainW.updateTrackingGui()
        assert suc


def test_tracking_speed3():
    with mock.patch.object(app.mount.sett,
                           'checkRateSolar',
                           return_value=True):
        suc = app.mainW.updateTrackingGui()
        assert suc


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


def test_slewParkPos_1(qtbot):
    class Test:
        @staticmethod
        def text():
            return '1'
    buttons = range(0, 8)
    alt = [Test(), Test(), Test(), Test(), Test(), Test(), Test(), Test()]
    az = [Test(), Test(), Test(), Test(), Test(), Test(), Test(), Test()]
    app.mainW.posButtons = buttons
    app.mainW.posAlt = alt
    app.mainW.posAz = az

    with mock.patch.object(app.mount.obsSite,
                           'slewAltAz',
                           return_value=True):
        for button in buttons:
            with mock.patch.object(app.mainW,
                                   'sender',
                                   return_value=button):
                suc = app.mainW.slewToParkPos()
                assert suc


def test_slewParkPos_2(qtbot):
    buttons = str(range(0, 8))
    app.mainW.posButtons = buttons
    with mock.patch.object(app.mount.obsSite,
                           'slewAltAz',
                           return_value=False):
        for button in buttons:
            with mock.patch.object(app.mainW,
                                   'sender',
                                   return_value=button):
                suc = app.mainW.slewToParkPos()
                assert not suc


def test_slewParkPos_3(qtbot):
    buttons = range(0, 8)
    app.mainW.posButtons = buttons
    with mock.patch.object(app.mount.obsSite,
                           'slewAltAz',
                           return_value=False):
        with mock.patch.object(app.mainW,
                               'sender',
                               return_value=None):
            suc = app.mainW.slewToParkPos()
            assert not suc


def test_slewParkPos_4(qtbot):
    class Test:
        @staticmethod
        def text():
            return '1'
    buttons = range(0, 8)
    alt = [Test(), Test(), Test(), Test(), Test(), Test(), Test(), Test()]
    az = [Test(), Test(), Test(), Test(), Test(), Test(), Test(), Test()]
    app.mainW.posButtons = buttons
    app.mainW.posAlt = alt
    app.mainW.posAz = az

    with qtbot.waitSignal(app.message) as blocker:
        with mock.patch.object(app.mount.obsSite,
                               'slewAltAz',
                               return_value=True):
            for button in buttons:
                with mock.patch.object(app.mainW,
                                       'sender',
                                       return_value=button):
                    suc = app.mainW.slewToParkPos()
                    assert suc
            assert ['Slew to [Park Pos 0]', 0] == blocker.args


def test_slewParkPos_5(qtbot):
    class Test:
        @staticmethod
        def text():
            return '1'
    buttons = range(0, 8)
    alt = [Test(), Test(), Test(), Test(), Test(), Test(), Test(), Test()]
    az = [Test(), Test(), Test(), Test(), Test(), Test(), Test(), Test()]
    app.mainW.posButtons = buttons
    app.mainW.posAlt = alt
    app.mainW.posAz = az

    with qtbot.waitSignal(app.message) as blocker:
        with mock.patch.object(app.mount.obsSite,
                               'slewAltAz',
                               return_value=False):
            for button in buttons:
                with mock.patch.object(app.mainW,
                                       'sender',
                                       return_value=button):
                    suc = app.mainW.slewToParkPos()
                    assert not suc
            assert ['Cannot slew to [Park Pos 0]', 2] == blocker.args


def test_stop1(qtbot):
    with mock.patch.object(app.mount.obsSite,
                           'stop',
                           return_value=True):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.stop()
            assert suc
        assert ['Mount stopped', 0] == blocker.args


def test_stop2(qtbot):
    with mock.patch.object(app.mount.obsSite,
                           'stop',
                           return_value=False):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.stop()
            assert not suc
        assert ['Cannot stop mount', 2] == blocker.args
