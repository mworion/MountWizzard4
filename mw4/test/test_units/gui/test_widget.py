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
# Michael Würtenberger
# (c) 2019
#
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import pytest
import platform
# external packages
from PyQt5.QtWidgets import QStyle
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QWidget
# local import
from mw4.test.test_units.setupQt import setupQt
from mw4.gui.widget import MWidget


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app, spy, mwGlob, test
    app, spy, mwGlob, test = setupQt()
    yield


def test_wIcon_1():
    suc = MWidget.wIcon()
    assert not suc


def test_wIcon_2():
    suc = MWidget.wIcon(QPushButton())
    assert not suc


def test_wIcon_3():
    suc = MWidget.wIcon(QPushButton(), QStyle.SP_ComputerIcon)
    assert suc


def test_getStyle_1():
    a = MWidget()
    with mock.patch.object(platform,
                           'system',
                           return_value='Darwin'):
        val = a.getStyle()
        assert val


def test_getStyle_2():
    a = MWidget()
    with mock.patch.object(platform,
                           'system',
                           return_value='Linux'):
        val = a.getStyle()
        assert val


def test_getStyle_3():
    a = MWidget()
    with mock.patch.object(platform,
                           'system',
                           return_value='Windows'):
        val = a.getStyle()
        assert val


def test_initUI():
    a = MWidget()
    suc = a.initUI()
    assert suc


def test_changeStyleDynamic_1():
    a = MWidget()
    suc = a.changeStyleDynamic()
    assert not suc


def test_changeStyleDynamic_2():
    a = MWidget()
    suc = a.changeStyleDynamic(QPushButton())
    assert not suc


def test_changeStyleDynamic_3():
    a = MWidget()
    suc = a.changeStyleDynamic(QPushButton(), 'test')
    assert not suc


def test_changeStyleDynamic_4():
    a = MWidget()
    suc = a.changeStyleDynamic(QPushButton(), 'test', 'true')
    assert suc


def test_clearPolar_1():
    a = MWidget()
    fig, axe = a.clearPolar()

    assert fig is None
    assert axe is None


def test_clearPolar_2():
    a = MWidget()
    fig, axe = a.clearPolar(QWidget())

    assert fig is None
    assert axe is None


def test_clearPolar_3():
    a = MWidget()
    b = QWidget()
    c = a.embedMatplot(b)

    fig, axe = a.clearPolar(c)

    assert fig is not None
    assert axe is not None


def test_embedMatplot_1():
    a = MWidget()
    b = QWidget()

    c = a.embedMatplot()

    assert c is None


def test_embedMatplot_2():
    a = MWidget()
    b = QWidget()

    c = a.embedMatplot(b)

    assert c is not None
