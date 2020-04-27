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
import logging
import faulthandler
faulthandler.enable()

# external packages

# local import
from mw4.base import loggerMW


@pytest.fixture(autouse=True, scope='function')
def module_setup_teardown():
    global app
    logger = logging.getLogger(__name__)
    app = loggerMW.CustomLogger(logger, {})

    yield


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

