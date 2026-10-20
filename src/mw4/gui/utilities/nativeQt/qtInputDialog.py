# MountWizzard4 - Python-based tool for interacting with 10micron mounts
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2019-2026 mworion
from dataclasses import dataclass, field
from mw4.gui.utilities.qtMain import MWidget
from PySide6.QtCore import QEventLoop, Qt
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)
from typing import Any


@dataclass(kw_only=True)
class InputDialogOptions:
    title: str = "Input"
    label: str = "Enter value:"
    actualValue: str | float | None = None
    inputMode: str = "text"
    minValue: float = 0
    maxValue: float = 2147483647
    step: int = 1
    decimals: int = 1
    items: list[str] = field(default_factory=list)
    currentIndex: int = 0


class MWInputDialog(MWidget):
    Accepted = 1
    Rejected = 0

    def __init__(self, options: InputDialogOptions, parent: QWidget | None = None) -> None:
        super().__init__()
        self.options = options
        self.inputMode = options.inputMode
        self.items = options.items
        self.resultCode: int = self.Rejected
        self.inputValue: str = ""
        self.eventLoop = QEventLoop()
        self.setWindowTitle(options.title)
        self.setFixedSize(350, 150)
        self.inputWidget: Any = self.createInputWidget(options)
        self.inputEdit = self.inputWidget
        self.createLayout(options.label)
        self.centerOnParent(parent)

    @staticmethod
    def parseValue(inputMode: str, actualValue: str | float | None) -> int | float | str:
        if inputMode == "int":
            try:
                return int(float(str(actualValue))) if actualValue is not None else 0
            except (ValueError, TypeError):
                return 0
        if inputMode == "double":
            try:
                return float(actualValue) if actualValue is not None else 0.0
            except (ValueError, TypeError):
                return 0.0
        return str(actualValue) if actualValue else ""

    def createInputWidget(self, options: InputDialogOptions) -> Any:
        value = self.parseValue(options.inputMode, options.actualValue)
        if options.inputMode == "int":
            widget: Any = QSpinBox()
            widget.setMinimum(int(options.minValue))
            widget.setMaximum(int(options.maxValue))
            widget.setSingleStep(options.step)
            widget.setValue(int(value))
            widget.returnPressed.connect(self.onAccept)
        elif options.inputMode == "double":
            widget = QDoubleSpinBox()
            widget.setMinimum(float(options.minValue))
            widget.setMaximum(float(options.maxValue))
            widget.setDecimals(options.decimals)
            widget.setSingleStep(1.0)
            widget.setValue(float(value))
            widget.returnPressed.connect(self.onAccept)
        elif options.inputMode == "item":
            widget = QComboBox()
            widget.addItems(options.items)
            widget.setCurrentIndex(options.currentIndex)
        else:
            widget = QLineEdit()
            widget.setText(str(value))
            widget.returnPressed.connect(self.onAccept)
        widget.setMinimumHeight(25)
        return widget

    def createButtons(self) -> QHBoxLayout:
        buttonRow = QHBoxLayout()
        buttonRow.addStretch(1)
        self.btnOk = QPushButton("OK")
        self.btnOk.setMinimumSize(80, 25)
        self.btnOk.clicked.connect(self.onAccept)
        self.btnOk.setDefault(True)
        self.btnCancel = QPushButton("Cancel")
        self.btnCancel.setMinimumSize(80, 25)
        self.btnCancel.clicked.connect(self.onReject)
        buttonRow.addWidget(self.btnOk)
        buttonRow.addWidget(self.btnCancel)
        return buttonRow

    def createLayout(self, label: str) -> None:
        labelWidget = QLabel(label)
        labelWidget.setAlignment(Qt.AlignmentFlag.AlignLeft)
        contentLayout = QVBoxLayout(self.ws)
        contentLayout.setContentsMargins(12, 12, 12, 12)
        contentLayout.addWidget(labelWidget)
        contentLayout.addWidget(self.inputWidget, 1)
        contentLayout.addLayout(self.createButtons())

    def centerOnParent(self, parent: QWidget | None) -> None:
        if parent is None:
            return
        self.move(
            parent.x() + max(0, (parent.width() - self.width()) // 2),
            parent.y() + max(0, (parent.height() - self.height()) // 2),
        )

    def onAccept(self) -> None:
        if self.inputMode in ("int", "double"):
            text = str(self.inputWidget.value())
        elif self.inputMode == "item":
            text = self.inputWidget.currentText()
        else:  # text mode
            text = self.inputWidget.text()

        if not self.validateInput(text):
            return
        self.inputValue = text
        self.resultCode = self.Accepted
        self.finishLoop()
        self.close()

    def validateInput(self, text: str) -> bool:
        if not text:
            return False
        if self.inputMode == "int" or self.inputMode == "double":
            return True
        return True

    def onReject(self) -> None:
        self.inputValue = ""
        self.resultCode = self.Rejected
        self.finishLoop()
        self.close()

    def finishLoop(self) -> None:
        if self.eventLoop.isRunning():
            self.eventLoop.quit()

    def closeEvent(self, event: QCloseEvent) -> None:
        if self.eventLoop.isRunning():
            self.inputValue = ""
            self.resultCode = self.Rejected
            self.eventLoop.quit()
        super().closeEvent(event)

    def exec(self) -> int:
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.show()
        self.titleBar.normButton.setVisible(False)
        self.titleBar.maxButton.setVisible(False)
        self.titleBar.minButton.setVisible(False)
        self.inputWidget.setFocus()
        self.eventLoop.exec()
        return self.resultCode

    def getValue(self) -> str:
        return self.inputValue

    def wasAccepted(self) -> bool:
        return self.resultCode == self.Accepted

    @classmethod
    def getText(
        cls,
        parent: QWidget | None,
        title: str,
        label: str,
        actualValue: str = "",
    ) -> tuple[str, bool]:
        dlg = cls(
            InputDialogOptions(
                title=title,
                label=label,
                actualValue=actualValue,
                inputMode="text",
            ),
            parent=parent,
        )
        dlg.exec()
        return dlg.getValue(), dlg.wasAccepted()

    @classmethod
    def getInt(
        cls,
        parent: QWidget | None,
        title: str,
        label: str,
        actualValue: int = 0,
        minValue: int = -2147483647,
        maxValue: int = 2147483647,
        step: int = 1,
    ) -> tuple[int, bool]:
        dlg = cls(
            InputDialogOptions(
                title=title,
                label=label,
                actualValue=actualValue,
                inputMode="int",
                minValue=minValue,
                maxValue=maxValue,
                step=step,
            ),
            parent=parent,
        )
        dlg.exec()
        if dlg.wasAccepted():
            try:
                return int(dlg.getValue()), True
            except ValueError:
                return 0, False
        return 0, False

    @classmethod
    def getDouble(
        cls,
        parent: QWidget | None,
        title: str,
        label: str,
        actualValue: float = 0.0,
        minValue: float = -2147483647.0,
        maxValue: float = 2147483647.0,
        decimals: int = 1,
    ) -> tuple[float, bool]:
        dlg = cls(
            InputDialogOptions(
                title=title,
                label=label,
                actualValue=actualValue,
                inputMode="double",
                minValue=minValue,
                maxValue=maxValue,
                decimals=decimals,
            ),
            parent=parent,
        )
        dlg.exec()
        if dlg.wasAccepted():
            try:
                return float(dlg.getValue()), True
            except ValueError:
                return 0.0, False
        return 0.0, False

    @classmethod
    def getItem(
        cls,
        parent: QWidget | None,
        title: str,
        label: str,
        items: list[str],
        currentIndex: int = 0,
    ) -> tuple[str, bool]:
        dlg = cls(
            InputDialogOptions(
                title=title,
                label=label,
                inputMode="item",
                items=items,
                currentIndex=currentIndex,
            ),
            parent=parent,
        )
        dlg.exec()
        return dlg.getValue(), dlg.wasAccepted()
