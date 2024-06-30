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
# written in python3, (c) 2019-2024 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import time
import unittest.mock as mock
import pytest
import astropy

# external packages

# local import
from mw4.update import UpdateCLI, Update
from base.loggerMW import setupLogging

setupLogging()


def test_updateCLI_1():
    with mock.patch.object(Update,
                           'runInstall',
                           return_value=True):
        with mock.patch.object(Update,
                               'restart'):
            with mock.patch.object(time,
                                   'sleep'):
                UpdateCLI(runnable='python', version='1.2.3')


def test_updateCLI_2():
    with mock.patch.object(Update,
                           'runInstall',
                           return_value=False):
        with mock.patch.object(Update,
                               'restart'):
            with mock.patch.object(time,
                                   'sleep'):
                UpdateCLI(runnable='python', version='1.2.3')

