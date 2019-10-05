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


def test_initConfig_1():
    config = app.config['mainW']
    for i in range(0, 8):
        config[f'posText{i:1d}'] = str(i)
        config[f'posAlt{i:1d}'] = str(i)
        config[f'posAz{i:1d}'] = str(i)
    app.mainW.initConfig()
    assert app.mainW.ui.posText0.text() == '0'
    assert app.mainW.ui.posAlt0.text() == '0'
    assert app.mainW.ui.posAz0.text() == '0'
    assert app.mainW.ui.posText4.text() == '4'
    assert app.mainW.ui.posAlt4.text() == '4'
    assert app.mainW.ui.posAz4.text() == '4'
    assert app.mainW.ui.posText7.text() == '7'
    assert app.mainW.ui.posAlt7.text() == '7'
    assert app.mainW.ui.posAz7.text() == '7'


def test_storeConfig_1():
    app.mainW.storeConfig()


def test_setupParkPosGui(qtbot):
    assert 8 == len(app.mainW.posButtons)
    assert 8 == len(app.mainW.posTexts)
    assert 8 == len(app.mainW.posAlt)
    assert 8 == len(app.mainW.posAz)



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
