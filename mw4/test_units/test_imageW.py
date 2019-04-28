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
import unittest.mock as mock
import pytest
# external packages
import PyQt5.QtWidgets
import PyQt5.QtTest
import PyQt5.QtCore
# local import
from mw4 import mainApp
from mw4.test_units.test_setupQt import setupQt


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app, spy, mwGlob, test
    app, spy, mwGlob, test = setupQt()
    yield


@pytest.fixture(autouse=True, scope='function')
def function():
    app.config['showImageWindow'] = True
    app.toggleImageWindow()
    yield
    app.imageW = None
    app.config['showImageWindow'] = False


def test_storeConfig_1():
    app.imageW.storeConfig()


def test_initConfig_1():
    app.config['imageW'] = {}
    suc = app.imageW.initConfig()
    assert suc


def test_initConfig_2():
    del app.config['imageW']
    suc = app.imageW.initConfig()
    assert not suc


def test_initConfig_3():
    app.config['imageW'] = {}
    app.config['imageW']['winPosX'] = 10000
    app.config['imageW']['winPosY'] = 10000
    suc = app.imageW.initConfig()
    assert suc


def test_showWindow_1(qtbot):
    with mock.patch.object(app.imageW,
                           'show',
                           return_value=None):
        suc = app.imageW.showWindow()
        assert suc


def test_setupDropDownGui():
    app.imageW.setupDropDownGui()
