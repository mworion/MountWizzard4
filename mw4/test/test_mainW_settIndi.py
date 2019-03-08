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
    app = None


def test_indiHost():
    app.mainW.ui.indiHostEnvironment.setText('TEST')
    app.mainW.indiHostEnvironment()
    assert app.environment.client.host == ('TEST', 7624)


def test_localWeatherName():
    app.mainW.ui.localWeatherName.setText('TEST')
    app.mainW.localWeatherName()
    assert 'TEST' == app.environment.wDevice['local']['name']


def test_globalWeatherName():
    app.mainW.ui.globalWeatherName.setText('TEST')
    app.mainW.globalWeatherName()
    assert 'TEST' == app.environment.wDevice['global']['name']


def test_sqmWeatherName():
    app.mainW.ui.sqmName.setText('TEST')
    app.mainW.sqmName()
    assert 'TEST' == app.environment.wDevice['sqm']['name']

