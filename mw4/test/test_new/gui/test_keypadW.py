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

# external packages
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtCore import QObject
from PyQt5.QtGui import QCloseEvent

# local import
from mw4.gui.keypadW import KeypadWindow


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    class Test(QObject):
        config = {'mainW': {}}

    global app
    app = KeypadWindow(app=Test())
    yield
    del app


def test_storeConfig_1():
    suc = app.storeConfig()
    assert suc


def test_closeEvent_1():
    app.closeEvent(QCloseEvent())


def test_loadFinished_1():
    app.loadFinished()


def test_showUrl_1():
    app.showUrl()


def test_showUrl_2():
    app.host = 'localhost'
    app.showUrl()
