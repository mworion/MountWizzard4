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
import pytest
import astropy

# external packages

# local import
from indibase.indiSignals import INDISignals


@pytest.fixture(autouse=True, scope='function')
def function():
    signals = INDISignals()
    yield signals


def test_indiSignals(function):
    a = INDISignals()
    assert a is not None