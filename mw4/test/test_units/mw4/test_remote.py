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
# Python  v3.7.3
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
from test.test_units import setupQt


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app, spy, mwGlob, test
    app, spy, mwGlob, test = setupQt()


def test_startRemote_1():
    class Test:
        @staticmethod
        def nextPendingConnection():
            return 0
    app.remote.tcpServer = Test()
    suc = app.remote.startRemote()
    assert not suc


def test_addConnection_1():
    app.remote.tcpServer = None
    suc = app.remote.addConnection()
    assert not suc


def test_addConnection_2():
    class Test:
        @staticmethod
        def nextPendingConnection():
            return 0
    app.remote.tcpServer = Test()
    suc = app.remote.addConnection()
    assert not suc

