# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import pytest
from mw4.gui.extWindows.simulator.simulatorW import SimulatorWindow
from PySide6.Qt3DCore import Qt3DCore
from PySide6.Qt3DRender import Qt3DRender
from PySide6.QtWidgets import QApplication
from tests.unit_tests.unitTestAddOns.baseTestApp import App
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def function(qapp):
    func = SimulatorWindow(app=App(), title="Simulator")
    with mock.patch.object(func, "show"):
        yield func.light
        QApplication.processEvents()


def test_setIntensity_1(function):
    function.parent.entityModel["main"] = {"entity": Qt3DCore.QEntity()}
    a = Qt3DCore.QEntity(function.parent.entityModel["main"]["entity"])
    light = Qt3DRender.QPointLight()
    a.addComponent(light)
    function.parent.entityModel["main"]["light"] = light
    with mock.patch.object(Qt3DRender.QPointLight, "setIntensity"):
        function.setIntensity()


def test_create_1(function):
    function.create()
