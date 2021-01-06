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
# written in python3, (c) 2019-2021 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest

# external packages

# local import
from base import loggerMW


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global app

    yield


def test_timeTz():
    suc = loggerMW.timeTz()
    assert suc


def test_setupLogging():
    suc = loggerMW.setupLogging()
    assert suc


def test_setCustomLoggingLevel():
    suc = loggerMW.setCustomLoggingLevel()
    assert suc


