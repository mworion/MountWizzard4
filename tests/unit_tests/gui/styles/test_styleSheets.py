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

import pytest
from mw4.gui.styles.styleSheets import BASIC_STYLE, MAC_STYLE, NON_MAC_STYLE


@pytest.fixture(autouse=True, scope="module")
def module(qapp):
    yield


def test_styleSheets_1():
    assert isinstance(MAC_STYLE, str)


def test_styleSheets_2():
    assert isinstance(NON_MAC_STYLE, str)


def test_styleSheets_3():
    assert isinstance(BASIC_STYLE, str)
