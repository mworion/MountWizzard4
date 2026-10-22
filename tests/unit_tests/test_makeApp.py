# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from tests.unit_tests.unitTestAddOns.baseTestApp import Camera


def test_makeApp_default(makeApp):
    app = makeApp()
    assert app.statusOperationRunning == 0


def test_makeApp_overrides(makeApp):
    camera = Camera()
    app = makeApp(statusOperationRunning=3, camera=camera, mount__marker=7)
    assert app.statusOperationRunning == 3
    assert app.camera is camera
    assert app.mount.marker == 7
