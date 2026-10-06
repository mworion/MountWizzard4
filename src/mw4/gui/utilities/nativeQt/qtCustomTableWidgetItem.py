# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QTableWidgetItem


class QCustomTableWidgetItem(QTableWidgetItem):
    def __init__(self, value: str) -> None:
        super().__init__(value)

    def __lt__(self, other: QTableWidgetItem) -> bool:
        selfData = self.data(Qt.ItemDataRole.EditRole)
        selfDataValue = 99 if selfData == "" else float(selfData)
        otherData = other.data(Qt.ItemDataRole.EditRole)
        otherDataValue = 99 if otherData == "" else float(otherData)
        return selfDataValue < otherDataValue
