############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2025 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries
import pytest

# external packages
# local import
from mw4.indibase.indiSignals import INDISignals


@pytest.fixture(autouse=True, scope="function")
def function():
    signals = INDISignals()
    yield signals


def test_indiSignals(function):
    a = INDISignals()
    assert a is not None
