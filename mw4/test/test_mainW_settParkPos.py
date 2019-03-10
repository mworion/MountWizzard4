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
import logging
import pytest
# external packages
import PyQt5.QtGui
import PyQt5.QtWidgets
import PyQt5.uic
import PyQt5.QtTest
import PyQt5.QtCore
# local import
from mw4 import mainApp
from mw4.test.test_setupQt import setupQt


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app, spy, mwGlob, test
    app, spy, mwGlob, test = setupQt()
    yield


def test_initConfig_1():
    app.config['mainW'] = {}
    suc = app.mainW.initConfig()
    assert suc


def test_initConfig_2():
    del app.config['mainW']
    suc = app.mainW.initConfig()
    assert suc


def test_storeConfig_1():
    suc = app.storeConfig()
    assert suc


def test_setupIcons():
    suc = app.mainW.setupIcons()
    assert suc


def test_clearGUI():
    suc = app.mainW.clearGUI()
    assert suc


def test_initConfig_1():
    config = app.config['mainW']
    for i in range(0, 8):
        config[f'posText{i:1d}'] = str(i)
        config[f'posAlt{i:1d}'] = str(i)
        config[f'posAz{i:1d}'] = str(i)
    app.mainW.initConfig()
    assert app.mainW.ui.posText0.text() == '0'
    assert app.mainW.ui.posAlt0.text() == '0'
    assert app.mainW.ui.posAz0.text() == '0'
    assert app.mainW.ui.posText4.text() == '4'
    assert app.mainW.ui.posAlt4.text() == '4'
    assert app.mainW.ui.posAz4.text() == '4'
    assert app.mainW.ui.posText7.text() == '7'
    assert app.mainW.ui.posAlt7.text() == '7'
    assert app.mainW.ui.posAz7.text() == '7'


def test_storeConfig_1():
    app.mainW.storeConfig()


def test_setupParkPosGui(qtbot):
    assert 8 == len(app.mainW.posButtons)
    assert 8 == len(app.mainW.posTexts)
    assert 8 == len(app.mainW.posAlt)
    assert 8 == len(app.mainW.posAz)

