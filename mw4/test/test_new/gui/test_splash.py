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
# Python  v3.7.5
#
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages
import PyQt5.QtGui
from PyQt5.QtWidgets import QWidget
import pytest

# local import
from mw4.gui.splash import SplashScreen


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app
    app = SplashScreen(QWidget())
    yield
    del app


def test_splash_icon():
    value = PyQt5.QtGui.QPixmap(':/icon/mw4.ico')

    assert not PyQt5.QtGui.QPixmap.isNull(value)


def test_splash_upcoming():
    app.showMessage('test')
    app.setValue(10)
    app.setValue(50)
    app.setValue(90)
    app.setValue(100)
