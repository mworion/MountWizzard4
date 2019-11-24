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
import unittest.mock as mock
import pytest
import platform
# external packages
import PyQt5.QtWidgets
import PyQt5.QtTest
import PyQt5.QtCore
# local import
from mw4.test.test_units.setupQt import setupQt


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app, spy, mwGlob, test
    app, spy, mwGlob, test = setupQt()
    yield


def test_wIcon_1():
    ui = app.mainW.ui.openMessageW
    icon = PyQt5.QtWidgets.QStyle.SP_ComputerIcon

    suc = app.mainW.wIcon(ui, icon)
    assert suc


def test_getStyle_1():
    with mock.patch.object(platform,
                           'system',
                           return_value='Darwin'):
        ret = app.mainW.getStyle()
        assert ret == app.mainW.MAC_STYLE + app.mainW.BASIC_STYLE


def test_getStyle_2():
    with mock.patch.object(platform,
                           'system',
                           return_value='Windows'):
        ret = app.mainW.getStyle()
        assert ret == app.mainW.NON_MAC_STYLE + app.mainW.BASIC_STYLE


def test_initUI_1():
    suc = app.mainW.initUI()
    assert suc


def test_changeStyleDynamic_1():
    ui = app.mainW.ui.openMessageW
    suc = app.mainW.changeStyleDynamic(ui, 'color', 'red')
    assert suc


def test_clearPolar_1():
    ui = app.mainW.ui.modelPolar
    widget = app.mainW.embedMatplot(ui)

    fig, axes = app.mainW.clearPolar(widget)
    assert fig
    assert axes


def test_embedMatplot():
    ui = app.mainW.ui.modelPolar
    ret = app.mainW.embedMatplot(ui)
    assert ret


def test_extractNames_1():
    name = ''
    name, short, ext = app.mainW.extractNames(name)
    assert name == ''
    assert short == ''
    assert ext == ''


def test_extractNames_2():
    name = ['test']
    name, short, ext = app.mainW.extractNames(name)
    assert name == 'test'
    assert short == 'test'
    assert ext == ''


def test_extractNames_3():
    name = ['c:/test']
    name, short, ext = app.mainW.extractNames(name)
    assert name == 'c:/test'
    assert short == 'test'
    assert ext == ''


def test_extractNames_4():
    name = ['c:/test.cfg']
    name, short, ext = app.mainW.extractNames(name)
    assert name == 'c:/test.cfg'
    assert short == 'test'
    assert ext == '.cfg'


def test_extractNames_5():
    name = ['c:/test.cfg', 'c:/test.cfg']
    name, short, ext = app.mainW.extractNames(name)
    assert name == ['c:/test.cfg', 'c:/test.cfg']
    assert short == ['test', 'test']
    assert ext == ['.cfg', '.cfg']
