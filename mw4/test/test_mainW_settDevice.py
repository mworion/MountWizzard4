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


def test_enableRelay_1(qtbot):
    app.mainW.ui.relayDevice.setCurrentIndex(0)
    with mock.patch.object(app.relay,
                           'stopTimers',
                           return_value=None):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.enableRelay()
            assert suc
        assert ['Relay disabled', 2] == blocker.args


def test_enableRelay_2(qtbot):
    app.mainW.ui.relayDevice.setCurrentIndex(1)
    with mock.patch.object(app.relay,
                           'startTimers',
                           return_value=None):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.enableRelay()
            assert suc
        assert ['Relay enabled', 2] == blocker.args


def test_enableRemote_1(qtbot):
    app.mainW.ui.remoteDevice.setCurrentIndex(0)
    with mock.patch.object(app.remote,
                           'startRemote',
                           return_value=None):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.enableRemote()
            assert suc
        assert ['Remote disabled', 2] == blocker.args


def test_enableRemote_2(qtbot):
    app.mainW.ui.remoteDevice.setCurrentIndex(1)
    with mock.patch.object(app.remote,
                           'stopRemote',
                           return_value=None):
        with qtbot.waitSignal(app.message) as blocker:
            suc = app.mainW.enableRemote()
            assert suc
        assert ['Remote enabled', 2] == blocker.args



