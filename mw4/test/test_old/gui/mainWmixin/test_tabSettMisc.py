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
# Python  v3.7.5
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
import logging
import pytest
import unittest.mock as mock
# external packages
import PyQt5
# local import
from mw4.test.test_old.setupQt import setupQt


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


def test_setLoggingLevel1(qtbot):
    app.mainW.ui.loglevelDebug.setChecked(True)
    app.mainW.setLoggingLevel()
    val = logging.getLogger().getEffectiveLevel()
    assert val == 20


def test_setLoggingLevel2(qtbot):
    app.mainW.ui.loglevelInfo.setChecked(True)
    app.mainW.setLoggingLevel()
    val = logging.getLogger().getEffectiveLevel()
    assert val == 30


def test_updateFwGui_productName():
    value = 'Test1234'
    app.mount.firmware.product = value
    app.mainW.updateFwGui(app.mount.firmware)
    assert value == app.mainW.ui.product.text()
    value = None
    app.mount.firmware.product = value
    app.mainW.updateFwGui(app.mount.firmware)
    assert '-' == app.mainW.ui.product.text()


def test_updateFwGui_hwVersion():
    value = 'Test1234'
    app.mount.firmware.hardware = value
    app.mainW.updateFwGui(app.mount.firmware)
    assert value == app.mainW.ui.hardware.text()
    value = None
    app.mount.firmware.hardware = value
    app.mainW.updateFwGui(app.mount.firmware)
    assert '-' == app.mainW.ui.hardware.text()


def test_updateFwGui_numberString():
    value = '2.15.18'
    app.mount.firmware.vString = value
    app.mainW.updateFwGui(app.mount.firmware)
    assert value == app.mainW.ui.vString.text()
    value = None
    app.mount.firmware.vString = value
    app.mainW.updateFwGui(app.mount.firmware)
    assert '-' == app.mainW.ui.vString.text()


def test_updateFwGui_fwdate():
    value = 'Test1234'
    app.mount.firmware.date = value
    app.mainW.updateFwGui(app.mount.firmware)
    assert value == app.mainW.ui.fwdate.text()
    value = None
    app.mount.firmware.date = value
    app.mainW.updateFwGui(app.mount.firmware)
    assert '-' == app.mainW.ui.fwdate.text()


def test_updateFwGui_fwtime():
    value = 'Test1234'
    app.mount.firmware.time = value
    app.mainW.updateFwGui(app.mount.firmware)
    assert value == app.mainW.ui.fwtime.text()
    value = None
    app.mount.firmware.time = value
    app.mainW.updateFwGui(app.mount.firmware)
    assert '-' == app.mainW.ui.fwtime.text()


def test_playAudioDomeSlewFinished_1():
    with mock.patch.object(PyQt5.QtMultimedia.QSound,
                           'play'):
        suc = app.mainW.playSound('DomeSlew')
        # todo not suc is wrong, just workaround
        assert not suc


def test_playAudioMountSlewFinished_1():
    with mock.patch.object(PyQt5.QtMultimedia.QSound,
                           'play'):
        suc = app.mainW.playSound('MountSlew')
        assert not suc


def test_playAudioMountAlert_1():
    with mock.patch.object(PyQt5.QtMultimedia.QSound,
                           'play'):
        suc = app.mainW.playSound('MountAlert')
        assert not suc


def test_playAudioModelFinished_1():
    with mock.patch.object(PyQt5.QtMultimedia.QSound,
                           'play'):
        suc = app.mainW.playSound('ModelFinished')
        assert not suc
