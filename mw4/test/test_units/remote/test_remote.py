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


def test_startRemote_1():
    suc = app.remote.startCommunication()
    assert suc


def test_stopRemote_1():
    app.remote.tcpServer = '1'
    suc = app.remote.stopCommunication()
    assert suc


def test_addConnection_1():
    app.remote.tcpServer = None
    suc = app.remote.addConnection()
    assert not suc


def test_receiveMessage_1():
    pass


def test_removeConnection_1():
    pass


def test_handleError_1():
    pass
