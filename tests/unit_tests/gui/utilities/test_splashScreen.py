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
#
# written in python3, (c) 2019-2021 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPixmap
import pytest
import unittest.mock as mock

# local import
from gui.utilities.splashScreen import SplashScreen


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():

    with mock.patch.object(QWidget, 'show'):
        yield


def test_icon_1(qtbot):
    app = SplashScreen(QWidget())
    qtbot.addWidget(app)

    value = QPixmap(':/icon/mw4.ico')
    assert isinstance(value, QPixmap)


def test_icon_2(qtbot):
    app = SplashScreen(QWidget(), 100, 100)
    qtbot.addWidget(app)

    value = QPixmap(':/icon/mw4.ico')
    assert isinstance(value, QPixmap)


def test_upcoming(qtbot):
    app = SplashScreen(QWidget())
    qtbot.addWidget(app)

    app.showMessage('test')
    app.setValue(10)
    app.setValue(50)
    app.setValue(90)
    app.setValue(100)


def test_drawContents(qtbot):
    app = SplashScreen(QWidget())
    qtbot.addWidget(app)

    app.drawContents(QPainter())


def test_finish(qtbot):
    app = SplashScreen(QWidget())
    qtbot.addWidget(app)

    app.finish(QWidget())
