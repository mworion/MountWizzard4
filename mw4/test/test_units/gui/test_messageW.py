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
import pytest
# external packages
# local import
from mw4.test.test_units.setupQt import setupQt


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app, spy, mwGlob, test
    app, spy, mwGlob, test = setupQt()
    app.config['showMessageWindow'] = True
    app.toggleWindow(windowTag='showMessageW')
    yield


def test_initConfig_1():
    app.config['messageW'] = {}
    suc = app.uiWindows['showMessageW']['classObj'].initConfig()
    assert suc


def test_initConfig_2():
    del app.config['messageW']
    suc = app.uiWindows['showMessageW']['classObj'].initConfig()
    assert suc


def test_initConfig_3():
    app.config['messageW'] = {}
    app.config['messageW']['winPosX'] = 10000
    app.config['messageW']['winPosY'] = 10000
    suc = app.uiWindows['showMessageW']['classObj'].initConfig()
    assert suc


def test_storeConfig():
    app.uiWindows['showMessageW']['classObj'].storeConfig()


def test_resizeEvent(qtbot):
    app.uiWindows['showMessageW']['classObj'].resizeEvent(None)


def test_clearWindow():
    app.uiWindows['showMessageW']['classObj'].clearWindow()


def test_writeMessage1(qtbot):
    app.uiWindows['showMessageW']['classObj'].ui.message.setText('')
    app.messageQueue.put(('test', 0))
    suc = app.uiWindows['showMessageW']['classObj'].writeMessage()
    assert suc
    val = app.uiWindows['showMessageW']['classObj'].ui.message.toPlainText()
    assert val.endswith('test\n')


def test_writeMessage2(qtbot):
    app.uiWindows['showMessageW']['classObj'].ui.message.setText('')
    app.messageQueue.put(('test', 6))
    suc = app.uiWindows['showMessageW']['classObj'].writeMessage()
    assert suc


def test_writeMessage3(qtbot):
    app.uiWindows['showMessageW']['classObj'].ui.message.setText('')
    app.messageQueue.put(('', 0))
    suc = app.uiWindows['showMessageW']['classObj'].writeMessage()
    assert suc
    val = app.uiWindows['showMessageW']['classObj'].ui.message.toPlainText()
    assert val.endswith('\n')


def test_writeMessage4(qtbot):
    app.uiWindows['showMessageW']['classObj'].ui.message.setText('')
    app.messageQueue.put(('test', -1))
    suc = app.uiWindows['showMessageW']['classObj'].writeMessage()
    assert suc
