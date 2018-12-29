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
import pytest
# external packages
import PyQt5.QtWidgets
import PyQt5.QtTest
import PyQt5.QtCore
# local import
from mw4 import mainApp

test = PyQt5.QtWidgets.QApplication([])

mwGlob = {'workDir': '.',
          'configDir': './mw4/test/config/',
          'dataDir': './mw4/test/config/',
          'modeldata': 'test',
          }

'''
@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global spy
    global app
    app = mainApp.MountWizzard4(mwGlob=mwGlob)
    spy = PyQt5.QtTest.QSignalSpy(app.message)
    yield
    spy = None
    app = None
'''
app = mainApp.MountWizzard4(mwGlob=mwGlob)
spy = PyQt5.QtTest.QSignalSpy(app.message)

#
#
# testing mainW gui booting shutdown
#
#


def test_resizeEvent(qtbot):
    app.messageW.resizeEvent(None)


def test_closeEvent(qtbot):
    app.messageW.closeEvent(None)


def test_toggleWindow1(qtbot):
    app.messageW.showStatus = True
    with mock.patch.object(app.messageW,
                           'close',
                           return_value=None):
        app.messageW.toggleWindow()
        assert not app.messageW.showStatus


def test_toggleWindow2(qtbot):
    app.messageW.showStatus = False
    with mock.patch.object(app.messageW,
                           'showWindow',
                           return_value=None):
        app.messageW.toggleWindow()
        assert app.messageW.showStatus


def test_showWindow1(qtbot):
    app.messageW.showStatus = False
    with mock.patch.object(app.messageW,
                           'show',
                           return_value=None):
        app.messageW.showWindow()
        assert app.messageW.showStatus


def test_writeMessage1(qtbot):
    app.messageW.ui.message.setText('')
    suc = app.messageW.writeMessage('test', 0)
    assert suc
    val = app.messageW.ui.message.toPlainText()
    assert val.endswith('test\n')


def test_writeMessage2(qtbot):
    app.messageW.ui.message.setText('')
    suc = app.messageW.writeMessage('test', 6)
    assert not suc


def test_writeMessage3(qtbot):
    app.messageW.ui.message.setText('')
    suc = app.messageW.writeMessage('', 0)
    assert suc
    val = app.messageW.ui.message.toPlainText()
    assert val.endswith('\n')


def test_writeMessage4(qtbot):
    app.messageW.ui.message.setText('')
    suc = app.messageW.writeMessage('test', -1)
    assert not suc
