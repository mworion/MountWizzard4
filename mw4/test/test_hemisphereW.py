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
    test_app.hemisphereW.resizeEvent(None)


def test_closeEvent(qtbot):
    test_app.hemisphereW.closeEvent(None)


def test_toggleWindow1(qtbot):
    test_app.hemisphereW.showStatus = True
    with mock.patch.object(test_app.hemisphereW,
                           'close',
                           return_value=None):
        test_app.hemisphereW.toggleWindow()
        assert not test_app.hemisphereW.showStatus


def test_toggleWindow2(qtbot):
    test_app.hemisphereW.showStatus = False
    with mock.patch.object(test_app.hemisphereW,
                           'showWindow',
                           return_value=None):
        test_app.hemisphereW.toggleWindow()
        assert test_app.hemisphereW.showStatus


def test_showWindow1(qtbot):
    test_app.hemisphereW.showStatus = False
    test_app.hemisphereW.showWindow()
    assert test_app.hemisphereW.showStatus


def test_clearAxes1(qtbot):
    axes = test_app.hemisphereW.hemisphereMat.figure.axes[0]
    suc = test_app.hemisphereW.clearAxes(axes, True)
    assert suc


def test_clearAxes2(qtbot):
    axes = test_app.hemisphereW.hemisphereMat.figure.axes[0]
    suc = test_app.hemisphereW.clearAxes(axes, False)
    assert not suc
