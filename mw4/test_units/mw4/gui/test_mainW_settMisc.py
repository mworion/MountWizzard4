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
import logging
import pytest
# external packages
# local import
from mw4.test_units.mw4.test_setupQt import setupQt


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


def test_setLoggingLevelIB1(qtbot):
    app.mainW.ui.loglevelDebugIB.setChecked(True)
    app.mainW.setLoggingLevelIB()
    val = logging.getLogger('indibase').getEffectiveLevel()
    assert val == 10


def test_setLoggingLevelIB2(qtbot):
    app.mainW.ui.loglevelInfoIB.setChecked(True)
    app.mainW.setLoggingLevelIB()
    val = logging.getLogger('indibase').getEffectiveLevel()
    assert val == 20


def test_setLoggingLevelIB3(qtbot):
    app.mainW.ui.loglevelWarningIB.setChecked(True)
    app.mainW.setLoggingLevelIB()
    val = logging.getLogger('indibase').getEffectiveLevel()
    assert val == 30


def test_setLoggingLevelIB4(qtbot):
    app.mainW.ui.loglevelErrorIB.setChecked(True)
    app.mainW.setLoggingLevelIB()
    val = logging.getLogger('indibase').getEffectiveLevel()
    assert val == 40


def test_setLoggingLevelMC1(qtbot):
    app.mainW.ui.loglevelDebugMC.setChecked(True)
    app.mainW.setLoggingLevelMC()
    val = logging.getLogger('mountcontrol').getEffectiveLevel()
    assert val == 10


def test_setLoggingLevelMC2(qtbot):
    app.mainW.ui.loglevelInfoMC.setChecked(True)
    app.mainW.setLoggingLevelMC()
    val = logging.getLogger('mountcontrol').getEffectiveLevel()
    assert val == 20


def test_setLoggingLevelMC3(qtbot):
    app.mainW.ui.loglevelWarningMC.setChecked(True)
    app.mainW.setLoggingLevelMC()
    val = logging.getLogger('mountcontrol').getEffectiveLevel()
    assert val == 30


def test_setLoggingLevelMC4(qtbot):
    app.mainW.ui.loglevelErrorMC.setChecked(True)
    app.mainW.setLoggingLevelMC()
    val = logging.getLogger('mountcontrol').getEffectiveLevel()
    assert val == 40


def test_updateFwGui_productName():
    value = 'Test1234'
    app.mount.fw.productName = value
    app.mainW.updateFwGui(app.mount.fw)
    assert value == app.mainW.ui.productName.text()
    value = None
    app.mount.fw.productName = value
    app.mainW.updateFwGui(app.mount.fw)
    assert '-' == app.mainW.ui.productName.text()


def test_updateFwGui_hwVersion():
    value = 'Test1234'
    app.mount.fw.hwVersion = value
    app.mainW.updateFwGui(app.mount.fw)
    assert value == app.mainW.ui.hwVersion.text()
    value = None
    app.mount.fw.hwVersion = value
    app.mainW.updateFwGui(app.mount.fw)
    assert '-' == app.mainW.ui.hwVersion.text()


def test_updateFwGui_numberString():
    value = '2.15.18'
    app.mount.fw.numberString = value
    app.mainW.updateFwGui(app.mount.fw)
    assert value == app.mainW.ui.numberString.text()
    value = None
    app.mount.fw.numberString = value
    app.mainW.updateFwGui(app.mount.fw)
    assert '-' == app.mainW.ui.numberString.text()


def test_updateFwGui_fwdate():
    value = 'Test1234'
    app.mount.fw.fwdate = value
    app.mainW.updateFwGui(app.mount.fw)
    assert value == app.mainW.ui.fwdate.text()
    value = None
    app.mount.fw.fwdate = value
    app.mainW.updateFwGui(app.mount.fw)
    assert '-' == app.mainW.ui.fwdate.text()


def test_updateFwGui_fwtime():
    value = 'Test1234'
    app.mount.fw.fwtime = value
    app.mainW.updateFwGui(app.mount.fw)
    assert value == app.mainW.ui.fwtime.text()
    value = None
    app.mount.fw.fwtime = value
    app.mainW.updateFwGui(app.mount.fw)
    assert '-' == app.mainW.ui.fwtime.text()
