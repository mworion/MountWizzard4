# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import pytest
from mw4.gui.extWindows.simulator.simulatorW import SimulatorWindow
from PySide6.Qt3DCore import Qt3DCore
from PySide6.Qt3DExtras import Qt3DExtras
from PySide6.QtWidgets import QApplication
from skyfield.api import Angle
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def function(qapp, makeApp):
    func = SimulatorWindow(app=makeApp(), title="Simulator")
    with mock.patch.object(func, "show"):
        yield func.telescope
        QApplication.processEvents()


def test_updatePositions_1(function):
    function.app.dReg.d["mount"].stat = False
    function.updatePositions()


def test_updatePositions_2(function):
    function.parent.entityModel["mountBase"] = {"entity": Qt3DCore.QEntity()}
    t = Qt3DCore.QTransform()
    function.parent.entityModel["mountBase"]["trans"] = t
    function.parent.entityModel["mountBase"]["entity"].addComponent(t)

    function.parent.entityModel["lat"] = {"entity": Qt3DCore.QEntity()}
    t = Qt3DCore.QTransform()
    function.parent.entityModel["lat"]["trans"] = t
    function.parent.entityModel["lat"]["entity"].addComponent(t)

    function.parent.entityModel["gem"] = {"entity": Qt3DCore.QEntity()}
    m = Qt3DExtras.QCuboidMesh()
    t = Qt3DCore.QTransform()
    function.parent.entityModel["gem"]["mesh"] = m
    function.parent.entityModel["gem"]["trans"] = t
    function.parent.entityModel["gem"]["entity"].addComponent(m)
    function.parent.entityModel["gem"]["entity"].addComponent(t)

    function.parent.entityModel["gemCorr"] = {"entity": Qt3DCore.QEntity()}
    t = Qt3DCore.QTransform()
    function.parent.entityModel["gemCorr"]["trans"] = t
    function.parent.entityModel["gemCorr"]["entity"].addComponent(t)

    function.parent.entityModel["otaRing"] = {"entity": Qt3DCore.QEntity()}
    t = Qt3DCore.QTransform()
    function.parent.entityModel["otaRing"]["trans"] = t
    function.parent.entityModel["otaRing"]["entity"].addComponent(t)

    function.parent.entityModel["otaTube"] = {"entity": Qt3DCore.QEntity()}
    t = Qt3DCore.QTransform()
    function.parent.entityModel["otaTube"]["trans"] = t
    function.parent.entityModel["otaTube"]["entity"].addComponent(t)

    function.parent.entityModel["otaImagetrain"] = {"entity": Qt3DCore.QEntity()}
    t = Qt3DCore.QTransform()
    function.parent.entityModel["otaImagetrain"]["trans"] = t
    function.parent.entityModel["otaImagetrain"]["entity"].addComponent(t)

    function.app.dReg.d["mount"].stat = True
    function.updatePositions()


def test_updateRotation_1(function):
    function.app.mount.obsSite.angularPosRA = None
    function.app.mount.obsSite.angularPosDEC = None
    function.updateRotation()


def test_updateRotation_2(function):
    function.app.mount.obsSite.angularPosRA = Angle(degrees=10)
    function.app.mount.obsSite.angularPosDEC = Angle(degrees=10)
    function.parent.entityModel["ra"] = {"entity": Qt3DCore.QEntity()}
    t = Qt3DCore.QTransform()
    function.parent.entityModel["ra"]["entity"].addComponent(t)
    function.parent.entityModel["ra"]["trans"] = t

    function.parent.entityModel["dec"] = {"entity": Qt3DCore.QEntity()}
    t = Qt3DCore.QTransform()
    function.parent.entityModel["dec"]["entity"].addComponent(t)
    function.parent.entityModel["dec"]["trans"] = t
    function.updateRotation()


def test_create_1(function):
    function.app.mount.obsSite.location.latitude = Angle(degrees=10)
    with (
        mock.patch.object(function, "updatePositions"),
        mock.patch.object(function, "updateRotation"),
    ):
        function.create()


def test_create_2(function):
    function.app.mount.obsSite.location.latitude = Angle(degrees=-10)
    with (
        mock.patch.object(function, "updatePositions"),
        mock.patch.object(function, "updateRotation"),
    ):
        function.create()


def test_updatePositions_3(function):
    function.app.dReg.d["mount"].stat = True
    with mock.patch.object(function.parent, "entityModel", {}):
        function.updatePositions()


def test_updateRotation_3(function):
    function.app.mount.obsSite.angularPosRA = Angle(degrees=10)
    function.app.mount.obsSite.angularPosDEC = Angle(degrees=10)
    with mock.patch.object(function.parent, "entityModel", {}):
        function.updateRotation()


def test_createMountBase(function):
    model = function.createMountBase()
    assert list(model) == ["mountRoot", "mountBase", "mountKnobs", "lat", "mountRa", "ra"]


def test_createDeclinationAxis(function):
    model = function.createDeclinationAxis()
    assert list(model) == [
        "mountDec",
        "mountDecKnobs",
        "mountDecWeights",
        "dec",
        "mountHead",
        "mountHeadKnobs",
    ]


def test_createOta(function):
    model = function.createOta()
    assert next(iter(model)) == "gem"
    assert list(model)[-1] == "otaFocusTop"


def test_create_assemblesAllParts(function):
    function.app.mount.obsSite.location.latitude = Angle(degrees=10)
    with (
        mock.patch.object(function, "updatePositions"),
        mock.patch.object(function, "updateRotation"),
        mock.patch("mw4.gui.extWindows.simulator.telescope.linkModel") as linkModel,
    ):
        function.create()
    model = linkModel.call_args[0][0]
    assert len(model) == 21
    assert "rot" not in model["mountBase"] or model["mountBase"]["rot"] != [0, 0, 180]


def test_create_southernHemisphereRotatesBase(function):
    function.app.mount.obsSite.location.latitude = Angle(degrees=-10)
    with (
        mock.patch.object(function, "updatePositions"),
        mock.patch.object(function, "updateRotation"),
        mock.patch("mw4.gui.extWindows.simulator.telescope.linkModel") as linkModel,
    ):
        function.create()
    assert linkModel.call_args[0][0]["mountBase"]["rot"] == [0, 0, 180]
