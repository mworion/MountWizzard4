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
from mw4.gui.styles.gradients import gradients


@pytest.fixture(autouse=True, scope="module")
def module(qapp):
    yield


def test_gradients_1():
    assert len(gradients) == 2
