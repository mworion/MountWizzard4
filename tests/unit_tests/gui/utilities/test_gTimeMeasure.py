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

# external packages

# local import
from gui.utilities.gTimeMeasure import TimeMeasure


@pytest.fixture(autouse=True, scope='module')
def module(qapp):
    yield


def test_TimeMeasure():
    TimeMeasure(orientation='left')


def test_TimeMeasure_tickStrings():
    values = [-1, 0, 1]
    TimeMeasure(orientation='left').tickStrings(values, 0, 0)
