# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion


from mw4.gui.mainWaddon.satData import SatData


def test_class_1():
    assert "satellites" in vars(SatData)
