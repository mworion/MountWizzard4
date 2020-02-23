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
import unittest.mock as mock
import pytest
# external packages
import wakeonlan
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
    app.mainW.storeConfig()


def test_setupIcons():
    suc = app.mainW.setupIcons()
    assert suc


def test_checkFormatMAC_1():
    val = app.mainW.checkFormatMAC('')
    assert val is None


def test_checkFormatMAC_2():
    val = app.mainW.checkFormatMAC(5)
    assert val is None


def test_checkFormatMAC_3():
    val = app.mainW.checkFormatMAC('test')
    assert val is None


def test_checkFormatMAC_4():
    val = app.mainW.checkFormatMAC('00:00:00')
    assert val is None


def test_checkFormatMAC_5():
    val = app.mainW.checkFormatMAC('00:00:00:00.00.kk')
    assert val is None


def test_checkFormatMAC_6():
    val = app.mainW.checkFormatMAC('00.11.22:ab:44:55')
    assert val == '00:11:22:AB:44:55'


def test_bootRackComp_1():
    with mock.patch.object(wakeonlan,
                           'send_magic_packet',
                           return_value=False):
        suc = app.mainW.bootRackComp()
        assert not suc


def test_bootRackComp_2():
    with mock.patch.object(wakeonlan,
                           'send_magic_packet',
                           return_value=True):
        suc = app.mainW.bootRackComp()
        assert not suc


def test_mountHost():
    app.mainW.ui.mountHost.setText('test')
    app.mainW.mountHost()

    assert app.mount.host == ('test', 3492)


def test_mountMAC():
    app.mainW.ui.mountMAC.setText('00:00:00:00:00:00')
    app.mainW.mountMAC()

    assert app.mount.MAC == '00:00:00:00:00:00'


def test_setMountMAC_1():
    suc = app.mainW.setMountMAC()
    assert not suc


def test_setMountMAC_2():
    class Test:
        addressLanMAC = None
        typeConnection = 0
    suc = app.mainW.setMountMAC(Test())
    assert not suc


def test_setMountMAC_3():
    class Test:
        addressLanMAC = ''
        typeConnection = 0
    suc = app.mainW.setMountMAC(Test())
    assert not suc


def test_setMountMAC_4():
    class Test:
        addressLanMAC = None
        typeConnection = 0
    app.mount.MAC = None
    suc = app.mainW.setMountMAC(Test())
    assert not suc


def test_setMountMAC_6():
    class Test:
        addressLanMAC = '00:00:00:00:00:00'
        typeConnection = 3
    app.mount.MAC = '00:00:00:00:00:00'
    suc = app.mainW.setMountMAC(Test())
    assert suc
