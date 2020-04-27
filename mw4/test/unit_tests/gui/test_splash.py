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
import faulthandler
faulthandler.enable()

# external packages
import PyQt5.QtGui
from PyQt5.QtWidgets import QWidget
import pytest

# local import
from mw4.gui.splash import SplashScreen


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():

    yield


def test_icon(qtbot):
    app = SplashScreen(QWidget())
    qtbot.addWidget(app)

    value = PyQt5.QtGui.QPixmap(':/icon/mw4.ico')
    assert not PyQt5.QtGui.QPixmap.isNull(value)


def test_upcoming(qtbot):
    app = SplashScreen(QWidget())
    qtbot.addWidget(app)

    app.showMessage('test')
    app.setValue(10)
    app.setValue(50)
    app.setValue(90)
    app.setValue(100)


def test_finish(qtbot):
    app = SplashScreen(QWidget())
    qtbot.addWidget(app)

    app.finish(QWidget())
