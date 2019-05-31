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
from mw4.test_units.test_setupQt import setupQt


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


def test_selectorGui():
    suc = app.mainW.setupSelectorGui()
    assert suc
    for _, ui in app.mainW.selectorsDropDowns.items():
        assert ui.count() == 7


def test_getNumberFiles_1():
    number = app.mainW.getNumberFiles()
    assert number == 0


def test_getNumberFiles_2():
    number = app.mainW.getNumberFiles(pathDir='/Users')
    assert number == 0


def test_getNumberFiles_3():
    number = app.mainW.getNumberFiles(pathDir='/Users/mw/PycharmProjects', includeSubdirs=True)
    assert number > 0


def test_convertHeaderEntry_1():
    chunk = app.mainW.convertHeaderEntry(entry='', fitsKey='')
    assert not chunk


def test_convertHeaderEntry_2():
    chunk = app.mainW.convertHeaderEntry(entry='2019-05-26T17:02:18.843', fitsKey='')
    assert not chunk


def test_convertHeaderEntry_3():
    chunk = app.mainW.convertHeaderEntry(entry='2019-05-26T17:02:18.843', fitsKey='DATE-OBS')
    assert chunk == '2019-05-26-17-02-18'


def test_convertHeaderEntry_4():
    chunk = app.mainW.convertHeaderEntry(entry='2019-05-26T17:02:18', fitsKey='DATE-OBS')
    assert chunk == '2019-05-26-17-02-18'
