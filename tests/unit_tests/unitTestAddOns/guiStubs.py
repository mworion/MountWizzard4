# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from PySide6.QtCore import QObject


class CheckBox:
    checked = False

    def isChecked(self):
        return self.checked

    def setChecked(self, value):
        self.checked = value


class LineEdit:
    valueFloat = 0

    def value(self):
        return self.valueFloat

    def setValue(self, value):
        self.valueFloat = value


class UIStub(QObject):
    def __init__(self):
        from tests.unit_tests.unitTestAddOns.guiStubs import LineEdit

        self.offLAT = LineEdit()


class MainW:
    def __init__(self):
        self.ui = UIStub()
        self.gameControllerRunning = False
