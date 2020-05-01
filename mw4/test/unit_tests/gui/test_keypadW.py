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
# written in python3 , (c) 2019, 2020 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import unittest.mock as mock
import pytest
import faulthandler
faulthandler.enable()

# external packages
from PyQt5.QtCore import QObject
from PyQt5.QtGui import QCloseEvent

# local import
from mw4.gui.keypadW import KeypadWindow
from mw4.gui.widget import MWidget


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global Test

    class Test(QObject):
        config = {'mainW': {}}

    yield


def test_initConfig_1(qtbot):
    app = KeypadWindow(app=Test())
    qtbot.addWidget(app)

    suc = app.initConfig()
    assert suc


def test_initConfig_2(qtbot):
    app = KeypadWindow(app=Test())
    qtbot.addWidget(app)

    app.app.config['keypadW'] = {'winPosX': 10000}
    suc = app.initConfig()
    assert suc


def test_initConfig_3(qtbot):
    app = KeypadWindow(app=Test())
    qtbot.addWidget(app)

    app.app.config['keypadW'] = {'winPosY': 10000}
    suc = app.initConfig()
    assert suc


def test_storeConfig_1(qtbot):
    app = KeypadWindow(app=Test())
    qtbot.addWidget(app)

    if 'keypadW' in app.app.config:
        del app.app.config['keypadW']
    suc = app.storeConfig()
    assert suc


def test_storeConfig_2(qtbot):
    app = KeypadWindow(app=Test())
    qtbot.addWidget(app)

    app.app.config['keypadW'] = {}
    suc = app.storeConfig()
    assert suc


def test_closeEvent_1(qtbot):
    app = KeypadWindow(app=Test())
    qtbot.addWidget(app)

    with mock.patch.object(MWidget,
                           'closeEvent',
                           return_value=True):
        app.closeEvent(QCloseEvent())


def test_loadFinished_1(qtbot):
    app = KeypadWindow(app=Test())
    qtbot.addWidget(app)

    app.loadFinished()


def test_showUrl_1(qtbot):
    app = KeypadWindow(app=Test())
    qtbot.addWidget(app)

    app.showUrl()


def test_showUrl_2(qtbot):
    app = KeypadWindow(app=Test())
    qtbot.addWidget(app)

    app.host = 'localhost'
    app.showUrl()
