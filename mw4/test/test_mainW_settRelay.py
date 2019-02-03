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


def test_setupRelayGui(qtbot):
    assert 8 == len(app.mainW.relayDropDownIndex)
    assert 8 == len(app.mainW.relayTexts)
    assert 8 == len(app.mainW.relayButtons)
    for dropDown in app.mainW.relayDropDownIndex:
        val = dropDown.count()
        assert 2 == val


def test_enableRelay2(qtbot):
    app.mainW.ui.checkEnableRelay.setChecked(False)
    with mock.patch.object(app.relay,
                           'startTimers',
                           return_value=None):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.enableRelay()
            assert suc
        assert ['Relay disabled', 0] == blocker.args


def test_toggleRelay1(qtbot):
    app.mainW.ui.checkEnableRelay.setChecked(False)
    with qtbot.waitSignal(app.message) as blocker:
        suc = app.mainW.toggleRelay()
        assert not suc
    assert ['Relay box off', 2] == blocker.args


def test_toggleRelay2(qtbot):
    app.mainW.ui.checkEnableRelay.setChecked(True)
    with mock.patch.object(app.relay,
                           'switch',
                           return_value=False):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.toggleRelay()
            assert not suc
        assert ['Relay cannot be switched', 2] == blocker.args


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
