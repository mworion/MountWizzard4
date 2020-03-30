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
import sys

# external packages
import pytest
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication

# local import
from mw4.loader import MyApp

global test
app = MyApp(sys.argv)


@pytest.fixture(autouse=True, scope="function")
def setup_teardown():

    yield



def test_handleButtons_1():
    ui = QtWidgets.QTabBar()

    val = app.handleButtons(obj=ui, returnValue=10)
    assert val == 10


def test1():
    pass


def test2():
    pass


def test3():
    pass


def test4():
    pass
