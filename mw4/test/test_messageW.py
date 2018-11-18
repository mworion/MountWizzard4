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
import locale
# external packages
import PyQt5.QtWidgets
import PyQt5.QtTest
import PyQt5.QtCore
# local import
from mw4 import mainApp

test = PyQt5.QtWidgets.QApplication([])

mwGlob = {'workDir': '.',
          'configDir': './mw4/test/config/',
          'build': 'test',
          }
test_app = mainApp.MountWizzard4(mwGlob=mwGlob)
spy = PyQt5.QtTest.QSignalSpy(test_app.message)


#
#
# testing mainW gui booting shutdown
#
#


def test_resizeEvent(qtbot):
    test_app.messageW.resizeEvent(None)


def test_closeEvent(qtbot):
    test_app.messageW.closeEvent(None)


def test_toggleWindow1(qtbot):
    test_app.messageW.showStatus = True
    with mock.patch.object(test_app.messageW,
                           'close',
                           return_value=None):
        test_app.messageW.toggleWindow()
        assert not test_app.messageW.showStatus


def test_toggleWindow2(qtbot):
    test_app.messageW.showStatus = False
    with mock.patch.object(test_app.messageW,
                           'showWindow',
                           return_value=None):
        test_app.messageW.toggleWindow()
        assert test_app.messageW.showStatus


def test_showWindow1(qtbot):
    test_app.messageW.showStatus = False
    with mock.patch.object(test_app.messageW,
                           'show',
                           return_value=None):
        test_app.messageW.showWindow()
        assert test_app.messageW.showStatus


def test_writeMessage1(qtbot):
    test_app.messageW.ui.message.setText('')
    suc = test_app.messageW.writeMessage('test', 0)
    assert suc
    val = test_app.messageW.ui.message.toPlainText()
    assert val.endswith('test\n')


def test_writeMessage2(qtbot):
    test_app.messageW.ui.message.setText('')
    suc = test_app.messageW.writeMessage('test', 6)
    assert not suc


def test_writeMessage3(qtbot):
    test_app.messageW.ui.message.setText('')
    suc = test_app.messageW.writeMessage('', 0)
    assert suc
    val = test_app.messageW.ui.message.toPlainText()
    assert val.endswith('\n')


def test_writeMessage4(qtbot):
    test_app.messageW.ui.message.setText('')
    suc = test_app.messageW.writeMessage('test', -1)
    assert not suc


