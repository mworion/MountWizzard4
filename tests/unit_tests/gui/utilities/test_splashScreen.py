############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages
import unittest.mock as mock

import pytest

# local import
from gui.utilities.splashScreen import SplashScreen
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtWidgets import QWidget


@pytest.fixture(autouse=True, scope="function")
def module_setup_teardown():
    with mock.patch.object(QWidget, "show"):
        yield


def test_icon_1(qtbot):
    value = QPixmap(":/icon/mw4.ico")
    assert isinstance(value, QPixmap)


def test_icon_2(qtbot):
    value = QPixmap(":/icon/mw4.ico")
    assert isinstance(value, QPixmap)


def test_upcoming(qtbot):
    app = SplashScreen(QWidget())
    app.showMessage("test")
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
    with mock.patch.object(app, "update"):
        with mock.patch.object(app.qss, "close"):
            app.finish(QWidget())


def test_close(qtbot):
    app = SplashScreen(QWidget())
    with mock.patch.object(app, "update"):
        with mock.patch.object(app.qss, "close"):
            app.close()
