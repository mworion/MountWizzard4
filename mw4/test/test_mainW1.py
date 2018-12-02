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
# Python  v3.6.5
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
# external packages
import PyQt5.QtGui
import PyQt5.QtWidgets
import PyQt5.uic
import PyQt5.QtTest
import PyQt5.QtCore
# local import
from mw4 import mainApp

test = PyQt5.QtWidgets.QApplication([])

mwGlob = {'workDir': '.',
          'configDir': './mw4/test/config/',
          'build': 'test',
          }
app = mainApp.MountWizzard4(mwGlob=mwGlob)
spy = PyQt5.QtTest.QSignalSpy(app.message)


def test_indiHost():
    app.mainW.ui.indiHost.setText('TEST')
    app.mainW.indiHost()
    assert app.environment.client.host == ('TEST', 7624)


def test_localWeatherName():
    app.mainW.ui.localWeatherName.setText('TEST')
    app.mainW.localWeatherName()
    assert 'TEST' == app.environment.wDevice['local']['name']


def test_globalWeatherName():
    app.mainW.ui.globalWeatherName.setText('TEST')
    app.mainW.globalWeatherName()
    assert 'TEST' == app.environment.wDevice['global']['name']


def test_sqmWeatherName():
    app.mainW.ui.sqmName.setText('TEST')
    app.mainW.sqmName()
    assert 'TEST' == app.environment.wDevice['sqm']['name']


def test_newEnvironConnected(qtbot):
    with qtbot.waitSignal(app.message) as blocker:
        app.mainW.newEnvironDevice('test')
    assert ['INDI device [test] found', 0] == blocker.args


def test_indiEnvironConnected(qtbot):
    with qtbot.waitSignal(app.message) as blocker:
        app.mainW.indiEnvironConnected()
    assert ['INDI server environment connected', 0] == blocker.args


def test_indiEnvironDisconnected(qtbot):
    with qtbot.waitSignal(app.message) as blocker:
        app.mainW.indiEnvironDisconnected()
    assert ['INDI server environment disconnected', 0] == blocker.args
