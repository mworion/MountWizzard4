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
# GUI with PySide for python
#
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import sys
import os
import logging
from unittest import mock

# external packages

# local import
from mw4.base import loggerMW
from mw4.base.loggerMW import LoggerWriter


def test_loggerWriter():
    a = LoggerWriter(logging.getLogger().debug, 'Test', sys.stdout)
    a.write('test\ntest')


def test_setupLogging():
    with mock.patch.object(os.path,
                           'isdir',
                           return_value=False):
        with mock.patch.object(os,
                               'mkdir'):
            loggerMW.setupLogging()


def test_setCustomLoggingLevel():
    loggerMW.setCustomLoggingLevel()


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
    loggerTest.warning('test')
