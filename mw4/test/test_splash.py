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
# external packages
import PyQt5.QtGui
import PyQt5.QtWidgets
import pytest
# local import
from mw4.gui import splash
from mw4.test.test_setupQt import setupQt


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app, spy, mwGlob, test
    app, spy, mwGlob, test = setupQt()
    yield


def test_splash_icon():
    value = PyQt5.QtGui.QPixmap(':/mw4.ico')

    assert not PyQt5.QtGui.QPixmap.isNull(value)


def test_splash_upcoming():
    splashW = splash.SplashScreen(test)
    splashW.showMessage('test')
    splashW.setValue(10)
    splashW.setValue(50)
    splashW.setValue(90)
    splashW.setValue(100)
