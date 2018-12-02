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
          'build': 'test',
          }


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    print("MODULE SETUP!!!")
    global spy
    global app

    app = mainApp.MountWizzard4(mwGlob=mwGlob)
    spy = PyQt5.QtTest.QSignalSpy(app.message)
    yield
    print("MODULE TEARDOWN!!!")
    spy = None
    app = None


#
#
# testing mainW gui booting shutdown
#
#


def test_resizeEvent(qtbot):
    app.hemisphereW.resizeEvent(None)


def test_closeEvent(qtbot):
    app.hemisphereW.closeEvent(None)


def test_toggleWindow1(qtbot):
    app.hemisphereW.showStatus = True
    with mock.patch.object(app.hemisphereW,
                           'close',
                           return_value=None):
        app.hemisphereW.toggleWindow()
        assert not app.hemisphereW.showStatus


def test_toggleWindow2(qtbot):
    app.hemisphereW.showStatus = False
    with mock.patch.object(app.hemisphereW,
                           'showWindow',
                           return_value=None):
        app.hemisphereW.toggleWindow()
        assert app.hemisphereW.showStatus


def test_showWindow1(qtbot):
    app.hemisphereW.showStatus = False
    app.hemisphereW.showWindow()
    assert app.hemisphereW.showStatus


def test_clearAxes1(qtbot):
    axes = app.hemisphereW.hemisphereMat.figure.axes[0]
    suc = app.hemisphereW.clearAxes(axes, True)
    assert suc


def test_clearAxes2(qtbot):
    axes = app.hemisphereW.hemisphereMat.figure.axes[0]
    suc = app.hemisphereW.clearAxes(axes, False)
    assert not suc
