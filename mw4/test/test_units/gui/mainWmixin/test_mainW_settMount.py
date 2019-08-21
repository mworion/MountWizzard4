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
# Python  v3.7.4
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
# local import
from mw4.test.test_units.setupQt import setupQt


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
    app.mainW.storeConfig()


def test_setupIcons():
    suc = app.mainW.setupIcons()
    assert suc


def test_mountHost():
    app.mainW.ui.mountHost.setText('test')
    app.mainW.mountHost()

    assert app.mount.host == ('test', 3492)


def test_mountMAC():
    app.mainW.ui.mountMAC.setText('00:00:00:00:00:00')
    app.mainW.mountMAC()

    assert app.mount.MAC == '00:00:00:00:00:00'


