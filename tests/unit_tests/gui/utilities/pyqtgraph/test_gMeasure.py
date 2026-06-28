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
# written in python3, (c) 2019-2026 by mworion
# License APL2.0
#
###########################################################

import pytest
from mw4.gui.utilities.pyqtgraph.gMeasure import Measure


@pytest.fixture(autouse=True, scope="module")
def module(qapp):
    yield


def test_Measure():
    Measure()
