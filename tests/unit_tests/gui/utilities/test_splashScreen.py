############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################



import unittest.mock as mock

import pytest
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtWidgets import QWidget


from mw4.gui.utilities.splashScreen import SplashScreen


@pytest.fixture(autouse=True, scope="module")
def module_setup_teardown():
    with mock.patch.object(QWidget, "show"):
        yield


def test_icon_1():
    value = QPixmap(":/icon/mw4.ico")
    assert isinstance(value, QPixmap)


def test_icon_2():
    value = QPixmap(":/icon/mw4.ico")
    assert isinstance(value, QPixmap)


def test_upcoming():
    app = SplashScreen(QWidget())
    app.showMessage("test")
    app.setValue(10)
    app.setValue(50)
    app.setValue(90)
    app.setValue(100)


def test_drawContents():
    app = SplashScreen(QWidget())
    app.drawContents(QPainter())


def test_finish():
    app = SplashScreen(QWidget())
    app.finish(QWidget())


def test_init():
    SplashScreen(QWidget(), 100, 100)


def test_finish():
    app = SplashScreen(QWidget())
    with mock.patch.object(app, "update"):
        with mock.patch.object(app.qss, "finish"):
            app.finish(QWidget())


def test_close():
    app = SplashScreen(QWidget())
    with mock.patch.object(app, "update"):
        with mock.patch.object(app.qss, "close"):
            app.close()
