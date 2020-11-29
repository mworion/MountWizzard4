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
# written in python3 , (c) 2019, 2020 by mworion
#
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest
import logging
# external packages

# local import
from base import loggerMW


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global app
    log = logging.getLogger(__name__)
    app = loggerMW.CustomLogger(logger, {})

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


def test_process():
    val, kwargs = app.process('test', '10')
    assert val == 'test'
    assert kwargs == '10'

