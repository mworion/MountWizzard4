############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
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
from gui.extWindows.image.imageSignals import ImageWindowSignals


@pytest.fixture(autouse=True, scope="module")
def function():
    func = ImageWindowSignals()
    yield func


def test_init(function):
    assert function
