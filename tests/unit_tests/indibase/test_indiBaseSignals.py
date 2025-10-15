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
import pytest
import unittest.mock as mock

# external packages
from PyQt5.QtCore import QObject, pyqtSignal

# local import
from mw4.indibase.indiBase import INDISignals


@pytest.fixture(autouse=True, scope='function')
def function():
    signals = INDISignals()
    yield signals


def test_indiSignals(function):
    a = INDISignals()
    assert a is not None
