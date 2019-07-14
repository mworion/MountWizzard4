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
# Python  v3.7.3
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
    text = 'test_mountwizzard is it'
    pre = 'test_mountwizzard'
    val = app.mainW._removePrefix(text, pre)
    assert val == 'is it'


def test_removePrefix_2():
    text = 'testis it'
    pre = 'test_mountwizzard'
    val = app.mainW._removePrefix(text, pre)
    assert val == 'is it'


def test_removePrefix_3():
    text = 'test_mountwizzard   is it  '
    pre = 'test_mountwizzard'
    val = app.mainW._removePrefix(text, pre)
    assert val == 'is it'


def test_indiMessage_1(qtbot):
    app.mainW.ui.indiMessage.setChecked(False)
    device = 'test_mountwizzard'
    text = '[WARNING]'

    with qtbot.assertNotEmitted(app.message):
        suc = app.mainW.indiMessage(device, text)
        assert not suc


def test_indiMessage_2(qtbot):
    app.mainW.ui.indiMessage.setChecked(True)
    device = 'test_mountwizzard'
    text = '[WARNING] this is a test_mountwizzard'
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.indiMessage(device, text)
        assert suc
    assert ['test_mountwizzard -> this is a test_mountwizzard', 0] == blocker.args


def test_indiMessage_3(qtbot):
    app.mainW.ui.indiMessage.setChecked(True)
    device = 'test_mountwizzard'
    text = '[ERROR] this is a test_mountwizzard'
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.indiMessage(device, text)
        assert suc
    assert ['test_mountwizzard -> this is a test_mountwizzard', 2] == blocker.args


def test_showIndiEnvironConnected(qtbot):
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.showIndiEnvironConnected()
        assert suc
    assert ['INDI server environment connected', 0] == blocker.args


def test_showIndiEnvironDisconnected(qtbot):
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.showIndiEnvironDisconnected()
        assert suc
    assert ['INDI server environment disconnected', 0] == blocker.args


def test_showIndiNewEnvironDevice_1(qtbot):
    app.environ.name = 'test_mountwizzard'
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.showIndiNewEnvironDevice('test_mountwizzard')
        assert suc
    assert ['INDI environment device [test_mountwizzard] found', 0] == blocker.args


def test_showIndiNewEnvironDevice_2(qtbot):
    app.environ.name = 'snoop'
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.showIndiNewEnvironDevice('test_mountwizzard')
        assert suc
    assert ['INDI environment device snoops -> [test_mountwizzard]', 0] == blocker.args


def test_showIndiRemoveEnvironDevice(qtbot):
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.showIndiRemoveEnvironDevice('test_mountwizzard')
        assert suc
    assert ['INDI environment device [test_mountwizzard] removed', 0] == blocker.args


def test_showEnvironDeviceConnected():
    suc = app.mainW.showEnvironDeviceConnected()
    assert suc


def test_showEnvironDeviceDisconnected():
    suc = app.mainW.showEnvironDeviceDisconnected()
    assert suc


def test_showIndiSkymeterConnected(qtbot):
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.showIndiSkymeterConnected()
        assert suc
    assert ['INDI server skymeter connected', 0] == blocker.args


def test_showIndiSkymeterDisconnected(qtbot):
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.showIndiSkymeterDisconnected()
        assert suc
    assert ['INDI server skymeter disconnected', 0] == blocker.args


def test_showIndiNewSkymeterDevice_1(qtbot):
    app.skymeter.name = 'test_mountwizzard'
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.showIndiNewSkymeterDevice('test_mountwizzard')
        assert suc
    assert ['INDI skymeter device [test_mountwizzard] found', 0] == blocker.args


def test_showIndiNewSkymeterDevice_2(qtbot):
    app.skymeter.name = 'snoop'
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.showIndiNewSkymeterDevice('test_mountwizzard')
        assert suc
    assert ['INDI skymeter device snoops -> [test_mountwizzard]', 0] == blocker.args


def test_showIndiRemoveSkymeterDevice(qtbot):
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.showIndiRemoveSkymeterDevice('test_mountwizzard')
        assert suc
    assert ['INDI skymeter device [test_mountwizzard] removed', 0] == blocker.args


def test_showSkymeterDeviceConnected():
    suc = app.mainW.showSkymeterDeviceConnected()
    assert suc


def test_showSkymeterDeviceDisconnected():
    suc = app.mainW.showSkymeterDeviceDisconnected()
    assert suc


def test_showIndiWeatherConnected(qtbot):
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.showIndiWeatherConnected()
        assert suc
    assert ['INDI server weather connected', 0] == blocker.args


def test_showIndiWeatherDisconnected(qtbot):
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.showIndiWeatherDisconnected()
        assert suc
    assert ['INDI server weather disconnected', 0] == blocker.args


def test_showIndiNewWeatherDevice_1(qtbot):
    app.weather.name = 'test_mountwizzard'
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.showIndiNewWeatherDevice('test_mountwizzard')
        assert suc
    assert ['INDI weather device [test_mountwizzard] found', 0] == blocker.args


def test_showIndiNewWeatherDevice_2(qtbot):
    app.weather.name = 'snoop'
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.showIndiNewWeatherDevice('test_mountwizzard')
        assert suc
    assert ['INDI weather device snoops -> [test_mountwizzard]', 0] == blocker.args


def test_showIndiRemoveWeatherDevice(qtbot):
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.showIndiRemoveWeatherDevice('test_mountwizzard')
        assert suc
    assert ['INDI weather device [test_mountwizzard] removed', 0] == blocker.args


def test_showWeatherDeviceConnected():
    suc = app.mainW.showWeatherDeviceConnected()
    assert suc


def test_showWeatherDeviceDisconnected():
    suc = app.mainW.showWeatherDeviceDisconnected()
    assert suc
