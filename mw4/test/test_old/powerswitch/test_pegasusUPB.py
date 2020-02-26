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
from unittest import mock
import pytest
# external packages
# local import
from mw4.test.test_old.setupQt import setupQt

host_ip = 'astro-mount.fritz.box'


@pytest.fixture(autouse=True, scope='module')
def module_setup_teardown():
    global app, spy, mwGlob, test
    app, spy, mwGlob, test = setupQt()


def test_name():
    name = 'PegasusUPB'
    app.power.name = name
    assert name == app.power.name


def test_startCommunication_1():
    app.power.name = ''
    with mock.patch.object(app.power.run['indi'].client,
                           'connectServer',
                           return_value=False):
        suc = app.power.startCommunication()
        assert not suc
