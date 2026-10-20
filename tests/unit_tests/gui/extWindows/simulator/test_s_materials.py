# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion

import pytest
from mw4.gui.extWindows.simulator.materials import Materials
from PySide6.QtGui import QColor


@pytest.fixture(autouse=True, scope="module")
def module_setup_teardown():
    global app
    app = Materials()
    yield


def test_1():
    assert app.white


def test_createMetalRough():
    mat = app.createMetalRough(QColor(10, 20, 30), 0.25, 0.75)
    assert mat.baseColor() == QColor(10, 20, 30)
    assert mat.metalness() == 0.25
    assert mat.roughness() == 0.75


def test_createDiffuseSpecular_withoutShininess():
    mat = app.createDiffuseSpecular((1, 2, 3), (4, 5, 6), (7, 8, 9, 10))
    assert mat.ambient() == QColor(1, 2, 3)
    assert mat.specular() == QColor(4, 5, 6)
    assert mat.diffuse() == QColor(7, 8, 9, 10)
    assert not mat.isAlphaBlendingEnabled()


def test_createDiffuseSpecular_withShininessAndBlending():
    mat = app.createDiffuseSpecular((1, 2, 3), (4, 5, 6), (7, 8, 9), True, 99)
    assert mat.isAlphaBlendingEnabled()
    assert mat.shininess() == 99


def test_createPhongAlpha_defaultsToAmbient():
    mat = app.createPhongAlpha(app.M_RED)
    assert mat.ambient() == mat.diffuse() == mat.specular()
    assert mat.alpha() == 1
    assert mat.shininess() == 64


def test_createPhongAlpha_withOwnColors():
    mat = app.createPhongAlpha(app.M_RED, app.M_GREEN, app.M_YELLOW, 0.5, 10)
    assert mat.diffuse().green() == 192
    assert mat.specular().red() == app.M_YELLOW[0]
    assert mat.alpha() == pytest.approx(0.5, abs=1e-3)
    assert mat.shininess() == 10


def test_createPhong_withShininess():
    mat = app.createPhong(app.M_RED, 33)
    assert mat.ambient() == QColor(app.rgb2hex(app.M_RED))
    assert mat.shininess() == 33


def test_createPhong_withoutShininess():
    mat = app.createPhong(app.M_RED)
    assert mat.specular() == QColor(app.rgb2hex(app.M_RED))
