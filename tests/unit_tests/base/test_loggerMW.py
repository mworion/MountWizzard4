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
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import sys
import os

import pytest
import logging
from unittest import mock

# external packages

# local import
from base import loggerMW
from base.loggerMW import LoggerWriter


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global app
    yield


def test_loggerWriter():
    a = LoggerWriter(logging.getLogger().debug, 'Test', sys.stdout)
    a.write('asdfahdf\najdfhasf')
    a.flush()


def test_setupLogging():
    with mock.patch.object(os.path,
                           'isdir',
                           return_value=False):
        with mock.patch.object(os,
                               'mkdir'):
            suc = loggerMW.setupLogging()
            assert suc


def test_setCustomLoggingLevel():
    suc = loggerMW.setCustomLoggingLevel()
    assert suc


def test_addLoggingLevel_1():
    setattr(logging, 'T1', None)
    loggerMW.addLoggingLevel('T1', 31)


def test_addLoggingLevel_2():
    setattr(logging, 'M1', None)
    loggerMW.addLoggingLevel('T2', 32, 'M1')


def test_addLoggingLevel_3():
    class Test:
        M2 = None

    with mock.patch.object(logging,
                           'getLoggerClass',
                           return_value=Test()):
        loggerMW.addLoggingLevel('T3', 33, 'M2')


def test_addLoggingLevel_4():
    loggerMW.addLoggingLevel('Test', 65)
    loggerTest = logging.getLogger('test')
    loggerTest.setLevel(60)
    loggerTest.test('test')
