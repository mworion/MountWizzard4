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
# written in python3, (c) 2019-2023 by mworion
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
    value = QPixmap(':/icon/mw4.ico')
    assert isinstance(value, QPixmap)


def test_icon_2(qtbot):
    value = QPixmap(':/icon/mw4.ico')
    assert isinstance(value, QPixmap)


def test_upcoming(qtbot):
    app = SplashScreen(QWidget())
    app.showMessage('test')
    app.setValue(10)
    app.setValue(50)
    app.setValue(90)
    app.setValue(100)


def test_drawContents(qtbot):
    app = SplashScreen(QWidget())
    app.drawContents(QPainter())


def test_finish(qtbot):
    app = SplashScreen(QWidget())
    app.finish(QWidget())


def test_init():
    SplashScreen(QWidget(), 100, 100)


def test_finish(qtbot):
    app = SplashScreen(QWidget())
    with mock.patch.object(app, 'update'):
        with mock.patch.object(app.qss, 'close'):
            app.finish(QWidget())


def test_close(qtbot):
    app = SplashScreen(QWidget())
    with mock.patch.object(app, 'update'):
        with mock.patch.object(app.qss, 'close'):
            app.close()
