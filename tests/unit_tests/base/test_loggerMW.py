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
    a = LoggerWriter(logging.getLogger().debug, "Test", sys.stdout)
    a.write("test\ntest")
    a.flush()


def test_setupLogging():
    with mock.patch.object(os.path, "isdir", return_value=False):
        with mock.patch.object(os, "mkdir"):
            loggerMW.setupLogging()


def test_setCustomLoggingLevel():
    loggerMW.setCustomLoggingLevel()
