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
from gui.extWindows.simulator.materials import Materials


@pytest.fixture(autouse=True, scope="module")
def module_setup_teardown():
    global app
    app = Materials()
    yield


def test_1():
    assert app.white
