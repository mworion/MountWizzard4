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
from unittest import mock

import pytest
from gui.extWindows.simulator.simulatorW import SimulatorWindow

# external packages
# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    func = SimulatorWindow(app=App())
    with mock.patch.object(func, "show"):
        yield func.world


def test_updatePositions_1(function):
    with mock.patch.object(
        function.app.mount,
        "calcTransformationMatricesActual",
        return_value=(0, 0, None, None, None),
    ):
        function.updatePositions()


def test_updatePositions_2(function):
    function.create()
    function.updatePositions()


def test_create_1(function):
    with mock.patch.object(function, "updatePositions"):
        function.create()
