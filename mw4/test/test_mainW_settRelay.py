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
app, spy, mwGlob, test = setupQt()


def test_storeConfig_1():
    app.mainW.storeConfig()


def test_setupRelayGui(qtbot):
    assert 8 == len(app.mainW.relayDropDowns)
    assert 8 == len(app.mainW.relayButtonTexts)
    assert 8 == len(app.mainW.relayButtons)
    for dropDown in app.mainW.relayDropDowns:
        val = dropDown.count()
        assert 2 == val


def test_toggleRelay1(qtbot):
    app.mainW.ui.checkEnableRelay.setChecked(False)
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.relayButtonPressed()
        assert not suc
    assert ['Relay box off', 2] == blocker.args


def test_toggleRelay2(qtbot):
    app.mainW.ui.checkEnableRelay.setChecked(True)
    with mock.patch.object(app.relay,
                           'switch',
                           return_value=False):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.relayButtonPressed()
            assert not suc
        assert ['Relay action cannot be performed', 2] == blocker.args


def test_relayHost():
    app.mainW.ui.relayHost.setText('test')
    app.mainW.relayHost()

    assert app.relay.host == ('test', 80)


def test_relayUser():
    app.mainW.ui.relayUser.setText('test')
    app.mainW.relayUser()

    assert app.relay.user == 'test'


def test_relayPassword():
    app.mainW.ui.relayPassword.setText('test')
    app.mainW.relayPassword()

    assert app.relay.password == 'test'


def test_enableRelay_1(qtbot):
    app.mainW.ui.checkEnableRelay.setChecked(True)

    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.enableRelay()
        assert suc
        assert ['Relay enabled', 0] == blocker.args


def test_enableRelay_2(qtbot):
    app.mainW.ui.checkEnableRelay.setChecked(False)

    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.enableRelay()
        assert suc
        assert ['Relay disabled', 0] == blocker.args


def test_doRelayAction_1(qtbot):
    app.mainW.relayDropDowns[7].setCurrentIndex(0)
    with mock.patch.object(app.relay,
                           'switch',
                           return_value=False):
        suc = app.mainW.doRelayAction(7)
        assert not suc


def test_doRelayAction_2(qtbot):
    app.mainW.relayDropDowns[7].setCurrentIndex(0)
    with mock.patch.object(app.relay,
                           'switch',
                           return_value=True):
        suc = app.mainW.doRelayAction(7)
        assert suc


def test_doRelayAction_3(qtbot):
    app.mainW.relayDropDowns[7].setCurrentIndex(2)
    suc = app.mainW.doRelayAction(7)
    assert not suc


def test_doRelayAction_4(qtbot):
    app.mainW.relayDropDowns[7].setCurrentIndex(1)
    with mock.patch.object(app.relay,
                           'pulse',
                           return_value=False):
        suc = app.mainW.doRelayAction(7)
        assert not suc


def test_doRelayAction_5(qtbot):
    app.mainW.relayDropDowns[7].setCurrentIndex(1)
    with mock.patch.object(app.relay,
                           'pulse',
                           return_value=True):
        suc = app.mainW.doRelayAction(7)
        assert suc
