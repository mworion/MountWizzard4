# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
import numpy as np
import pytest
from mw4.gui.utilities.pyqtgraph.gImageBar import ImageBar
from unittest import mock


@pytest.fixture(autouse=True, scope="module")
def module(qapp):
    yield


def test_ImageBar_constructPlot():
    function = ImageBar()
    function.constructPlot()


def test_ImageBar_setColorMap():
    function = ImageBar()
    function.setImageColorMap(0)


def test_ImageBar_setImage_1():
    function = ImageBar()
    suc = function.setImage(None)
    assert not suc


def test_ImageBar_setImage_2():
    function = ImageBar()
    img = np.random.rand(100, 100)
    suc = function.setImage(img)
    assert suc


def test_ImageBar_setImage_4():
    function = ImageBar()
    img = np.zeros((100, 100))
    with mock.patch.object(function.barItem, "setLevels") as m:
        suc = function.setImage(img)
        assert suc
        m.assert_not_called()


def test_ImageBar_setImage_3():
    function = ImageBar()
    img = np.random.rand(100, 100)
    suc = function.setImage(img, False)
    assert suc


def test_ImageBar_showCrosshair():
    function = ImageBar()
    function.lx = mock.MagicMock()
    function.ly = mock.MagicMock()
    function.showCrosshair(True)


def test_ImageBar_showCrosshair_noLines():
    function = ImageBar()
    function.lx = None
    function.ly = None
    function.showCrosshair(True)


def test_ImageBar_addEllipse():
    function = ImageBar()
    with mock.patch.object(function.p[0], "addItem"):
        suc = function.addEllipse(0, 0, 1, 1, 0)
        assert suc


def test_ImageBar_addValueAnnotation():
    function = ImageBar()
    with mock.patch.object(function.p[0], "addItem"):
        function.addValueAnnotation(0, 0, 10)
