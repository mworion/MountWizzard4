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
from unittest import mock

import pytest

# external packages
from PySide6.Qt3DCore import Qt3DCore
from PySide6.Qt3DRender import Qt3DRender

from mw4.gui.extWindows.simulator.simulatorW import SimulatorWindow

# local import
from tests.unit_tests.unitTestAddOns.baseTestApp import App


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    func = SimulatorWindow(app=App())
    with mock.patch.object(func, "show"):
        yield func.light


def test_setIntensity_1(function):
    function.parent.entityModel["main"] = {"entity": Qt3DCore.QEntity()}

    a = Qt3DCore.QEntity(function.parent.entityModel["main"]["entity"])
    l = Qt3DRender.QPointLight()
    a.addComponent(l)
    function.parent.entityModel["main"]["light"] = l
    function.setIntensity()


def test_create_1(function):
    function.create()
