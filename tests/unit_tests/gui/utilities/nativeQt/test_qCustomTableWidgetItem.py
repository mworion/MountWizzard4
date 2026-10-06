# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion


from mw4.gui.utilities.nativeQt.qtCustomTableWidgetItem import QCustomTableWidgetItem


def test_QCustomTableWidgetItem_1():
    i1 = QCustomTableWidgetItem("")
    i2 = QCustomTableWidgetItem("")
    assert not (i1 < i2)


def test_QCustomTableWidgetItem_2():
    i1 = QCustomTableWidgetItem("-2.0")
    i2 = QCustomTableWidgetItem("")
    assert i1 < i2


def test_QCustomTableWidgetItem_3():
    i1 = QCustomTableWidgetItem("-2.0")
    i2 = QCustomTableWidgetItem("5")
    assert i1 < i2
