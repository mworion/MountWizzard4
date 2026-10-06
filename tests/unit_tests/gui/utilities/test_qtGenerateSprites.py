# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from mw4.gui.utilities.qtGenerateSprites import makePointer, makeSat
from PySide6.QtGui import QPainterPath


def test_makePointer():
    val = makePointer()
    assert isinstance(val, QPainterPath)


def test_makeSat():
    val = makeSat()
    assert isinstance(val, QPainterPath)
