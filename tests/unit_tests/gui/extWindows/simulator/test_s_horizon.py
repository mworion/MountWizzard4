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
import unittest.mock as mock
from mw4.gui.extWindows.simulator.simulatorW import SimulatorWindow
from PySide6.Qt3DCore import Qt3DCore
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    func = SimulatorWindow(app=App())
    with mock.patch.object(func, "show"):
        yield func.horizon


def test_showEnable_1(function):
    function.parent.entityModel["horizonRoot"] = {"entity": Qt3DCore.QEntity()}
    function.showEnable()


def test_clear_1(function):
    function.parent.entityModel = {}
    function.clear()


def test_clear_2(function):
    function.parent.entityModel["horizonRoot"] = {"entity": Qt3DCore.QEntity()}
    function.clear()


def test_createWall_1(function):
    val = function.createWall(Qt3DCore.QEntity(), 0, 0)
    assert isinstance(val, Qt3DCore.QEntity)


def test_create_1(function):
    function.parent.entityModel["ref_fusion"] = {"entity": Qt3DCore.QEntity()}
    function.app.data.horizonP = None
    function.create()


def test_create_2(function):
    function.parent.entityModel["ref_fusion"] = {"entity": Qt3DCore.QEntity()}
    function.app.data.horizonP = [(0, 0), (10, 10)]
    with mock.patch.object(function, "clear"):
        with mock.patch.object(function, "createWall"):
            with mock.patch.object(function, "showEnable"):
                function.create()
