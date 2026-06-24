############################################################
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10_micron mounts
# GUI with PySide
#
# written in python3, (c) 2019-2026 by mworion
# License APL2.0
#
###########################################################
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


class MWInputDialog(MWidget):
    """
    Lightweight, themed input dialog built on top of the frameless
    :class:`MWidget`. Provides text input functionality with a consistent
    look and feel matching MW4's design.

    The dialog is not a :class:`QDialog` – :meth:`exec` runs a local
    :class:`QEventLoop` so the call site can stay synchronous, mirroring
    Qt's own ``QInputDialog.exec()`` semantics.
    """

    Accepted = 1
    Rejected = 0

    def __init__(
        self,
        parent: QWidget | None = None,
        title: str = "Input",
        label: str = "Enter value:",
        actualValue: str | int | float | None = None,
        inputMode: str = "text",
        minValue: int | float = 0,
        maxValue: int | float = 2147483647,
        step: int = 1,
        decimals: int = 1,
        items: list[str] | None = None,
        currentIndex: int = 0,
    ) -> None:
        super().__init__()
        self.inputMode = inputMode
        self.resultCode: int = self.Rejected
        self.inputValue: str = ""
        self.eventLoop = QEventLoop()
        self.minValue = minValue
        self.maxValue = maxValue
        self.step = step
        self.decimals = decimals
        self.items = items if items is not None else []
        self.currentIndex = currentIndex
        self.setWindowTitle(title)
        self.setFixedSize(350, 150)

        labelWidget = QLabel(label)
        labelWidget.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # Parse actualValue based on input mode
        parsedValue: int | float | str = ""
        if self.inputMode == "int":
            try:
                parsedValue = int(float(str(actualValue))) if actualValue is not None else 0
            except (ValueError, TypeError):
                parsedValue = 0
        elif self.inputMode == "double":
            try:
                parsedValue = float(actualValue) if actualValue is not None else 0.0
            except (ValueError, TypeError):
                parsedValue = 0.0
        elif self.inputMode == "item":
            parsedValue = str(actualValue) if actualValue else ""
        else:  # text mode
            parsedValue = str(actualValue) if actualValue else ""

        # Create appropriate input widget based on mode
        if self.inputMode == "int":
            self.inputWidget = QSpinBox()
            self.inputWidget.setMinimum(int(self.minValue))
            self.inputWidget.setMaximum(int(self.maxValue))
            self.inputWidget.setSingleStep(self.step)
            self.inputWidget.setValue(int(parsedValue))
            self.inputWidget.returnPressed.connect(self.onAccept)
        elif self.inputMode == "double":
            self.inputWidget = QDoubleSpinBox()
            self.inputWidget.setMinimum(float(self.minValue))
            self.inputWidget.setMaximum(float(self.maxValue))
            self.inputWidget.setDecimals(self.decimals)
            self.inputWidget.setSingleStep(1.0)
            self.inputWidget.setValue(float(parsedValue))
            self.inputWidget.returnPressed.connect(self.onAccept)
        elif self.inputMode == "item":
            self.inputWidget = QComboBox()
            self.inputWidget.addItems(self.items)
            self.inputWidget.setCurrentIndex(self.currentIndex)
        else:  # text mode
            self.inputWidget = QLineEdit()
            self.inputWidget.setText(str(parsedValue))
            self.inputWidget.returnPressed.connect(self.onAccept)

        # Set minimum height for input widget
        self.inputWidget.setMinimumHeight(25)

        # Keep reference for backward compatibility
        self.inputEdit = self.inputWidget

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

        contentLayout = QVBoxLayout(self.ws)
        contentLayout.setContentsMargins(12, 12, 12, 12)
        contentLayout.addWidget(labelWidget)
        contentLayout.addWidget(self.inputWidget, 1)
        contentLayout.addLayout(buttonRow)

        if parent is not None:
            self.move(
                parent.x() + max(0, (parent.width() - self.width()) // 2),
                parent.y() + max(0, (parent.height() - self.height()) // 2),
            )

    def onAccept(self) -> None:
        """Handle OK button click."""
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
        """Validate input based on input mode and constraints."""
        if not text:
            return False
        if self.inputMode == "int":
            # QSpinBox automatically enforces bounds
            return True
        elif self.inputMode == "double":
            # QDoubleSpinBox automatically enforces bounds
            return True
        return True

    def onReject(self) -> None:
        """Handle Cancel button click."""
        self.inputValue = ""
        self.resultCode = self.Rejected
        self.finishLoop()
        self.close()

    def finishLoop(self) -> None:
        """Quit the event loop if running."""
        if self.eventLoop.isRunning():
            self.eventLoop.quit()

    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle window close event."""
        if self.eventLoop.isRunning():
            self.inputValue = ""
            self.resultCode = self.Rejected
            self.eventLoop.quit()
        super().closeEvent(event)

    def exec(self) -> int:
        """Execute dialog modally."""
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.show()
        self.setMinimumSize(350, 150)
        self.setMaximumSize(350, 150)
        self.titleBar.normButton.setVisible(False)
        self.titleBar.maxButton.setVisible(False)
        self.titleBar.minButton.setVisible(False)
        self.titleBar.windowFixed = True
        self.inputWidget.setFocus()
        self.eventLoop.exec()
        return self.resultCode

    def getValue(self) -> str:
        """Get the input value."""
        return self.inputValue

    def wasAccepted(self) -> bool:
        """Check if dialog was accepted."""
        return self.resultCode == self.Accepted

    @classmethod
    def getText(
        cls,
        parent: QWidget | None,
        title: str,
        label: str,
        actualValue: str = "",
        echoMode: QLineEdit.EchoMode = QLineEdit.EchoMode.Normal,
    ) -> tuple[str, bool]:
        dlg = cls(
            parent=parent,
            title=title,
            label=label,
            actualValue=actualValue,
            inputMode="text",
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
            parent=parent,
            title=title,
            label=label,
            actualValue=actualValue,
            inputMode="int",
            minValue=minValue,
            maxValue=maxValue,
            step=step,
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
            parent=parent,
            title=title,
            label=label,
            actualValue=actualValue,
            inputMode="double",
            minValue=minValue,
            maxValue=maxValue,
            decimals=decimals,
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
            parent=parent,
            title=title,
            label=label,
            inputMode="item",
            items=items,
            currentIndex=currentIndex,
        )
        dlg.exec()
        return dlg.getValue(), dlg.wasAccepted()
