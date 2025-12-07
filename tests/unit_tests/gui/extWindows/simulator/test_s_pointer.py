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

from unittest import mock

import pytest


from PySide6.Qt3DCore import Qt3DCore

from mw4.gui.extWindows.simulator.simulatorW import SimulatorWindow


from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    func = SimulatorWindow(app=App())
    with mock.patch.object(func, "show"):
        yield func.pointer


def test_showEnable_1(function):
    function.parent.entityModel["pointer"] = {"entity": Qt3DCore.QEntity()}
    function.showEnable()


def test_updatePositions_1(function):
    function.app.deviceStat["mount"] = False
    function.updatePositions()


def test_updatePositions_2(function):
    function.app.deviceStat["mount"] = True
    with mock.patch.object(
        function.app.mount,
        "calcTransformationMatricesActual",
        return_value=(0, 0, None, None, None),
    ):
        function.updatePositions()


def test_updatePositions_3(function):
    function.app.deviceStat["mount"] = True
    with mock.patch.object(
        function.app.mount,
        "calcTransformationMatricesActual",
        return_value=(0, 0, [1, 1, 1], None, None),
    ):
        function.updatePositions()


def test_create_1(function):
    with mock.patch.object(function, "updatePositions"):
        with mock.patch.object(function, "showEnable"):
            function.create()
