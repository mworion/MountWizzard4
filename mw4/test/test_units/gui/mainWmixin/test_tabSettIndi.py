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
# Python  v3.7.4
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
# external packages
# local import
from mw4.test.test_units.setupQt import setupQt


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


def test_removePrefix_1():
    text = 'test is it'
    pre = 'test'
    val = app.mainW.removePrefix(text, pre)
    assert val == 'is it'


def test_removePrefix_2():
    text = 'testis it'
    pre = 'test'
    val = app.mainW.removePrefix(text, pre)
    assert val == 'is it'


def test_removePrefix_3():
    text = 'test   is it  '
    pre = 'test'
    val = app.mainW.removePrefix(text, pre)
    assert val == 'is it'


def test_indiMessage_1(qtbot):
    app.mainW.ui.message.setChecked(False)
    device = 'test'
    text = '[WARNING]'

    with qtbot.assertNotEmitted(app.message):
        suc = app.mainW.message(device, text)
        assert not suc


def test_indiMessage_2(qtbot):
    app.mainW.ui.message.setChecked(True)
    device = 'test'
    text = '[WARNING] this is a test'
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.message(device, text)
        assert suc
    assert ['test -> this is a test', 0] == blocker.args


def test_indiMessage_3(qtbot):
    app.mainW.ui.message.setChecked(True)
    device = 'test'
    text = '[ERROR] this is a test'
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.message(device, text)
        assert suc
    assert ['test -> this is a test', 2] == blocker.args


def test_showIndiDomeDisconnected(qtbot):
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.showIndiDomeDisconnected()
        assert suc
    assert ['INDI server environment disconnected', 0] == blocker.args


def test_showIndiNewEnvironDevice_1(qtbot):
    app.environ.name = 'test'
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.showIndiNewEnvironDevice('test')
        assert suc
    assert ['INDI environment device [test] found', 0] == blocker.args


def test_showIndiNewEnvironDevice_2(qtbot):
    app.environ.name = 'snoop'
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.showIndiNewEnvironDevice('test')
        assert suc
    assert ['INDI environment device snoops -> [test]', 0] == blocker.args


def test_showIndiRemoveEnvironDevice(qtbot):
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.showIndiRemoveEnvironDevice('test')
        assert suc
    assert ['INDI environment device [test] removed', 0] == blocker.args


def test_showEnvironDeviceConnected():
    suc = app.mainW.showEnvironDeviceConnected('test')
    assert suc


def test_showEnvironDeviceDisconnected():
    suc = app.mainW.showEnvironDeviceDisconnected('test')
    assert suc


def test_showIndiDomeDisconnected(qtbot):
    suc = app.mainW.showIndiDomeDisconnected()
    assert suc


def test_showIndiNewDomeDevice_1(qtbot):
    app.dome.name = 'test'
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.showIndiNewDomeDevice('test')
        assert suc
    assert ['INDI dome device [test] found', 0] == blocker.args


def test_showIndiNewDomeDevice_2(qtbot):
    app.dome.name = 'snoop'
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.showIndiNewDomeDevice('test')
        assert suc
    assert ['INDI dome device snoops -> [test]', 0] == blocker.args


def test_showIndiRemoveDomeDevice(qtbot):
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.showIndiRemoveDomeDevice('test')
        assert suc
    assert ['INDI dome device [test] removed', 0] == blocker.args


def test_showDomeDeviceConnected():
    suc = app.mainW.showDomeDeviceConnected('test')
    assert suc


def test_showDomeDeviceDisconnected():
    suc = app.mainW.showDomeDeviceDisconnected()
    assert suc


def test_showIndiImagingDisconnected(qtbot):
    suc = app.mainW.showIndiImagingDisconnected()
    assert suc


def test_showIndiNewImagingDevice_1(qtbot):
    app.imaging.name = 'test'
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.showIndiNewImagingDevice('test')
        assert suc
    assert ['INDI imaging device [test] found', 0] == blocker.args


def test_showIndiNewImagingDevice_2(qtbot):
    app.imaging.name = 'snoop'
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.showIndiNewImagingDevice('test')
        assert suc
    assert ['INDI imaging device snoops -> [test]', 0] == blocker.args


def test_showIndiRemoveImagingDevice(qtbot):
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.showIndiRemoveImagingDevice('test')
        assert suc
    assert ['INDI imaging device [test] removed', 0] == blocker.args


def test_showImagingDeviceConnected():
    suc = app.mainW.showImagingDeviceConnected('test')
    assert suc


def test_showImagingDeviceDisconnected():
    suc = app.mainW.showImagingDeviceDisconnected()
    assert suc


def test_showIndiSkymeterDisconnected(qtbot):
    suc = app.mainW.showIndiSkymeterDisconnected()
    assert suc


def test_showIndiNewSkymeterDevice_1(qtbot):
    app.skymeter.name = 'test'
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.showIndiNewSkymeterDevice('test')
        assert suc
    assert ['INDI skymeter device [test] found', 0] == blocker.args


def test_showIndiNewSkymeterDevice_2(qtbot):
    app.skymeter.name = 'snoop'
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.showIndiNewSkymeterDevice('test')
        assert suc
    assert ['INDI skymeter device snoops -> [test]', 0] == blocker.args


def test_showIndiRemoveSkymeterDevice(qtbot):
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.showIndiRemoveSkymeterDevice('test')
        assert suc
    assert ['INDI skymeter device [test] removed', 0] == blocker.args


def test_showSkymeterDeviceConnected():
    suc = app.mainW.showSkymeterDeviceConnected('test')
    assert suc


def test_showPowerDeviceDisconnected():
    suc = app.mainW.showPowerDeviceDisconnected()
    assert suc


def test_showIndiPowerDisconnected(qtbot):
    suc = app.mainW.showIndiPowerDisconnected()
    assert suc


def test_showIndiNewPowerDevice_1(qtbot):
    app.power.name = 'test'
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.showIndiNewPowerDevice('test')
        assert suc
    assert ['INDI power device [test] found', 0] == blocker.args


def test_showIndiNewPowerDevice_2(qtbot):
    app.power.name = 'snoop'
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.showIndiNewPowerDevice('test')
        assert suc
    assert ['INDI power device snoops -> [test]', 0] == blocker.args


def test_showIndiRemovePowerDevice(qtbot):
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.showIndiRemovePowerDevice('test')
        assert suc
    assert ['INDI power device [test] removed', 0] == blocker.args


def test_showPowerDeviceConnected():
    suc = app.mainW.showPowerDeviceConnected('test')
    assert suc


def test_showPowerDeviceDisconnected():
    suc = app.mainW.showPowerDeviceDisconnected('test')
    assert suc
